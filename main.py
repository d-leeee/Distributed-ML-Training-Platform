import time
from worker import Worker
from job_queue import JobQueue
import warnings
from sklearn.exceptions import ConvergenceWarning
warnings.filterwarnings("ignore", category=ConvergenceWarning)

if __name__ == "__main__":
    queue = JobQueue()
    param_grid = {
    'C': [0.01, 0.1, 1, 10],
    'penalty': ['l1', 'l2'],
    'solver': ['saga'],
    'max_iter': [100, 200, 300, 400, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000],
    'fit_intercept': [True],
    'class_weight': ['balanced'],
    'random_state': [42]
    }
    job1 = queue.submit_job('Logistic Regression', 'Digits', None)
    job2 = queue.submit_job('Logistic Regression', 'Digits', param_grid)
    worker = Worker(queue)
    while True:
        job = queue.get_job()
        if job:
            print(f'Processing job: {job["description"]}')
            start = time.time()
            result = worker.process_job(job)
            end = time.time()
            print(f"Training time: {end - start} seconds")
            if result is not None:
                print(f'Job result: {result}')
        else:
            print("All jobs processed.")
            break