from job_queue import JobQueue
import uuid

class Worker:
    def __init__(self, queue):
        self.worker_id = str(uuid.uuid4())
        self.queue = queue

        print("Worker started.")

    def process_job(self, job):
        job_id = job['id']
        job_type = job['type']

        if job_type == 'Linear Regression':
            # Process linear regression job
            pass
        elif job_type == 'Math':
            result = self.math(job['parameters'])
        else:
            raise ValueError("Unknown job type")
        self.queue.mark_completed(job_id, 'completed')
        return result

    def math(self, parameters):
        a = parameters.get('a')
        b = parameters.get('b')

        if parameters.get('operation') == 'add':
            return a + b
        elif parameters.get('operation') == 'multiply':
            return a * b
        else:
            raise ValueError("Unknown operation")
        
if __name__ == "__main__":
    queue = JobQueue()
    job1 = queue.submit_job('Math', 'Add two numbers', {'a': 5, 'b': 10, 'operation': 'add'})
    job2 = queue.submit_job('Math', 'Multiply two numbers', {'a': 5, 'b': 10, 'operation': 'multiply'})

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

    print("Summary: ")
    for job in [job1, job2]:
        status = queue.r.hget(f'job:{job["id"]}', 'status')
        completion_time = queue.r.hget(f'job:{job["id"]}', 'completed_at')
        print(f"Job '{job['description']}' status: {status.decode() if status else None}, completed at: {completion_time.decode() if completion_time else None}")