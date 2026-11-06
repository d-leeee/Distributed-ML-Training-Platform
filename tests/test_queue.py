import os
import signal
import subprocess
import sys
import threading
import time

from job_queue import DEAD, JobQueue, PENDING, processing_key
from worker import Worker

SRC = os.path.join(os.path.dirname(__file__), "..", "src")


def test_each_job_is_claimed_by_exactly_one_worker(r):
    q = JobQueue(r)
    ids = {q.submit_job("x", "y", kind="noop")["id"] for _ in range(500)}
    claimed = {}
    lock = threading.Lock()

    def claimer(wid):
        local = JobQueue(type(r)(connection_pool=r.connection_pool))
        while True:
            job = local.claim(wid, timeout=0.1)
            if job is None:
                return
            with lock:
                claimed.setdefault(job["id"], []).append(wid)

    threads = [threading.Thread(target=claimer, args=(f"w{i}",)) for i in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert set(claimed) == ids
    assert all(len(owners) == 1 for owners in claimed.values())


def test_complete_records_result_once(r):
    q = JobQueue(r)
    job = q.submit_job("x", "y", kind="noop")
    q.claim("w1")
    assert q.complete("w1", job["id"], {"accuracy": 0.9}) is True
    assert q.complete("w1", job["id"], {"accuracy": 0.1}) is False  # already acked
    stored = q.get_job(job["id"])
    assert stored["status"] == "completed"
    assert float(stored["accuracy"]) == 0.9


def test_failed_job_retries_then_goes_to_dead_letter(r):
    q = JobQueue(r, max_attempts=3)
    job = q.submit_job("x", "y", kind="boom")
    outcomes = []
    for _ in range(3):
        claimed = q.claim("w1")
        outcomes.append(q.fail("w1", claimed["id"], "boom"))
    assert outcomes == ["retried", "retried", "dead"]
    assert r.lrange(DEAD, 0, -1) == [job["id"]]
    assert r.llen(PENDING) == 0
    assert q.get_job(job["id"])["attempts"] == "3"


def test_jobs_of_a_dead_worker_are_requeued(r):
    q = JobQueue(r, heartbeat_ttl=1)
    job = q.submit_job("x", "y", kind="noop")
    q.register_worker("crashed")
    q.claim("crashed")
    assert q.reap() == 0  # heartbeat still alive: nothing happens
    time.sleep(1.2)       # heartbeat expires
    assert q.reap() == 1
    assert r.lrange(PENDING, 0, -1) == [job["id"]]
    assert r.llen(processing_key("crashed")) == 0
    # a healthy worker can now finish it
    q.claim("w2")
    assert q.complete("w2", job["id"], {}) is True


def test_presumed_dead_worker_cannot_overwrite_result(r):
    q = JobQueue(r, heartbeat_ttl=1)
    job = q.submit_job("x", "y", kind="noop")
    q.register_worker("slow")
    q.claim("slow")
    time.sleep(1.2)
    q.reap()                              # slow worker presumed dead, job requeued
    q.claim("fast")
    assert q.complete("fast", job["id"], {"by": "fast"}) is True
    assert q.complete("slow", job["id"], {"by": "slow"}) is False
    assert q.get_job(job["id"])["by"] == "fast"


def test_killed_worker_process_loses_no_jobs(r, redis_server):
    """SIGKILL a real worker mid-job; a second worker must finish every job exactly once."""
    q = JobQueue(r, heartbeat_ttl=2)
    ids = [q.submit_job("x", "y", {"duration": 0.3}, kind="simulated_io")["id"] for _ in range(10)]
    env = {**os.environ, "REDIS_PORT": str(redis_server), "PYTHONPATH": SRC}
    code = (
        "from handlers import HANDLERS; from job_queue import JobQueue; from worker import Worker;"
        "Worker(JobQueue(heartbeat_ttl=2), HANDLERS, heartbeat_interval=0.5, reap_interval=0.5).run(stop_when_empty=True)"
    )
    victim = subprocess.Popen([sys.executable, "-c", code], env=env, stdout=subprocess.DEVNULL)
    time.sleep(1.0)                       # let it get a few jobs in
    victim.send_signal(signal.SIGKILL)    # no cleanup, holds a job
    victim.wait()

    survivor = Worker(JobQueue(r, heartbeat_ttl=2),
                      {"simulated_io": lambda job: {"ok": 1}},
                      heartbeat_interval=0.5, reap_interval=0.5)
    deadline = time.time() + 15
    while time.time() < deadline and int(r.hget("stats", "completed") or 0) < len(ids):
        job = survivor.queue.claim(survivor.id, timeout=0.5)
        survivor.queue.reap()
        if job:
            survivor.process(job)

    statuses = [q.get_job(i)["status"] for i in ids]
    assert statuses == ["completed"] * len(ids)
    assert int(r.hget("stats", "completed")) == len(ids)  # each result recorded exactly once
    assert int(r.hget("stats", "requeued") or 0) >= 1      # the killed worker's job came back


def test_training_job_end_to_end(r):
    q = JobQueue(r)
    from handlers import HANDLERS
    job = q.submit_job("Random Forest", "Wine", {"n_estimators": [10, 50]})
    w = Worker(q, HANDLERS)
    w.process(q.claim(w.id))
    stored = q.get_job(job["id"])
    assert stored["status"] == "completed"
    assert float(stored["accuracy"]) > 0.8
    assert "best_params" in stored
