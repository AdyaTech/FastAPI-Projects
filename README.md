<h1 align="center">Netra Vision</h1>
<p align="center"><em>Show it a leaf. Get a severity reading and a plan.</em></p>

<p align="center">
  <img src="docs/screenshot.png" alt="Netra Vision showing a leaf photo with a severity gauge, possible issues and a treatment plan" width="860">
</p>

**Netra** (Sanskrit for "eye") is a small web app for checking crop leaves. Drop in a photo and it tells you how serious the damage looks, what the problem might be, and what to do about it, sorted into *do now*, *this week* and *this season*.

It runs on your own computer with no sign-up and **no API key required**. Add an OpenAI key later if you want real AI diagnosis.

## Features

- **Drag-and-drop lens.** Drop one photo or a whole batch. A soft sweep plays while each leaf is read.
- **Severity at a glance.** A five-step gauge from healthy to critical, with a plain-language note on how urgent it is.
- **Possible issues with confidence rings,** each with a short description of the symptoms.
- **Treatment plan by urgency,** tagged organic, chemical or preventive, with numbered steps.
- **Field log.** Every analysis is saved with its photo, so you can reopen, compare or delete it later.
- **Print report and copy summary** for sharing with a local agriculture officer.
- **Calm, readable design** with light and dark modes and reduced-motion support.
- **Private by default.** In offline mode nothing leaves your machine.

## Two modes

| | Offline (default, no key) | AI (with an OpenAI key) |
| --- | --- | --- |
| Setup | None | Add `OPENAI_API_KEY` to `.env` |
| How it works | Measures how much of the leaf is green, yellow or brown | A vision model reads the photo |
| Crop name | Not identified | Identified |
| Diseases | General hints only ("possible leaf spot") | Named, with confidence |
| Best for | Trying it out, a rough first look | A real diagnosis and plan |

The page labels every offline result as a rough estimate, so it never passes itself off as a diagnosis.

## Quick start (VS Code)

You need **Python 3.10+** ([python.org](https://www.python.org/downloads/); on Windows tick *Add python.exe to PATH*) and **VS Code** with the Python extension.

1. Unzip the project and open the `netra-vision` folder in VS Code (**File > Open Folder**).
2. Open a terminal (**Terminal > New Terminal**, or Ctrl+`) and run:

```bash
python -m venv .venv
```

Activate the environment:

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Mac / Linux
source .venv/bin/activate
```

Install and start:

```bash
pip install -r requirements.txt
python run.py
```

3. Open **http://localhost:8000**, drop in a leaf photo (try the ones in `samples/`) and press **Analyse**.

Next time, just open the folder and run `python run.py`. You can also press **F5** in VS Code, or double-click `run.bat` (Windows) / run `./run.sh` (Mac, Linux).

<details>
<summary>Troubleshooting</summary>

- **Scripts are disabled when activating (Windows):** run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal, then activate again.
- **`python` is not recognised:** reinstall Python with *Add python.exe to PATH* ticked and open a new terminal. On Mac/Linux try `python3`.
- **Port 8000 is busy:** `PORT=8001 python run.py` (Mac/Linux) or `$env:PORT=8001; python run.py` (PowerShell).
- **Alternative start command:** `uvicorn main:app --app-dir app --reload`
</details>

## Turn on AI diagnosis (optional)

1. Get an API key from [platform.openai.com](https://platform.openai.com/).
2. Open `.env` (created on first run from `.env.example`) and set `OPENAI_API_KEY=your-key`.
3. Restart the server.

Remove the key to go back to offline mode, or set `NETRA_OFFLINE=1` to force it.

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | empty | Empty means offline mode |
| `OPENAI_MODEL` | `gpt-5.5` | Vision model to use |
| `NETRA_OFFLINE` | `0` | `1` forces offline mode even with a key |
| `PORT` | `8000` | Port used by `run.py` |

Keep `.env` private. It is already in `.gitignore`.

## API

Interactive docs live at `/docs` while the server runs.

| Method | Path | What it does |
| --- | --- | --- |
| `POST` | `/analyse` | Analyse one JPEG/PNG (form field `file`, max 15 MB) |
| `POST` | `/analyse/batch` | Analyse several (field `files`); one bad image doesn't stop the rest |
| `GET` | `/analyses` | List saved analyses, newest first |
| `GET` | `/analyses/{id}` | One analysis |
| `DELETE` | `/analyses/{id}` | Delete one analysis and its photo |
| `DELETE` | `/analyses` | Delete everything |

```bash
curl -F "file=@samples/leaf-1.jpeg" http://localhost:8000/analyse/
```

## Project layout

```
run.py                    start the server: python run.py
frontend/index.html       the web app, served at /ui (no build step)
app/main.py               FastAPI app, CORS, static files
app/routes/analyse.py     POST /analyse, POST /analyse/batch
app/routes/analyses.py    history endpoints
app/services/vision.py    OpenAI call and reply parsing
app/services/offline.py   keyless colour-based leaf check
app/services/image.py     validation, phone-photo rotation, resizing
app/services/storage.py   SQLite history and uploads folder
samples/                  test leaf photos
.vscode/                  F5 launch config and tasks
```

**Built with** FastAPI, Pillow, SQLite and plain HTML, CSS and JavaScript.

## Good to know

- **Not a replacement for an expert.** Results come from software reading a photo. Confirm with a local agriculture officer before applying any chemical.
- **Photos work best** in daylight, with a single leaf filling the frame and the damage in view.
- **JPEG and PNG only**, up to 15 MB each.
- **Your data stays local.** Photos are saved in `app/uploads/` and results in `app/data/netra.db`. In AI mode, photos are sent to OpenAI for analysis.

## Ideas for next steps

- A trained on-device disease model so offline mode can name diseases
- Hindi and other regional language support
- Track the same plant over time to see whether treatment is working

## License

No license is set yet. Add one (for example MIT) before sharing the code publicly.
