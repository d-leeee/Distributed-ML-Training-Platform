import time
import warnings
from worker import Worker
from job_queue import JobQueue
from redis.redis_client import RedisClient
from sklearn.exceptions import ConvergenceWarning
warnings.filterwarnings("ignore", category=ConvergenceWarning)

if __name__ == "__main__":
    queue = JobQueue()
    worker = Worker(queue)

    while True:
        job = queue.get_job()
        if job:
            result = None
            try:
                RedisClient.r.rpush("logs", f'Processing job: {job["description"]}')
                start = time.time()
                result = worker.process_job(job)
                end = time.time()

                training_time = end - start
                RedisClient.r.hset(f"job:{job['id']}", "training_time", training_time)
                RedisClient.r.hincrby("jobs_completed", "count", 1)

                if result is not None:
                    RedisClient.r.rpush("logs", f'Job result: {result}')
            except Exception as e:
                RedisClient.r.rpush("logs", f"Error processing job {job['id']}: {e}")
        else:
            time.sleep(1)
            continue
