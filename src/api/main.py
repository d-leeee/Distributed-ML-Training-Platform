from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Any, List, Union, Optional
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


class CreateJobRequest(BaseModel):
    type: str
    description: str
    parameters: Optional[dict[str, Any]] = None


class CreateJobsRequest(BaseModel):
    jobs: List[CreateJobRequest]


@app.post("/create_job", status_code=201)
def create_job(req: Union[CreateJobRequest, List[CreateJobRequest]] = Body(...)):
    from job_queue import JobQueue
    queue = JobQueue()

    jobs = req if isinstance(req, list) else [req]
    ids: List[str] = []
    for j in jobs:
        job = queue.submit_job(j.type, j.description, j.parameters)
        ids.append(job["id"])

    if ids:
        r.hincrby("jobs_submitted", "count", len(ids))
    return {"submitted": len(ids), "job_ids": ids}