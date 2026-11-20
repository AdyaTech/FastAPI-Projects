# Dollop

A small-batch gelato shop website with a FastAPI backend and a plain HTML/CSS/JS frontend.
Browse the flavors, build a cup, and let the **Flavor Lab** (the AI feature) build one for you from a mood.

## The big AI feature: Flavor Lab

Type something like *"rainy evening, want something warm, nothing too sweet"* or
*"celebrating with a dairy-free friend, under ₹300"*. The Flavor Lab:

1. builds a cup (2 to 3 scoops and an optional topper) from what is actually in stock,
2. names it, explains each pick, and shows the total,
3. lets you **tweak** it ("swap the coffee", "make it cheaper") because it remembers the conversation,
4. drops the scoops into your cup with one click.

How it works:

- With `GROQ_API_KEY` set, the backend sends today's menu and your request to Llama 3.3 on Groq and asks for JSON back.
- Without a key, a built-in taste matcher does the job, so the project always runs.
- Either way, the server **checks every answer against the real menu**. Made-up flavors, sold-out flavors,
  repeats and blown budgets are fixed before the website sees them.
- Requests are rate limited per visitor (15 a minute) so nobody can drain your API key.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

# optional, for the real AI (free key from https://console.groq.com/keys)
cp .env.example .env             # then paste your key after GROQ_API_KEY=

uvicorn main:app --reload
```

Open http://127.0.0.1:8000 for the website and http://127.0.0.1:8000/docs for the API docs.

## Tests

```bash
pytest
```

## API

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/menu` | Whole menu. Filters: `?category=sorbet`, `?vegan=true` |
| GET | `/menu/{id}` | One item |
| GET | `/ai/status` | Real AI or offline matcher |
| GET | `/ai/featured` | Cup of the day |
| POST | `/ai/compose` | `{"message": "...", "history": [...]}` returns a cup |

## Files

- `data.py`: the freezer. Edit flavors, prices and what is sold out here.
- `ai.py`: the Flavor Lab (prompt, Groq call, offline matcher, safety checks).
- `main.py`, `models.py`: the API.
- `static/`: the website (`index.html`, `css/style.css`, `js/app.js`).
