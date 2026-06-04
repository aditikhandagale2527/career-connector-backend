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