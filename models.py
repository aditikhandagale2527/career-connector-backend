from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterUser(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "student"  # student or recruiter

class LoginUser(BaseModel):
    email: EmailStr
    password: str

class JobPost(BaseModel):
    title: str
    company: str
    location: str
    description: str
    skills_required: list[str]

# Add these to your existing models.py

from typing import Optional

class RecruiterJobPost(BaseModel):
    title: str
    company: str
    location: str
    job_type: str  # Full-time, Part-time, Internship, Remote
    description: str
    skills_required: list[str]
    salary_range: Optional[str] = None
    deadline: Optional[str] = None

class ApplicationStatus(BaseModel):
    status: str  # pending, shortlisted, rejected
