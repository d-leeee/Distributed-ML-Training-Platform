from fastapi import FastAPI
import redis
import os

app = FastAPI()

r = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379, db=0)

@app.get("/jobs")
def list_jobs():
    jobs = []
    for k in r.scan_iter("job:*"):
        v = r.hgetall(k)
        jobs.append({field.decode(): value.decode() for field, value in v.items()})
    return jobs
