"""Paleo Studio: upload a doodle, paint it, stamp it, jigsaw it. Fully offline."""
import io, json, random, uuid
from pathlib import Path

import numpy as np
from flask import Flask, jsonify, request, send_file, send_from_directory
from PIL import Image

import ai

ROOT = Path(__file__).parent
app = Flask(__name__, static_folder=str(ROOT / "static"), static_url_path="/static")
(ROOT / "data").mkdir(exist_ok=True)
BOOK = ROOT / "data" / "collection.json"
SESS, TOTAL_STICKERS = {}, 8


def png(arr):
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png", max_age=0)


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/analyze")
def analyze():
    f = request.files.get("file")
    if not f:
        return jsonify(error="no file"), 400
    try:
        im = Image.open(f.stream).convert("RGBA")
    except Exception:
        return jsonify(error="not an image"), 400
    paper = Image.new("RGBA", im.size, "white")
    paper.alpha_composite(im)
    im = paper.convert("RGB")
    s = 600 / max(im.size)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    base = np.asarray(im, dtype=np.uint8)
    labels, n, border, sizes, ink = ai.segment(base)
    sid = uuid.uuid4().hex[:10]
    while len(SESS) >= 20:
        SESS.pop(next(iter(SESS)))
    SESS[sid] = dict(base=base, labels=labels, n=n, border=border, sizes=sizes,
                     adj=ai.adjacency(labels, n), fills={})
    return jsonify(id=sid, w=base.shape[1], h=base.shape[0], info=ai.describe(ink, border, sizes, n))


@app.get("/api/image/<sid>")
def image(sid):
    s = SESS[sid]
    return png(ai.render(s["base"], s["labels"], s["fills"], s["n"]))


@app.post("/api/auto/<sid>")
def auto(sid):
    s, seed = SESS[sid], int(request.json.get("seed", 0))
    s["fills"] = ai.colorize(s["labels"], s["n"], s["border"], s["sizes"], s["adj"], seed)
    return jsonify(theme=ai.theme_name(seed))


@app.post("/api/clear/<sid>")
def clear(sid):
    SESS[sid]["fills"] = {}
    return jsonify(ok=True)


@app.post("/api/fill/<sid>")
def fill(sid):
    s, j = SESS[sid], request.json
    lab = s["labels"]
    h, w = lab.shape
    x, y = min(max(int(j["x"]), 0), w - 1), min(max(int(j["y"]), 0), h - 1)
    c = int(lab[y, x])
    if c == 0:  # tapped the ink line: use the most common region nearby
        near = lab[max(y - 4, 0):y + 5, max(x - 4, 0):x + 5]
        near = near[near > 0]
        c = int(np.bincount(near).argmax()) if near.size else 0
    if c:
        s["fills"][c] = ai.hex2rgb(j["color"])
    return jsonify(ok=bool(c))


def owned():
    return json.loads(BOOK.read_text()) if BOOK.exists() else []


@app.get("/api/stickers")
def stickers():
    return jsonify(owned=owned(), total=TOTAL_STICKERS)


@app.post("/api/stickers/award")
def award():
    have = owned()
    left = [i for i in range(TOTAL_STICKERS) if i not in have]
    if not left:
        return jsonify(new=None, owned=have)
    pick = random.choice(left)
    have.append(pick)
    BOOK.write_text(json.dumps(have))
    return jsonify(new=pick, owned=have)


if __name__ == "__main__":
    print("Paleo Studio running at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000)
