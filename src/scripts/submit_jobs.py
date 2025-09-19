from job_queue import JobQueue
from redis.redis_client import RedisClient 


def submit_jobs():
    queue = JobQueue()
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
    RedisClient.r.hset("jobs_submitted", "count", count)
    RedisClient.r.hset("jobs_completed", "count", 0)

if __name__ == "__main__":
    submit_jobs()