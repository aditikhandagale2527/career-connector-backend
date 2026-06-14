from fastapi import APIRouter
import google.generativeai as genai
import os

router = APIRouter()

@router.post("/recommend")
async def get_recommendations(data: dict):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash") 
    
    skills = data.get("skills", [])
    prompt = f"""
    Based on these skills: {', '.join(skills)}
    Suggest 5 career paths with:
    1. Job title
    2. Why it suits these skills
    3. Skill gaps to fill
    Return as JSON.
    """
    response = model.generate_content(prompt)
    return {"recommendations": response.text}
