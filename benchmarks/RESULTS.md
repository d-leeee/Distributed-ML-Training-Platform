# Benchmark results

Machine: Linux x86_64, 2 CPU cores, Python 3.13.18

## Scaling: network-bound jobs (0.2 s each, like an API call)

| Workers | Jobs | Time (s) | Jobs/s | Speedup | p50 latency (s) | p95 latency (s) |
|---|---|---|---|---|---|---|
| 1 | 40 | 8.08 | 4.9 | 1.0x | 4.12 | 7.66 |
| 2 | 320 | 32.38 | 9.9 | 2.0x | 16.32 | 30.69 |
| 4 | 320 | 16.13 | 19.8 | 4.0x | 8.14 | 15.27 |
| 8 | 320 | 8.1 | 39.5 | 8.1x | 4.11 | 7.63 |
| 16 | 320 | 4.09 | 78.2 | 16.0x | 2.1 | 3.81 |
| 32 | 320 | 2.1 | 152.4 | 31.1x | 1.1 | 2.02 |

## Scaling: CPU-bound jobs (limited by this machine's 2 cores)

| Workers | Jobs | Time (s) | Jobs/s | Speedup |
|---|---|---|---|---|
| 1 | 24 | 14.8 | 1.6 | 1.0x |
| 2 | 24 | 7.41 | 3.2 | 2.0x |
| 4 | 24 | 7.34 | 3.3 | 2.1x |

## Queue overhead (zero-work jobs)

8 workers processed 5000 empty jobs in 1.73 s: **2882.8 jobs/s** through claim, run, and ack.

## Crash recovery

8 workers, 400 jobs, 3 workers killed with SIGKILL at [0.79, 1.04, 1.67] s.

- Completed: 400/400, lost: 0
- Results recorded: 400 (exactly one per job)
- Jobs requeued from dead workers: 3
- Total time: 15.57 s

## Original queue under contention

The original `get_job()` read the head with LINDEX and removed it with a separate LPOP. With 16 concurrent claimers and 2000 jobs it handed out **994 duplicate claims** and **989 jobs were never run**. The new BLMOVE-based claim had 0 of either in the same test (tests/test_queue.py).
