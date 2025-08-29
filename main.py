from worker import Worker
from job_queue import JobQueue

if __name__ == "__main__":
    queue = JobQueue()
    job1 = queue.submit_job('Logistic Regression', 'Iris', None)
    job2 = queue.submit_job('Logistic Regression', 'Wine', None)
    worker = Worker(queue)
    while True:
        job = queue.get_job()
        if job:
            print(f'Processing job: {job["description"]}')
            result = worker.process_job(job)
            if result is not None:
                print(f'Job result: {result}')
        else:
            print("All jobs processed.")
            break