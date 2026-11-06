"""Reliable job queue on Redis.

Layout in Redis:
    queue:pending              list of job ids waiting to run
    queue:processing:<worker>  list of job ids a worker has claimed (one list per worker)
    queue:dead                 list of job ids that failed too many times (dead-letter queue)
    job:<id>                   hash with the job's fields, status, attempts and result
    worker:<id>:heartbeat      key with a short TTL; it disappears if the worker stops refreshing it
    workers                    set of registered worker ids
    stats                      hash of counters (submitted, completed, retried, requeued, dead)

Guarantees:
    - A job is claimed by exactly one worker at a time (BLMOVE is atomic).
    - A job is never lost: it is always in exactly one of pending / some processing list / dead,
      or it is completed.
    - If a worker dies, its jobs go back to pending once its heartbeat expires (reap()).
    - Execution is at-least-once (a slow worker that was presumed dead may finish a job that was
      also re-run elsewhere), but a result is recorded at most once: complete() only succeeds for
      the worker that still holds the job in its processing list.
"""
import json
import os
import time
import uuid

import redis

PENDING = "queue:pending"
DEAD = "queue:dead"
WORKERS = "workers"
STATS = "stats"


def processing_key(worker_id):
    return f"queue:processing:{worker_id}"


def heartbeat_key(worker_id):
    return f"worker:{worker_id}:heartbeat"


def job_key(job_id):
    return f"job:{job_id}"


# Record a result only if this worker still owns the job.
# KEYS: processing list, job hash, stats   ARGV: job id, completed_at, field/value pairs...
COMPLETE_LUA = """
if redis.call('LREM', KEYS[1], 1, ARGV[1]) == 0 then
  return 0
end
redis.call('HSET', KEYS[2], 'status', 'completed', 'completed_at', ARGV[2])
for i = 3, #ARGV, 2 do
  redis.call('HSET', KEYS[2], ARGV[i], ARGV[i + 1])
end
redis.call('HINCRBY', KEYS[3], 'completed', 1)
return 1
"""

# Retry a failed job, or move it to the dead-letter queue after max attempts.
# KEYS: processing list, job hash, pending, dead, stats   ARGV: job id, max attempts, error, now
FAIL_LUA = """
if redis.call('LREM', KEYS[1], 1, ARGV[1]) == 0 then
  return 0
end
local attempts = tonumber(redis.call('HGET', KEYS[2], 'attempts') or '0')
if attempts >= tonumber(ARGV[2]) then
  redis.call('HSET', KEYS[2], 'status', 'dead', 'error', ARGV[3], 'completed_at', ARGV[4])
  redis.call('RPUSH', KEYS[4], ARGV[1])
  redis.call('HINCRBY', KEYS[5], 'dead', 1)
  return 2
end
redis.call('HSET', KEYS[2], 'status', 'pending', 'error', ARGV[3])
redis.call('RPUSH', KEYS[3], ARGV[1])
redis.call('HINCRBY', KEYS[5], 'retried', 1)
return 1
"""

# Return every job held by a dead worker to the front of the queue (or dead-letter it).
# Does nothing if the worker's heartbeat is still alive.
# KEYS: processing list, pending, dead, stats, workers, heartbeat   ARGV: worker id, max attempts
# Note: builds job:<id> key names inside the script, which is fine on a single Redis node.
REAP_LUA = """
if redis.call('EXISTS', KEYS[6]) == 1 then
  return -1
end
local moved = 0
while true do
  local id = redis.call('LPOP', KEYS[1])
  if not id then break end
  local jk = 'job:' .. id
  local attempts = tonumber(redis.call('HGET', jk, 'attempts') or '0')
  if attempts >= tonumber(ARGV[2]) then
    redis.call('HSET', jk, 'status', 'dead', 'error', 'worker lost')
    redis.call('RPUSH', KEYS[3], id)
    redis.call('HINCRBY', KEYS[4], 'dead', 1)
  else
    redis.call('HSET', jk, 'status', 'pending')
    redis.call('LPUSH', KEYS[2], id)
    redis.call('HINCRBY', KEYS[4], 'requeued', 1)
  end
  moved = moved + 1
end
redis.call('SREM', KEYS[5], ARGV[1])
return moved
"""


