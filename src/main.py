import time
from worker import Worker
from job_queue import JobQueue
import warnings
from sklearn.exceptions import ConvergenceWarning
warnings.filterwarnings("ignore", category=ConvergenceWarning)

if __name__ == "__main__":
    queue = JobQueue()
    worker = Worker(queue)
    while True:
        job = queue.get_job()
        if job:
            print(f'Processing job: {job["description"]}', flush=True)
            start = time.time()
            result = worker.process_job(job)
            end = time.time()
            print(f"Training time: {end - start} seconds", flush=True)
            if result is not None:
                print(f'Job result: {result}', flush=True)
        else:
            print("All jobs processed.", flush=True)
            break