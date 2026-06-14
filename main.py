from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.user import router as user_router
from routes.jobs import router as jobs_router
from routes.ai import router as ai_router


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


@app.get("/")
def root():
    return {"message": "Career Connector API is running!"}
