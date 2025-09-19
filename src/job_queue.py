import json
import uuid
from datetime import datetime
from redis.redis_client import RedisClient 

class JobQueue:
    def __init__(self):
        self.queue_name = 'jobs'
        RedisClient.r.hsetnx("jobs_submitted", "count", 0)
        RedisClient.r.hsetnx("jobs_completed", "count", 0)

    def submit_job(self, job_type, description, parameters):
        # job parameters
        job = {
            'id': str(uuid.uuid4()),
            'type': job_type,
            'description': description,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'completed_at': None,
            'parameters': parameters,
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "training_time": 0.0
        }
        # queue job to Redis
        RedisClient.r.rpush(self.queue_name, json.dumps(job))

        # store job in hash map
        RedisClient.r.hset(f"job:{job['id']}", mapping={
            k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
            for k, v in job.items()
        })

        RedisClient.r.rpush("logs", f"Submitted Job {job['id']}")
        return job

    def get_job(self):
        # Get job from queue
        job_data = RedisClient.r.lindex(self.queue_name, 0)
        if job_data:
            job = json.loads(job_data.decode())
            RedisClient.r.lpop(self.queue_name)
            return job
        return None

    def mark_completed(self, job_id, status):
        # update job status and add completion time
        updates = {
            'status': status,
            'completed_at': datetime.now().isoformat()
        }
        RedisClient.r.hset(f"job:{job_id}", mapping=updates)
        RedisClient.r.rpush("logs", f"Job {job_id} marked as {status}")

    def find_job(self, job_id):
        job_data = RedisClient.r.hgetall(f"job:{job_id}")
        if job_data:
            return {**job_data, 'id': job_id}
        else:
            RedisClient.r.rpush("logs", f"Job {job_id} not found")
        return None