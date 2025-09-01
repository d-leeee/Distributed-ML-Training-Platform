import redis
import json
import uuid
import os
from datetime import datetime

class JobQueue:
    def __init__(self):
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.r = redis.Redis(host=redis_host, port=6379, db=0)
        self.queue_name = 'jobs'

    def submit_job(self, job_type, description, parameters):
        # job parameters
        job = {
            'id': str(uuid.uuid4()),
            'type': job_type,
            'description': description,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'completed_at': None,
            'parameters': parameters
        }
        # queue job to Redis
        self.r.rpush(self.queue_name, json.dumps(job))

        # store job in hash map
        self.r.hset(f"job:{job['id']}", mapping={
            k: v if isinstance(v, str) else json.dumps(v) 
            for k, v in job.items()
        })

        print(f"Submitted Job {job['id']}", flush=True)
        return job

    def get_job(self):
        # Get job from queue
        job_data = self.r.lindex(self.queue_name, 0)
        if job_data:
            job = json.loads(job_data.decode())
            self.r.lpop(self.queue_name)
            return job
        return None

    def mark_completed(self, job_id, status):
        # update job status and add completion time
        updates = {
            'status': status,
            'completed_at': datetime.now().isoformat()
        }
        self.r.hset(f"job:{job_id}", mapping=updates)
        print(f"Job {job_id} marked as {status}", flush=True)

    def find_job(self, job_id):
        job_data = self.r.hgetall(job_id)
        if job_data:
            return {**job_data, 'id': job_id}
        else:
            print("Job not found", flush=True)
        return None