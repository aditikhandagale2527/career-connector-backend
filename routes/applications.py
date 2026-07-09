from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from database import db
from jose import jwt, JWTError
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = await db["users"].find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"email": email, "id": str(user["_id"]), "name": user["name"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def calculate_match_score(student_skills: list, job_skills: list) -> int:
    if not job_skills or not student_skills:
        return 0
    # normalize both lists to lowercase
    student_skills_lower = [s.lower().strip() for s in student_skills]
    job_skills_lower = [s.lower().strip() for s in job_skills]

    matched = sum(1 for skill in job_skills_lower if skill in student_skills_lower)
    score = int((matched / len(job_skills_lower)) * 100)
    return score

@router.post("/apply")
async def apply_to_job(body: dict, user=Depends(get_current_user)):
    job_id = body.get("job_id")
    student_skills = body.get("skills", [])

    if not job_id:
        raise HTTPException(status_code=400, detail="job_id is required")

    # Check if already applied
    existing = await db["applications"].find_one({
        "job_id": job_id,
        "student_id": user["id"]
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already applied")

    # Check job exists
    job = await db["jobs"].find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Calculate match score
    job_skills = job.get("skills_required", [])
    match_score = calculate_match_score(student_skills, job_skills)

    # Auto shortlist if match >= 60%, otherwise auto reject
    status = "shortlisted" if match_score >= 60 else "rejected"

    application = {
        "job_id": job_id,
        "student_id": user["id"],
        "student_email": user["email"],
        "student_name": user["name"],
        "student_skills": student_skills,
        "match_score": match_score,
        "status": status,
        "applied_at": datetime.utcnow().isoformat()
    }
    await db["applications"].insert_one(application)
    return {
        "message": "Application submitted successfully",
        "match_score": match_score,
        "status": status
    }

@router.get("/my-applications")
async def get_my_applications(user=Depends(get_current_user)):
    applications = []
    async for app in db["applications"].find({"student_id": user["id"]}):
        app["_id"] = str(app["_id"])
        applications.append(app)
    return applications
