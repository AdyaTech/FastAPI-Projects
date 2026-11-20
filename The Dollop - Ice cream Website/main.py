from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

try:  # optional: reads GROQ_API_KEY from a .env file if python-dotenv is installed
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import ai
from data import menu_items
from models import AIStatus, ComposeRequest, Cup, MenuItem, MenuResponse

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="Dollop API",
    description="Menu API and the Flavor Lab (AI) for Dollop, a small-batch gelato shop.",
)

# The website lives in static/ and is served by this same app, so no CORS setup is needed.
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api")
def api_root():
    return {"message": "Welcome to the Dollop API"}


# /menu                  -> everything
# /menu?category=sorbet  -> one category
# /menu?vegan=true       -> dairy free only

@app.get("/menu", response_model=MenuResponse)
def get_menu(
    category: str | None = Query(None, description="gelato, sorbet or toppers"),
    vegan: bool | None = Query(None, description="true for dairy free items only"),
):
    items = menu_items
    if category:
        wanted = category.strip().lower()
        items = [i for i in items if i["category"] == wanted]
        if not items:
            raise HTTPException(status_code=404, detail=f"No items in category: {category}")
    if vegan:
        items = [i for i in items if i["vegan"]]
    return MenuResponse(count=len(items), items=items)


@app.get("/menu/{item_id}", response_model=MenuItem)
def get_item(item_id: int):
    item = ai.BY_ID.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Menu item with id {item_id} not found")
    return item


# ---------- Flavor Lab ----------

@app.get("/ai/status", response_model=AIStatus)
def ai_status():
    live = ai.mode() == "groq"
    return {"mode": ai.mode(), "model": ai.groq_model() if live else None}


@app.get("/ai/featured", response_model=Cup)
def ai_featured():
    """The cup of the day. Always built by the offline matcher, so it costs nothing."""
    return ai.featured_cup()


@app.post("/ai/compose", response_model=Cup)
async def ai_compose(body: ComposeRequest, request: Request):
    visitor = request.client.host if request.client else "unknown"
    if ai.rate_limited(visitor):
        raise HTTPException(status_code=429, detail="Too many requests. Wait a minute and try again.")
    return await ai.compose(body.message, [t.model_dump() for t in body.history])
