from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.user import router as user_router
from routes.jobs import router as jobs_router
from routes.ai import router as ai_router
from routes.resume import router as resume_router
from routes.recruiter import router as recruiter_router
from routes.applications import router as applications_router
from routes.livejobs import router as livejobs_router

app = FastAPI(title="Career Connector API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(ai_router, prefix="/api/ai", tags=["AI"])
app.include_router(resume_router, prefix="/api/resume", tags=["Resume"])
app.include_router(recruiter_router, prefix="/api/recruiter", tags=["Recruiter"])
app.include_router(applications_router, prefix="/api/applications", tags=["Applications"])
app.include_router(livejobs_router, prefix="/api/livejobs", tags=["LiveJobs"])

@app.get("/")
def root():
    return {"message": "Career Connector API is running!"}
