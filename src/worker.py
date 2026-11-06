"""Worker process: claims jobs, runs them, keeps a heartbeat, and reaps dead workers."""
import os
import signal
import socket
import threading
import time
import uuid


class Worker:
    def __init__(self, queue, handlers, heartbeat_interval=2.0, reap_interval=5.0):
        self.queue = queue
        self.handlers = handlers  # job kind -> function(job) -> result dict
        self.id = f"{socket.gethostname()}-{os.getpid()}-{uuid.uuid4().hex[:6]}"
        self.heartbeat_interval = heartbeat_interval
        self.reap_interval = reap_interval
        self._stop = threading.Event()

    def stop(self, *_):
        self._stop.set()

    def _heartbeat_loop(self):
        # Runs in a background thread so a long job never lets the heartbeat expire.
        while not self._stop.wait(self.heartbeat_interval):
            self.queue.heartbeat(self.id)

    def process(self, job):
        handler = self.handlers.get(job.get("kind") or "train")
        if handler is None:
            self.queue.fail(self.id, job["id"], f"no handler for kind {job.get('kind')!r}")
            return
        start = time.time()
        try:
            result = handler(job) or {}
        except Exception as e:
            outcome = self.queue.fail(self.id, job["id"], repr(e))
            print(f"[{self.id}] job {job['id']} failed ({outcome}): {e!r}", flush=True)
            return
        result["run_time"] = round(time.time() - start, 4)
        if not self.queue.complete(self.id, job["id"], result):
            # The job was reaped and handed to another worker while this one was running.
            print(f"[{self.id}] job {job['id']} finished but was no longer owned; result dropped", flush=True)

    def run(self, stop_when_empty=False):
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)
        self.queue.register_worker(self.id)
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()
        print(f"[{self.id}] started", flush=True)

        last_reap = 0.0
        try:
            while not self._stop.is_set():
                if time.time() - last_reap >= self.reap_interval:
                    self.queue.reap()
                    last_reap = time.time()
                job = self.queue.claim(self.id, timeout=1.0)
                if job is None:
                    if stop_when_empty:
                        break
                    continue
                self.process(job)
        finally:
            # Graceful shutdown: give back anything still held.
            self._stop.set()
            self.queue.deregister_worker(self.id)
            print(f"[{self.id}] stopped", flush=True)
