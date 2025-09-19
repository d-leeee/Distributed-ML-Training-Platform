import uuid
from models import Model

class Worker:
    def __init__(self, queue):
        self.worker_id = str(uuid.uuid4())
        self.queue = queue

        print("Worker started.", flush=True)

    def process_job(self, job):
        result = None
        try:
            train = Model(job['parameters'])
            result = train.train(job)
            self.queue.mark_completed(job['id'], 'completed')
        except Exception as e:
            print(f'Error Training {job["id"]}, trying again: {e}', flush=True)
            self.queue.mark_completed(job['id'], 'failed')
        return result