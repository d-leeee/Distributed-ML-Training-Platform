"""Submit a sample batch: every model on every dataset, plus one tuned job."""
from job_queue import JobQueue
from models import ALGORITHMS, DATASETS


def submit_jobs():
    queue = JobQueue()
    count = 0
    for model in ALGORITHMS:
        for dataset in DATASETS:
            queue.submit_job(model, dataset)
            count += 1
    # Lists become a GridSearchCV grid
    queue.submit_job("Logistic Regression", "Digits", {"C": [0.01, 0.1, 1, 10], "max_iter": 2000})
    count += 1
    print(f"Submitted {count} jobs", flush=True)


if __name__ == "__main__":
    submit_jobs()
