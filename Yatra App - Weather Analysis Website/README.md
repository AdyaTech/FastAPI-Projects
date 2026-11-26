# Yatra Planner

FastAPI backend + plain HTML/CSS/JS frontend. The backend serves the frontend, so there is one process to run.

## Run it from the VS Code terminal

Open the `yatra-app` folder in VS Code, then **Terminal → New Terminal**.

macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run.py
```

Open http://127.0.0.1:8000 (API docs at `/docs`). You can also press **F5** ("Yatra: run server").

## API keys
Keys live in `.env` (see `.env.example`): `WEATHERAPI_API_KEY` and `EXCHANGERATE_API_KEY`.

## Tests
```bash
python -m unittest discover tests
```

## Notes
- Curated places exist for Goa, Jaipur and Manali only; weather works for any city.
- Endpoints: `POST /plan`, `POST /stream/plan` (SSE), `GET /destinations`, `GET /plan/cache-stats`, `DELETE /plan/cache`.
