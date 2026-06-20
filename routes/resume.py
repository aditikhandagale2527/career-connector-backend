from fastapi import APIRouter, UploadFile, File
import PyPDF2
import io
import google.generativeai as genai
import os

router = APIRouter()

@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    # Read PDF
    contents = await file.read()
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(contents))
    
    # Extract text
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    # Use Gemini to extract skills
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    Extract all technical and soft skills from this resume text.
    Return ONLY a JSON array of skills like: ["Python", "SQL", "Communication"]
    
    Resume text:
    {text[:3000]}
    """
    
    response = model.generate_content(prompt)
    skills_text = response.text.replace("```json", "").replace("```", "").strip()
    
    return {
        "extracted_text": text[:500],
        "skills": skills_text
    }
