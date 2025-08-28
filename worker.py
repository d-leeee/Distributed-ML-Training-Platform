import uuid
from training_models.models import Model

class Worker:
    def __init__(self, queue):
        self.worker_id = str(uuid.uuid4())
        self.queue = queue

        print("Worker started.")

    def process_job(self, job):
        job_id = job['id']
        job_type = job['type']
        train = Model()

        if job_type in train.model:
            result = train.model[job_type].train(job['parameters'])
        else:
            raise ValueError("Unknown job type")
        self.queue.mark_completed(job_id, 'completed')
        return result