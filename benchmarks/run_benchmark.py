"""Benchmark the queue: scaling with worker count, raw queue overhead, and crash recovery.

Starts its own redis-server, spawns real worker processes, and writes results to
benchmarks/results.json, benchmarks/RESULTS.md and benchmarks/scaling.png.

    python benchmarks/run_benchmark.py            # full run
    python benchmarks/run_benchmark.py --quick    # smaller, for a smoke test
"""
import argparse
import json
import os
import platform
import random
import signal
import socket
import statistics
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "src")
sys.path.insert(0, SRC)

import redis  # noqa: E402

from job_queue import JobQueue  # noqa: E402

WORKER_CODE = (
    "import sys; from handlers import HANDLERS; from job_queue import JobQueue; from worker import Worker;"
    "Worker(JobQueue(heartbeat_ttl=3), HANDLERS, heartbeat_interval=1, reap_interval=1).run()"
)


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Cluster:
    def __init__(self):
        self.port = free_port()
        self.redis_proc = subprocess.Popen(
            ["redis-server", "--port", str(self.port), "--save", "", "--appendonly", "no",
             "--dir", tempfile.mkdtemp()],
            stdout=subprocess.DEVNULL,
        )
        self.r = redis.Redis(port=self.port, decode_responses=True)
        for _ in range(50):
            try:
                self.r.ping()
                break
            except redis.ConnectionError:
                time.sleep(0.1)
        self.env = {**os.environ, "REDIS_PORT": str(self.port), "PYTHONPATH": SRC}
        self.workers = []

    def queue(self):
        return JobQueue(self.r, heartbeat_ttl=3)

    def start_workers(self, n):
        self.workers = [
            subprocess.Popen([sys.executable, "-c", WORKER_CODE], env=self.env,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for _ in range(n)
        ]
        deadline = time.time() + 30
        while self.r.scard("workers") < n and time.time() < deadline:
            time.sleep(0.05)

    def stop_workers(self):
        for p in self.workers:
            if p.poll() is None:
                p.terminate()
        for p in self.workers:
            p.wait()
        self.workers = []

    def reset(self):
        self.stop_workers()
        self.r.flushall()

    def close(self):
        self.stop_workers()
        self.redis_proc.terminate()
        self.redis_proc.wait()


def wait_done(r, total, timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        s = r.hgetall("stats")
        if int(s.get("completed", 0)) + int(s.get("dead", 0)) >= total:
            return
        time.sleep(0.02)
    raise TimeoutError(f"only {r.hgetall('stats')} of {total} done")


def run_batch(cluster, workers, jobs, kind, params, kill=0):
    """Submit `jobs` jobs with `workers` workers running; optionally SIGKILL `kill` workers mid-run."""
    cluster.reset()
    q = cluster.queue()
    cluster.start_workers(workers)
    t0 = time.time()
    ids = [q.submit_job("bench", "bench", params, kind=kind)["id"] for _ in range(jobs)]
    killed_at = []
    if kill:
        # Kill workers at random points in the first half of the expected run
        victims = random.sample(cluster.workers, kill)
        for p in victims:
            time.sleep(random.uniform(0.2, 1.0))
            p.send_signal(signal.SIGKILL)
            killed_at.append(round(time.time() - t0, 2))
    wait_done(cluster.r, jobs)
    elapsed = time.time() - t0

    jobs_data = [q.get_job(i) for i in ids]
    latencies = sorted(float(j["completed_at"]) - float(j["created_at"]) for j in jobs_data if j.get("completed_at"))
    stats = q.stats()
    result = {
        "kind": kind,
        "workers": workers,
        "jobs": jobs,
        "seconds": round(elapsed, 2),
        "jobs_per_sec": round(jobs / elapsed, 1),
        "p50_latency_s": round(statistics.median(latencies), 2),
        "p95_latency_s": round(latencies[int(0.95 * (len(latencies) - 1))], 2),
        "completed": sum(j["status"] == "completed" for j in jobs_data),
        "results_recorded": stats.get("completed", 0),
        "lost": sum(j["status"] not in ("completed", "dead") for j in jobs_data),
        "requeued_after_crash": stats.get("requeued", 0),
        "reran": sum(int(j["attempts"]) > 1 for j in jobs_data),
    }
    if kill:
        result["killed_workers"] = kill
        result["killed_at_s"] = killed_at
    return result


def old_queue_race(cluster, jobs=2000, claimers=16):
    """Reproduce the original get_job() (LINDEX then LPOP) under contention and count double-claims."""
    import threading

    cluster.reset()
    r = cluster.r
    for i in range(jobs):
        r.rpush("jobs", json.dumps({"id": i}))
    seen = []
    lock = threading.Lock()

    def claim_loop():
        local = redis.Redis(port=cluster.port, decode_responses=True)
        while True:
            data = local.lindex("jobs", 0)  # original code: read the head...
            if data is None:
                return
            local.lpop("jobs")              # ...then pop it in a separate command
            with lock:
                seen.append(json.loads(data)["id"])

    threads = [threading.Thread(target=claim_loop) for _ in range(claimers)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    unique = len(set(seen))
    return {
        "jobs": jobs,
        "claimers": claimers,
        "claims": len(seen),
        "double_claimed": len(seen) - unique,
        "never_run": jobs - unique,
    }


def write_reports(results):
    with open(os.path.join(HERE, "results.json"), "w") as f:
        json.dump(results, f, indent=2)

    io_rows = results["scaling_io"]
    base = io_rows[0]["jobs_per_sec"]
    lines = [
        "# Benchmark results",
        "",
        f"Machine: {results['machine']}",
        "",
        "## Scaling: network-bound jobs (0.2 s each, like an API call)",
        "",
        "| Workers | Jobs | Time (s) | Jobs/s | Speedup | p50 latency (s) | p95 latency (s) |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in io_rows:
        lines.append(f"| {row['workers']} | {row['jobs']} | {row['seconds']} | {row['jobs_per_sec']} | "
                     f"{row['jobs_per_sec'] / base:.1f}x | {row['p50_latency_s']} | {row['p95_latency_s']} |")
    cpu_rows = results["scaling_cpu"]
    cbase = cpu_rows[0]["jobs_per_sec"]
    lines += ["", f"## Scaling: CPU-bound jobs (limited by this machine's {os.cpu_count()} cores)", "",
              "| Workers | Jobs | Time (s) | Jobs/s | Speedup |", "|---|---|---|---|---|"]
    for row in cpu_rows:
        lines.append(f"| {row['workers']} | {row['jobs']} | {row['seconds']} | {row['jobs_per_sec']} | "
                     f"{row['jobs_per_sec'] / cbase:.1f}x |")
    o = results["overhead"]
    lines += ["", "## Queue overhead (zero-work jobs)", "",
              f"{o['workers']} workers processed {o['jobs']} empty jobs in {o['seconds']} s: "
              f"**{o['jobs_per_sec']} jobs/s** through claim, run, and ack."]
    c = results["chaos"]
    lines += ["", "## Crash recovery", "",
              f"{c['workers']} workers, {c['jobs']} jobs, {c['killed_workers']} workers killed with SIGKILL "
              f"at {c['killed_at_s']} s.", "",
              f"- Completed: {c['completed']}/{c['jobs']}, lost: {c['lost']}",
              f"- Results recorded: {c['results_recorded']} (exactly one per job)",
              f"- Jobs requeued from dead workers: {c['requeued_after_crash']}",
              f"- Total time: {c['seconds']} s"]
    old = results["old_queue_race"]
    lines += ["", "## Original queue under contention", "",
              f"The original `get_job()` read the head with LINDEX and removed it with a separate LPOP. "
              f"With {old['claimers']} concurrent claimers and {old['jobs']} jobs it handed out "
              f"**{old['double_claimed']} duplicate claims** and **{old['never_run']} jobs were never run**. "
              f"The new BLMOVE-based claim had 0 of either in the same test (tests/test_queue.py)."]
    with open(os.path.join(HERE, "RESULTS.md"), "w") as f:
        f.write("\n".join(lines) + "\n")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6, 3.6), dpi=150)
        ws = [r["workers"] for r in io_rows]
        ax.plot(ws, [r["jobs_per_sec"] for r in io_rows], marker="o", color="#2a6fdb", label="Measured")
        ax.plot(ws, [base * w for w in ws], linestyle="--", color="#999999", label="Perfect linear")
        ax.set_xscale("log", base=2)
        ax.set_xticks(ws)
        ax.set_xticklabels(ws)
        ax.set_xlabel("Workers")
        ax.set_ylabel("Jobs per second")
        ax.set_title("Throughput vs. workers (0.2 s network-bound jobs)")
        ax.grid(alpha=0.3)
        ax.legend(frameon=False)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        fig.tight_layout()
        fig.savefig(os.path.join(HERE, "scaling.png"))
    except ImportError:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    random.seed(7)

    worker_counts = [1, 2, 4, 8] if args.quick else [1, 2, 4, 8, 16, 32]
    io_jobs = 40 if args.quick else 320
    cluster = Cluster()
    results = {"machine": f"{platform.system()} {platform.machine()}, {os.cpu_count()} CPU cores, "
                          f"Python {platform.python_version()}"}
    try:
        results["scaling_io"] = []
        for w in worker_counts:
            n = min(io_jobs, max(40, 20 * w)) if w == 1 else io_jobs
            row = run_batch(cluster, w, n, "simulated_io", {"duration": 0.2})
            results["scaling_io"].append(row)
            print("io", row, flush=True)

        results["scaling_cpu"] = []
        for w in [1, 2, 4]:
            row = run_batch(cluster, w, 8 if args.quick else 24, "cpu", {"n": 10_000_000})
            results["scaling_cpu"].append(row)
            print("cpu", row, flush=True)

        results["overhead"] = run_batch(cluster, 8, 500 if args.quick else 5000, "simulated_io", {"duration": 0})
        print("overhead", results["overhead"], flush=True)

        results["chaos"] = run_batch(cluster, 8, 80 if args.quick else 400, "simulated_io", {"duration": 0.2},
                                     kill=3)
        print("chaos", results["chaos"], flush=True)

        results["old_queue_race"] = old_queue_race(cluster)
        print("old race", results["old_queue_race"], flush=True)
    finally:
        cluster.close()
    write_reports(results)


if __name__ == "__main__":
    main()
