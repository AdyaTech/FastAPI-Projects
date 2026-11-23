# 🦖 Paleo Studio

**A doodle laboratory that runs entirely on your computer.** Upload a drawing, watch it colour itself, stamp it with dino shapes, cut it into a jigsaw, and collect dino stickers as you finish puzzles.

![Paleo Studio screenshot](screenshot.png)

No API keys. No network calls. No model downloads. No CDN assets. Your drawings never leave your machine.

## Features

- **Smart colorize**: one click and your line drawing is painted automatically
- **Tap to paint**: pick an ink and fill any shape yourself
- **Stamps**: 🦖 🐾 🥚 🦴 🌿 in any size
- **Jigsaw**: slice your doodle into a puzzle (grid size suggested for you)
- **Sticker collection**: finish puzzles to earn 8 collectible dino stickers
- **Specimen notes**: shape count, ink coverage, symmetry and a made-up Latin dino name
- **Sound effects** synthesised in the browser (mute any time)

## Quick start

```bash
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000> and click **Use a sample doodle**, or upload your own.

Tip: dark lines on light paper work best, and closed shapes get coloured best.

## How the "AI" works

It's classical computer vision plus simple rules, not machine learning:

1. **Find the ink**: Otsu thresholding separates dark lines from paper.
2. **Find the shapes**: connected-component labelling gives every enclosed area its own ID.
3. **Find the neighbours**: an adjacency map records which shapes touch.
4. **Colour by rules**:
   - big area at the top → sky blue
   - big area at the bottom → grass green
   - background → paper
   - everything else → one of four themes (Lagoon, Ember, Tundra, Orchard), with graph colouring so touching shapes never share a colour
5. **Describe the doodle**: counts shapes, measures mirror symmetry, and hashes the pixels into a deterministic dino name (the same drawing always gets the same name).

## Project layout

```
app.py          Flask routes
ai.py           segmentation, colouring and specimen notes
static/         UI, sound synth, stamps, jigsaw
data/           collection.json (your stickers, created on first win)
```

## Tech

Python · Flask · Pillow · NumPy · SciPy · vanilla JavaScript

## Privacy

Everything is processed locally on `127.0.0.1`. Nothing is uploaded anywhere.
