from job_queue import JobQueue
import time
import os
import redis

def submit_jobs():
    queue = JobQueue()
    r = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)
    param_grid = {
        "C": [0.01, 0.1, 1, 10],
        "penalty": ["l1", "l2"],
        "solver": ["saga"],
        "max_iter": [100, 200, 300, 400, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000],
        "fit_intercept": [true],
        "class_weight": ["balanced"],
        "random_state": [42]
    }
    count = 0
    job1 = queue.submit_job("Logistic Regression", "Iris", None)
    count += 1
    job2 = queue.submit_job("Logistic Regression", "Wine", None)
    count += 1
    job3 = queue.submit_job("Logistic Regression", "Breast Cancer", None)
    count += 1
    r.hset("jobs_submitted", "count", count)
    r.hset("jobs_completed", "count", 0)

if __name__ == "__main__":
    submit_jobs()