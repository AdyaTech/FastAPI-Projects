"""SQLite-backed history of analyses, plus the uploads folder."""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(APP_DIR, "uploads")
DATA_DIR = os.path.join(APP_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "netra.db")


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    with _conn() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS analyses (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                image_file TEXT NOT NULL,
                content_type TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )"""
        )


def _row(r: sqlite3.Row) -> dict:
    return {
        "id": r["id"],
        "filename": r["filename"],
        "image_url": f"/uploads/{r['image_file']}",
        "content_type": r["content_type"],
        "result": json.loads(r["result"]),
        "created_at": r["created_at"],
    }


def save_analysis(filename: str, image_file: str, content_type: str, result: dict) -> dict:
    analysis_id = uuid.uuid4().hex
    created = datetime.now(timezone.utc).isoformat()
    with _conn() as c:
        c.execute(
            "INSERT INTO analyses VALUES (?,?,?,?,?,?)",
            (analysis_id, filename, image_file, content_type, json.dumps(result), created),
        )
    return get_analysis(analysis_id)


def list_analyses(limit: int = 100, offset: int = 0) -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset)
        ).fetchall()
    return [_row(r) for r in rows]


def get_analysis(analysis_id: str) -> dict | None:
    with _conn() as c:
        r = c.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
    return _row(r) if r else None


def _remove_file(name: str) -> None:
    path = os.path.join(UPLOAD_DIR, os.path.basename(name))
    if os.path.isfile(path):
        os.remove(path)


def delete_analysis(analysis_id: str) -> bool:
    with _conn() as c:
        r = c.execute("SELECT image_file FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        if not r:
            return False
        c.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    _remove_file(r["image_file"])
    return True


def clear_analyses() -> int:
    with _conn() as c:
        files = [r["image_file"] for r in c.execute("SELECT image_file FROM analyses")]
        c.execute("DELETE FROM analyses")
    for f in files:
        _remove_file(f)
    return len(files)
