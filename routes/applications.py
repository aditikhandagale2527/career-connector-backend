from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from database import db
from jose import jwt, JWTError
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
import json
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

def calculate_match_score_basic(student_skills: list, job_skills: list) -> int:
    """Fallback: exact string match (used only if AI matching fails)"""
    if not job_skills or not student_skills:
        return 0
    student_skills_lower = [s.lower().strip() for s in student_skills]
    job_skills_lower = [s.lower().strip() for s in job_skills]
    matched = sum(1 for skill in job_skills_lower if skill in student_skills_lower)
    return int((matched / len(job_skills_lower)) * 100)

def calculate_match_score_ai(student_skills: list, job_skills: list) -> int:
    """Smart matching using Gemini — understands related/equivalent skills"""
    if not job_skills or not student_skills:
        return 0

    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
        You are evaluating how well a candidate's skills match a job's required skills.

        Candidate's skills: {', '.join(student_skills)}
        Job's required skills: {', '.join(job_skills)}

        Consider related or equivalent skills as partial or full matches
        (for example, "Data Visualization" experience reasonably supports a
        "Power BI" requirement, "JavaScript" supports "Frontend Development", etc).

        Return ONLY a JSON object in this exact format, nothing else:
        {{"match_score": <integer 0-100>}}
        """

        response = model.generate_content(prompt)
        cleaned = response.text.replace("```json", "").replace("```", "").strip()
        result = json.loads(cleaned)
        score = int(result.get("match_score", 0))
        return max(0, min(100, score))  # clamp between 0-100

    except Exception:
        # If AI matching fails for any reason, fall back to basic exact matching
        return calculate_match_score_basic(student_skills, job_skills)

@router.post("/apply")
async def apply_to_job(body: dict, user=Depends(get_current_user)):
    job_id = body.get("job_id")

    if not job_id:
        raise HTTPException(status_code=400, detail="job_id is required")

    existing = await db["applications"].find_one({
        "job_id": job_id,
        "student_id": user["id"]
    })
    if existing:
        raise HTTPException(status_code=400, detail="Already applied")

    job = await db["jobs"].find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profile = await db["student_profiles"].find_one({"user_id": user["id"]})
    student_skills = profile.get("skills", []) if profile else []

    job_skills = job.get("skills_required", [])
    match_score = calculate_match_score_ai(student_skills, job_skills)

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
