"""Print queue stats every few seconds and reap jobs held by dead workers."""
import time

from job_queue import JobQueue


def monitor(interval=3.0):
    queue = JobQueue()
    while True:
        moved = queue.reap()
        s = queue.stats()
        print(
            f"workers={s['workers']} pending={s['pending']} completed={s.get('completed', 0)} "
            f"retried={s.get('retried', 0)} requeued={s.get('requeued', 0)} dead={s.get('dead', 0)}"
            + (f"  (requeued {moved} from dead workers)" if moved else ""),
            flush=True,
        )
        time.sleep(interval)


if __name__ == "__main__":
    monitor()
