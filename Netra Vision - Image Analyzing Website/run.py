"""Start Netra Vision:  python run.py   (then open http://localhost:8000)"""
import os

import uvicorn

ROOT = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(ROOT, "app")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"\nNetra is starting. Open http://localhost:{port} in your browser. Press Ctrl+C to stop.\n")
    uvicorn.run("main:app", app_dir=APP_DIR, host="127.0.0.1", port=port, reload=True, reload_dirs=[APP_DIR])
