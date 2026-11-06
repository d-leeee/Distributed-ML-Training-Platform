# Design notes

## The bug in the first version

The original `get_job()` did this:

```python
job_data = r.lindex("jobs", 0)   # 1. look at the first job
...
r.lpop("jobs")                   # 2. remove the first job
```

These are two separate commands. Between them, another worker can run the same two commands. Two workers read the same job; then each pops one item, so one job runs twice and the job behind it is popped without anyone reading it. Under 16 concurrent workers this double-claimed 994 of 2,000 jobs and silently dropped 989 (`benchmarks/run_benchmark.py`, "Original queue under contention").

The first version also had no recovery: if a worker crashed after popping a job, that job was gone. And failures were counted as completions.

## Claiming: BLMOVE into a per-worker list

`BLMOVE queue:pending queue:processing:<worker> LEFT RIGHT` takes the first job and puts it in the worker's own processing list as **one atomic command**. Redis runs commands one at a time, so two workers can't both get it. It also blocks for up to 1 s when the queue is empty, so idle workers don't spin.

The processing list is the key idea: a job is always in exactly one place (pending, some worker's processing list, the dead-letter queue, or done). Nothing is ever only in a worker's memory.

## Detecting dead workers: heartbeats

Each worker sets `worker:<id>:heartbeat` with a 10 s TTL and refreshes it every 2 s from a background thread. The thread matters: training can take longer than the TTL, and the main loop is busy during it.

If the process dies (crash, OOM, SIGKILL, the machine goes away), the refreshes stop and Redis deletes the key after 10 s. Any worker or the monitor can then "reap" it: move its processing list back to the front of `queue:pending`. The reap is a Lua script, so it checks the heartbeat and moves the jobs in one atomic step. It can't race with a worker that comes back at the same moment.

Why 10 s / 2 s: the TTL needs to cover a few missed refreshes (GC pause, slow network) so live workers aren't reaped by mistake, but stay short so a crash costs little time. Lower TTL means faster recovery and more false alarms.

## Acking: only the owner can record a result

Heartbeats can be wrong. A worker might freeze for 15 s, get reaped, and then wake up and finish the job, while another worker is running it too.

So completing a job is a Lua script that first does `LREM queue:processing:<worker> <job>`. If the job is no longer in this worker's list (because it was reaped), the script returns 0 and the result is dropped. Exactly one result is ever recorded per job.

This gives **at-least-once execution, exactly-once results**. A job can occasionally run twice, so jobs need to be idempotent (safe to run twice). Training is: it's deterministic (`random_state=42`) and only writes its own job hash.

True exactly-once *execution* isn't possible in a distributed system without the work itself cooperating (e.g. a transactional write tied to the claim). At-least-once plus idempotent jobs is the standard approach (SQS, Celery with `acks_late`, Sidekiq Pro).

## Failures: retries and a dead-letter queue

If a handler raises, the job goes to the back of the queue and its `attempts` count goes up. After 3 attempts it moves to `queue:dead` with the error saved. A job that always fails (bad parameters, a bug) can't block the queue forever, and nothing is silently thrown away: you can inspect and resubmit dead jobs.

Jobs reaped from a dead worker go to the *front* of the queue instead, since they already waited their turn.

## Graceful shutdown

On SIGTERM (`docker compose stop`, a deploy), the worker finishes its current job, deletes its own heartbeat, and reaps itself, so anything it still holds goes back immediately instead of after 10 s.

## Limits and what I'd change at scale

- **One Redis node is a single point of failure.** With Redis persistence (AOF) or a managed Redis with a replica, a restart doesn't lose the queue. Redis Cluster would need the Lua scripts to declare every key they touch (the reap script builds `job:<id>` names itself, which only works on one node).
- **Reaping scans every registered worker.** That's fine for tens or hundreds of workers. For thousands, I'd track heartbeats in a sorted set by timestamp and reap with one range query.
- **No priorities or per-job timeouts.** Priorities would be several pending lists checked in order. Timeouts would need the worker to run the job in a subprocess it can kill.
- **Redis Streams** (`XREADGROUP`, `XAUTOCLAIM`) have this pattern built in. I built it from lists and Lua to understand the mechanics. For production I'd consider Streams or an existing queue (Celery, RQ, SQS).

## Benchmark caveats

- The scaling benchmark uses jobs that wait 0.2 s, like a network call. Those scale almost perfectly because workers spend the time waiting, not computing. CPU-bound jobs only scale up to the number of cores (2x on the 2-core test machine).
- The crash test kills 3 of 8 workers with SIGKILL at random times and checks that every job finishes with exactly one recorded result.
