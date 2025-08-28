import uuid
from training_models.models import Model

class Worker:
    def __init__(self, queue):
        self.worker_id = str(uuid.uuid4())
        self.queue = queue

        print("Worker started.")

    def process_job(self, job):
        train = Model()
        result = train.train(job['type'], job['description'], job['parameters'])
        self.queue.mark_completed(job['id'], 'completed')
        return result