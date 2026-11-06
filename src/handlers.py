"""Job handlers, keyed by job kind. Each takes the job dict and returns a result dict."""
import time


def train(job):
    from models import train_job  # imported lazily so non-ML workers start fast
    return train_job(job)


def simulated_io(job):
    """Stand-in for network-bound work (e.g. an LLM API call): waits for parameters.duration seconds."""
    params = job.get("parameters") or {}
    time.sleep(float(params.get("duration", 0.2)))
    return {"slept": params.get("duration", 0.2)}


def cpu(job):
    """CPU-bound stand-in: a fixed amount of pure-Python arithmetic."""
    params = job.get("parameters") or {}
    n = int(params.get("n", 2_000_000))
    total = 0
    for i in range(n):
        total += i * i % 7
    return {"checksum": total}


HANDLERS = {"train": train, "simulated_io": simulated_io, "cpu": cpu}
