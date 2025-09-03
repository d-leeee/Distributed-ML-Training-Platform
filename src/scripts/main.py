import os
import time
import warnings
import redis

from worker import Worker
from job_queue import JobQueue

from sklearn.exceptions import ConvergenceWarning
warnings.filterwarnings("ignore", category=ConvergenceWarning)

if __name__ == "__main__":
    queue = JobQueue()
    worker = Worker(queue)
    r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, db=0)

    while True:
        job = queue.get_job()
        if job:
            print(f'Processing job: {job["description"]}', flush=True)

            start = time.time()
            result = worker.process_job(job)
            end = time.time()

            training_time = end - start
            r.hset(f"job:{job['id']}", "training_time", training_time)
            r.hincrby("jobs_completed", "count", 1)
            
            if result is not None:
                print(f'Job result: {result}', flush=True)
        else:
            print("All jobs processed.", flush=True)
            break