def connect():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=0,
        decode_responses=True,
    )


class JobQueue:
    def __init__(self, r=None, max_attempts=3, heartbeat_ttl=10):
        self.r = r or connect()
        self.max_attempts = max_attempts
        self.heartbeat_ttl = heartbeat_ttl
        self._complete = self.r.register_script(COMPLETE_LUA)
        self._fail = self.r.register_script(FAIL_LUA)
        self._reap = self.r.register_script(REAP_LUA)

    # ---- producers -------------------------------------------------------

    def submit_job(self, job_type, description, parameters=None, kind="train"):
        job = {
            "id": str(uuid.uuid4()),
            "kind": kind,
            "type": job_type,
            "description": description,
            "parameters": json.dumps(parameters) if parameters is not None else "",
            "status": "pending",
            "attempts": 0,
            "created_at": time.time(),
        }
        pipe = self.r.pipeline(transaction=True)
        pipe.hset(job_key(job["id"]), mapping=job)
        pipe.rpush(PENDING, job["id"])
        pipe.hincrby(STATS, "submitted", 1)
        pipe.execute()
        return job

    # ---- workers ---------------------------------------------------------

    def register_worker(self, worker_id):
        self.r.sadd(WORKERS, worker_id)
        self.heartbeat(worker_id)

    def heartbeat(self, worker_id):
        self.r.set(heartbeat_key(worker_id), time.time(), ex=self.heartbeat_ttl)

    def deregister_worker(self, worker_id):
        """Graceful shutdown: drop the heartbeat so any held jobs are reaped right away."""
        self.r.delete(heartbeat_key(worker_id))
        self.reap_worker(worker_id)

    def claim(self, worker_id, timeout=1.0):
        """Atomically move the next job id from pending to this worker's processing list."""
        job_id = self.r.blmove(PENDING, processing_key(worker_id), timeout, "LEFT", "RIGHT")
        if job_id is None:
            return None
        pipe = self.r.pipeline(transaction=True)
        pipe.hset(job_key(job_id), mapping={"status": "running", "worker": worker_id, "started_at": time.time()})
        pipe.hincrby(job_key(job_id), "attempts", 1)
        pipe.execute()
        return self.get_job(job_id)

    def complete(self, worker_id, job_id, result):
        """Record the result. Returns False if this worker no longer owns the job."""
        flat = []
        for k, v in (result or {}).items():
            flat += [k, json.dumps(v) if isinstance(v, (dict, list)) else v]
        ok = self._complete(
            keys=[processing_key(worker_id), job_key(job_id), STATS],
            args=[job_id, time.time(), *flat],
        )
        return ok == 1

    def fail(self, worker_id, job_id, error):
        """Returns 'retried', 'dead', or None if this worker no longer owns the job."""
        code = self._fail(
            keys=[processing_key(worker_id), job_key(job_id), PENDING, DEAD, STATS],
            args=[job_id, self.max_attempts, str(error)[:500], time.time()],
        )
        return {1: "retried", 2: "dead"}.get(code)

    # ---- recovery --------------------------------------------------------

    def reap_worker(self, worker_id):
        return self._reap(
            keys=[processing_key(worker_id), PENDING, DEAD, STATS, WORKERS, heartbeat_key(worker_id)],
            args=[worker_id, self.max_attempts],
        )

    def reap(self):
        """Requeue jobs from every worker whose heartbeat has expired. Safe to call from anywhere."""
        moved = 0
        for worker_id in self.r.smembers(WORKERS):
            n = self.reap_worker(worker_id)
            if n > 0:
                moved += n
        return moved

    # ---- reads -----------------------------------------------------------

    def get_job(self, job_id):
        job = self.r.hgetall(job_key(job_id))
        if not job:
            return None
        job["id"] = job_id
        job["parameters"] = json.loads(job["parameters"]) if job.get("parameters") else None
        return job

    def stats(self):
        s = {k: int(v) for k, v in self.r.hgetall(STATS).items()}
        s["pending"] = self.r.llen(PENDING)
        s["dead_letter"] = self.r.llen(DEAD)
        s["workers"] = self.r.scard(WORKERS)
        return s
