# Netra Vision

Upload a photo of a crop leaf and get the likely disease, how serious it is, and a treatment plan sorted by urgency. FastAPI backend, plain-HTML frontend, no build step.

## Run it in VS Code (no API key needed)

Netra works out of the box. With no key it uses a built-in **offline colour check**: it measures how much of the leaf is green, yellow or brown and gives a severity estimate with general advice. It runs on your computer, needs no account and sends nothing anywhere. It can't name your crop or confirm a disease, and the page labels its results as a rough estimate.

**Before you start:** install Python 3.10 or newer from https://www.python.org/downloads/ (on Windows tick **"Add python.exe to PATH"**) and VS Code with its **Python** extension.

1. Unzip `netra-vision.zip`, then in VS Code choose **File > Open Folder** and pick the `netra-vision` folder.
2. Open the terminal: **Terminal > New Terminal** (shortcut Ctrl+`).
3. Run these commands, one at a time:

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows (PowerShell, the default VS Code terminal)
.venv\Scripts\Activate.ps1

# Mac / Linux
source .venv/bin/activate
```

Install and start:

```bash
pip install -r requirements.txt
python run.py
```

4. Open **http://localhost:8000** (Ctrl+click the link in the terminal). Drop in a leaf photo from `samples/` and press **Analyse**.
5. Stop it with **Ctrl+C** in the terminal.

Next time you only need to open the folder and run `python run.py`. On Mac/Linux use `python3` if `python` isn't found.

**Or press F5.** After step 3 (`pip install`), pick the `.venv` interpreter if VS Code asks (bottom-right corner, or Ctrl+Shift+P > "Python: Select Interpreter"), then press **F5**. The server starts under the debugger.

**Troubleshooting**

- *Windows says running scripts is disabled when activating:* run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal, then activate again. Or skip activation and run `.venv\Scripts\python run.py` after `.venv\Scripts\pip install -r requirements.txt`.
- *`python` is not recognised:* reinstall Python with "Add python.exe to PATH" ticked, then open a new terminal.
- *Port 8000 is busy:* run `PORT=8001 python run.py` (Mac/Linux) or `$env:PORT=8001; python run.py` (PowerShell).

`run.bat` (Windows) and `run.sh` (Mac/Linux) still work as one-click alternatives.

### Optional: real AI diagnosis later

If you get an OpenAI API key, put it in the `.env` file (created on first run) as `OPENAI_API_KEY=...` and restart. Netra then names the crop and disease and gives a full treatment plan. Remove the key to go back to offline mode.

## Layout

```
run.py                   start the server: python run.py
frontend/index.html      the web app (served at /ui)
app/main.py              FastAPI app, CORS, static files
app/routes/analyse.py    POST /analyse, POST /analyse/batch
app/routes/analyses.py   GET/DELETE /analyses
app/services/vision.py   OpenAI call and JSON parsing
app/services/offline.py  keyless colour-based leaf check
app/services/image.py    validation, EXIF rotation, resizing
app/services/storage.py  SQLite history + uploads folder
samples/                 test leaf photos
```

## API

| Method | Path | What it does |
| --- | --- | --- |
| POST | `/analyse` | Analyse one JPEG/PNG (field `file`, max 15 MB) |
| POST | `/analyse/batch` | Analyse several (field `files`); one failure doesn't stop the rest |
| GET | `/analyses` | List saved analyses, newest first |
| GET | `/analyses/{id}` | One analysis |
| DELETE | `/analyses/{id}` | Delete one analysis and its photo |
| DELETE | `/analyses` | Delete all |
| GET | `/docs` | Interactive API docs |

## Settings (`.env`)

- `OPENAI_API_KEY`: optional. Empty means offline mode. Keep `.env` out of git (it's in `.gitignore`).
- `OPENAI_MODEL`: defaults to `gpt-5.5`.
- `NETRA_OFFLINE`: `1` forces offline mode even if a key is set.

Diagnoses come from an AI model reading a photo. Treat them as a first opinion and confirm with a local agriculture officer before using chemicals.
