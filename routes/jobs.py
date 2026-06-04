from fastapi import APIRouter, HTTPException
from database import db
from models import JobPost
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_job(job: JobPost):
    new_job = job.dict()
    result = await db["jobs"].insert_one(new_job)
    return {"message": "Job posted successfully", "id": str(result.inserted_id)}

@router.get("/")
async def get_jobs():
    jobs = []
    async for job in db["jobs"].find():
        job["_id"] = str(job["_id"])
        jobs.append(job)
    return jobs

@router.get("/{job_id}")
async def get_job(job_id: str):
    job = await db["jobs"].find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job["_id"] = str(job["_id"])
    return job