from typing import Any, List, Optional, Union

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from job_queue import JobQueue

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
queue = JobQueue()


class CreateJobRequest(BaseModel):
    type: str
    description: str
    parameters: Optional[dict[str, Any]] = None
    kind: str = "train"


@app.post("/create-job", status_code=201)
def create_job(req: Union[CreateJobRequest, List[CreateJobRequest]] = Body(...)):
    jobs = req if isinstance(req, list) else [req]
    ids = [queue.submit_job(j.type, j.description, j.parameters, kind=j.kind)["id"] for j in jobs]
    return {"submitted": len(ids), "job_ids": ids}


@app.get("/jobs")
def list_jobs():
    ids = [k.split(":", 1)[1] for k in queue.r.scan_iter("job:*")]
    return [queue.get_job(i) for i in ids]


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = queue.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@app.get("/stats")
def stats():
    return queue.stats()
