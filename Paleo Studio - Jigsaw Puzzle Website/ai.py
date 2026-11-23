"""Offline 'AI' for Paleo Studio: classical computer vision plus heuristics.
Everything runs locally. No network, no API keys, no model downloads."""
import hashlib
import numpy as np
from scipy import ndimage as ndi

THEMES = {
    "Lagoon":  ["#2F7F6F", "#6BB5A5", "#E9C46A", "#E76F51", "#3D5A80", "#B8C4A9"],
    "Ember":   ["#C8553D", "#F28F3B", "#2D3047", "#93B7BE", "#E0CA3C", "#6B4E71"],
    "Tundra":  ["#3A6EA5", "#9DB4C0", "#E8D9B5", "#5C7457", "#A3445B", "#F2A65A"],
    "Orchard": ["#588157", "#A3B18A", "#DDA15E", "#BC6C25", "#7B2D26", "#3A5A40"],
}
hex2rgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
theme_name = lambda seed: list(THEMES)[seed % len(THEMES)]


def _otsu(gray):
    hist, _ = np.histogram(gray, bins=256, range=(0, 256))
    total, s_all = gray.size, float(np.dot(np.arange(256), hist))
    wb = sb = 0.0
    best, thr = 0.0, 128
    for t in range(256):
        wb += hist[t]
        if wb == 0:
            continue
        wf = total - wb
        if wf == 0:
            break
        sb += t * hist[t]
        between = wb * wf * (sb / wb - (s_all - sb) / wf) ** 2
        if between > best:
            best, thr = between, t
    return min(thr, 170)


def segment(rgb):
    """Find the ink lines, then label every enclosed white area as a region."""
    gray = rgb @ np.array([.299, .587, .114])
    ink = gray < _otsu(gray)
    labels, n = ndi.label(~ink)
    border = set(np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))) - {0}
    sizes = np.bincount(labels.ravel(), minlength=n + 1)
    return labels, n, border, sizes, ink


def adjacency(labels, n):
    """Which regions sit next to each other across an ink line."""
    big = n + 1
    lo = np.where(labels > 0, labels, big)
    mx = ndi.maximum_filter(labels, size=7)
    mn = ndi.minimum_filter(lo, size=7)
    m = (mx > 0) & (mn < big) & (mx != mn)
    adj = {i: set() for i in range(1, n + 1)}
    for a, b in set(zip(mx[m].tolist(), mn[m].tolist())):
        adj[a].add(b)
        adj[b].add(a)
    return adj


def colorize(labels, n, border, sizes, adj, seed=0):
    """Smart colorist: sky and grass by position, background as paper,
    everything else by graph coloring so neighbours never share a color."""
    h, w = labels.shape
    pal = [hex2rgb(c) for c in THEMES[theme_name(seed)]]
    rng = np.random.default_rng(seed)
    ids = [i for i in range(1, n + 1) if sizes[i] >= 20]
    cy = dict(zip(ids, ndi.center_of_mass(np.ones_like(labels), labels, ids)))
    fills = {}
    for i in sorted(ids, key=lambda k: -sizes[k]):
        y = cy[i][0] / h
        if i in border:
            fills[i] = hex2rgb("#F5F2E6")
        elif sizes[i] > .08 * h * w and y < .4:
            fills[i] = hex2rgb("#BFE0EE")
        elif sizes[i] > .08 * h * w and y > .7:
            fills[i] = hex2rgb("#A9CF95")
        else:
            used = {fills[j] for j in adj[i] if j in fills}
            options = [pal[k] for k in rng.permutation(len(pal)) if pal[k] not in used]
            fills[i] = (options or pal)[0]
    return fills


def render(base, labels, fills, n):
    lut = np.full((n + 1, 3), 255, np.float32)
    has = np.zeros(n + 1, bool)
    for i, c in fills.items():
        lut[i], has[i] = c, True
    out = np.where(has[labels][..., None], base * (lut[labels] / 255.0), base)
    return out.astype(np.uint8)


def describe(ink, border, sizes, n):
    """Fun, deterministic 'field notes' about the doodle."""
    shapes = sum(1 for i in range(1, n + 1) if i not in border and sizes[i] > 40)
    mirror = ink[:, ::-1]
    sym = (ink & mirror).sum() / max((ink | mirror).sum(), 1)
    seed = int(hashlib.md5(np.packbits(ink[::4, ::4]).tobytes()).hexdigest()[:8], 16)
    a = ["Doodle", "Scribble", "Squiggle", "Wobble", "Zigzag", "Blotch", "Loop", "Dash"]
    b = ["raptor", "ceratops", "don", "saurus", "dactyl", "mimus"]
    c = ["mirabilis", "fabulosa", "inkorum", "chartae", "vagans", "rex"]
    return dict(
        name=f"{a[seed % 8]}{b[seed // 8 % 6]} {c[seed // 48 % 6]}",
        shapes=int(shapes), ink=float(round(ink.mean() * 100, 1)), symmetry=int(round(sym * 100)),
        grid=3 if shapes < 8 else 4 if shapes < 25 else 5 if shapes < 60 else 6, seed=seed % 1000)
