import uuid
from models import Model
from redis.redis_client import RedisClient 

class Worker:
    def __init__(self, queue):
        self.worker_id = str(uuid.uuid4())
        self.queue = queue

        RedisClient.r.push("logs","Worker started.")

    def process_job(self, job):
        result = None
        try:
            train = Model(job['parameters'])
            result = train.train(job)
            self.queue.mark_completed(job['id'], 'completed')
        except Exception as e:
            RedisClient.r.push("logs", f'Error Training {job["id"]}, trying again: {e}')
            self.queue.mark_completed(job['id'], 'failed')
        return result