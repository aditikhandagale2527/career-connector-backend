from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from database import db
from models import RegisterUser, LoginUser
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register")
async def register(user: RegisterUser):
    existing = await db["users"].find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = pwd_context.hash(user.password[:72])
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_pw,
        "role": user.role
    }
    await db["users"].insert_one(new_user)
    return {"message": "User registered successfully"}

@router.post("/login")
async def login(user: LoginUser):
    db_user = await db["users"].find_one({"email": user.email})
    if not db_user or not pwd_context.verify(user.password[:72], db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": user.email, "role": db_user["role"]})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def get_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        user = await db["users"].find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"name": user["name"], "email": user["email"], "role": user["role"]}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")