import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

APP_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(APP_DIR, "..", ".env"))
load_dotenv()  # also honour an .env in the working directory

from routes.analyse import router as analyse_router
from routes.analyses import router as analyses_router
from services.storage import UPLOAD_DIR, init_db

init_db()

app = FastAPI(
    title="Netra Vision API",
    description="AI-powered crop disease detection. Upload plant photos, get a disease diagnosis and treatment plan.",
    version="1.1.0",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/ui/")


@app.get("/api")
async def api_index():
    return {
        "app": "netra-vision",
        "version": "1.1.0",
        "frontend": "GET /ui",
        "endpoints": {
            "POST /analyse": "Upload an image for disease detection",
            "POST /analyse/batch": "Upload multiple images for batch disease detection",
            "GET /analyses": "List all saved analyses",
            "GET /analyses/{analysis_id}": "Get one analysis",
            "DELETE /analyses/{analysis_id}": "Delete one analysis",
            "DELETE /analyses": "Delete all analyses",
        },
    }


app.include_router(analyse_router)
app.include_router(analyses_router)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/ui", StaticFiles(directory=os.path.join(APP_DIR, "..", "frontend"), html=True), name="frontend")
