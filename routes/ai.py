from fastapi import APIRouter
import google.generativeai as genai
import os

router = APIRouter()

@router.post("/recommend")
async def get_recommendations(data: dict):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    # List available models
    models = [m.name for m in genai.list_models()]
    return {"available_models": models}
