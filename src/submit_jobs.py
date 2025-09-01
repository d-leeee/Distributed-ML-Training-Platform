from job_queue import JobQueue

def submit_jobs():
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
    job1 = queue.submit_job('Logistic Regression', 'Wine', param_grid)
    job2 = queue.submit_job('Logistic Regression', 'Wine', param_grid)
    job3 = queue.submit_job('Logistic Regression', 'Wine', param_grid)

if __name__ == "__main__":
    submit_jobs()