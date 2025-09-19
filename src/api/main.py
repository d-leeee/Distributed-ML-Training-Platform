from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import Any, List, Union, Optional
from fastapi.middleware.cors import CORSMiddleware
from redis.redis_client import RedisClient 

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/jobs")
def list_jobs():
    jobs = []
    for k in RedisClient.r.scan_iter("job:*"):
        v = RedisClient.r.hgetall(k)
        jobs.append({field.decode(): value.decode() for field, value in v.items()})
    return jobs 

class CreateJobRequest(BaseModel):
    type: str
    description: str
    parameters: Optional[dict[str, Any]] = None


class CreateJobsRequest(BaseModel):
    jobs: List[CreateJobRequest]


@app.post("/create-job", status_code=201)
def create_job(req: Union[CreateJobRequest, List[CreateJobRequest]] = Body(...)):
    from job_queue import JobQueue
    queue = JobQueue()

    jobs = req if isinstance(req, list) else [req]
    ids: List[str] = []
    for j in jobs:
        job = queue.submit_job(j.type, j.description, j.parameters)
        ids.append(job["id"])

    if ids:
        RedisClient.r.hincrby("jobs_submitted", "count", len(ids))
    return {"submitted": len(ids), "job_ids": ids}