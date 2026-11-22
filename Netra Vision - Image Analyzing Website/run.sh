#!/usr/bin/env bash
# Starts Netra Vision on Mac/Linux at http://localhost:8000
set -e
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
[ -f .env ] || cp .env.example .env
echo
echo "Netra is starting. Open http://localhost:8000 in your browser."
echo "Press Ctrl+C to stop it."
echo
cd app && uvicorn main:app
