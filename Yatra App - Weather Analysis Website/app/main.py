from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from routes.planner import router as planner_router
from routes.stream import router as stream_router
from services.places import PLACES_DATABASE

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"

app = FastAPI(
    title="Yatra Planner API",
    description="Aggregate travel data from multiple sources to provide single plan with SSE support",
    version="1.0.0",
)

# Lets the frontend work even if it is opened from a different dev server (e.g. VS Code Live Server).
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/api", tags=["Info"])
async def api_info():
    return {
        "app": "Yatra Planner API",
        "version": "1.0.0",
        "endpoints": {
            "POST /plan": "Create a travel plan (Aggregated)",
            "POST /stream/plan": "Stream a travel plan (SSE)",
            "GET /destinations": "Destinations with curated places",
            "GET /plan/cache-stats": "View Cache statistics for travel plans",
            "DELETE /plan/cache": "Clear Cache for travel plans",
        },
    }


@app.get("/destinations", tags=["Info"])
async def destinations():
    return sorted(name.title() for name in PLACES_DATABASE)


app.include_router(planner_router)
app.include_router(stream_router)

# Frontend: index at "/", assets under "/static"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(FRONTEND_DIR / "index.html")
