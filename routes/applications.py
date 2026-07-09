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

@router.post("/apply")
async def apply_to_job(body: dict, user=Depends(get_current_user)):
    job_id = body.get("job_id")
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

    application = {
        "job_id": job_id,
        "student_id": user["id"],
        "student_email": user["email"],
        "student_name": user["name"],
        "status": "pending",
        "applied_at": datetime.utcnow().isoformat()
    }
    await db["applications"].insert_one(application)
    return {"message": "Application submitted successfully"}
