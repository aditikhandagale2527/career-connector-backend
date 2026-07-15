from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter()

@router.get("/search")
async def search_live_jobs(query: str, location: str = "India"):
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    if not app_id or not app_key:
        raise HTTPException(status_code=500, detail="Adzuna credentials not configured")

    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "results_per_page": 6,
        "what": query,
        "where": location,
        "content-type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            data = response.json()
            return {"results": data.get("results", [])}
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to fetch live jobs")
