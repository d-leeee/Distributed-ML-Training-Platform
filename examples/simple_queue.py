import redis
import json
import uuid

class SimpleJobQueue:
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.queue_name = 'simple_jobs'
        self.completed_jobs = []

    def submit_job(self, job_id, job_type, job_description, job_status):
        job = {
            'id': job_id,
            'type': job_type,
            'description': job_description,
            'status': job_status
        }
        self.r.rpush(self.queue_name, json.dumps(job))
        self.r.hset(job_id, mapping=job)
        return job['id']

    def get_job(self):
        # Get job from queue (with timeout)
        job_data = self.r.lindex(self.queue_name, 0)
        if job_data:
            job = json.loads(job_data.decode())
            self.r.lpop(self.queue_name)
            return job
        return None

    def mark_completed(self, job_id, result):
        self.r.hset(job_id, 'status', result)
        return

    def find_job(self, job_id):
        job_data = self.r.hgetall(job_id)
        if job_data:
            return {**job_data, 'id': job_id}
        else:
            print("Job not found")
        return None

    def test_queue():
        queue = SimpleJobQueue()

        job1 = queue.submit_job('frontend', 'render', 'Render the homepage', 'not started')
        job2 = queue.submit_job('backend', 'process', 'do not finish', 'not started')

        while queue.r.llen(queue.queue_name) > 0:
            job = queue.get_job()
            if job:
                print("Processing Job:", job['id'])
                if job['description'] == 'do not finish':
                    print("Skipping job:", job['id'])
                    queue.mark_completed(job['id'], 'skipped')
                    print(queue.find_job(job['id']))
                else:
                    queue.mark_completed(job['id'], 'finished')
                    print(queue.find_job(job['id']))

if __name__ == "__main__":
    SimpleJobQueue.test_queue()