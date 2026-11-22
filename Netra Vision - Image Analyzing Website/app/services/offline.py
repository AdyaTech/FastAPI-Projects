"""Offline leaf check: no API key, no internet, nothing leaves your computer.

It does NOT recognise crops or name diseases with certainty. It measures how much of
the plant-coloured area in the photo is green, yellow or brown/red, and turns that into
a severity estimate plus general advice. A real diagnosis needs the OpenAI model.
"""
from PIL import Image, ImageOps

SIZE = 128


def _fractions(image_path: str) -> dict:
    with Image.open(image_path) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((SIZE, SIZE))
        hsv = im.convert("HSV")
    green = yellow = brown = 0
    pixels = list(hsv.getdata())
    for h, s, v in pixels:
        deg, sat, val = h * 360 / 255, s / 255, v / 255
        if val < 0.12 or sat < 0.18:        # shadow, white, grey background
            continue
        if 65 <= deg <= 170:
            green += 1
        elif 38 <= deg < 65 and sat >= 0.35:
            yellow += 1
        elif deg < 38 or deg >= 300:         # brown, orange, red, purple-red
            brown += 1
        # blue/cyan (sky, water) ignored
    coloured = green + yellow + brown
    return {"green": green, "yellow": yellow, "brown": brown, "coloured": coloured, "total": max(len(pixels), 1)}


def _severity(damage: float) -> str:
    if damage < 0.05: return "healthy"
    if damage < 0.15: return "mild"
    if damage < 0.30: return "moderate"
    if damage < 0.50: return "severe"
    return "critical"


NOTE = ("Offline estimate based on leaf colour only. It cannot identify the crop or confirm a disease. "
        "For a real diagnosis, add an OpenAI key (see README) or show the leaf to a local agriculture officer.")


def analyse_offline(image_path: str) -> dict:
    f = _fractions(image_path)
    base = {"mode": "offline"}
    if f["coloured"] / f["total"] < 0.05 or f["green"] + f["yellow"] + f["brown"] == 0:
        return {**base, "crop_detected": "No clear plant found", "severity": "healthy", "diseases": [], "treatments": [],
                "overall_health": "Not enough leaf colour in this photo to judge anything.",
                "additional_notes": "Try a closer photo in daylight with the leaf filling the frame. " + NOTE}

    c = f["coloured"]
    g, y, b = f["green"] / c, f["yellow"] / c, f["brown"] / c
    damage = y + b
    sev = _severity(damage)
    pct = round(damage * 100)

    diseases = []
    if b >= 0.04:
        diseases.append({"name": "Possible leaf spot or blight (fungal or bacterial)", "confidence": round(min(0.55, 0.2 + b), 2),
                         "description": f"About {round(b * 100)}% of the leaf area is brown, red or dark. Spots and dead patches like this are common with fungal and bacterial leaf diseases, but colour alone can't tell which."})
    if y >= 0.04:
        diseases.append({"name": "Possible yellowing (chlorosis)", "confidence": round(min(0.5, 0.15 + y), 2),
                         "description": f"About {round(y * 100)}% of the leaf area is yellow. It can come from nutrient shortage, too much or too little water, pests or a virus."})
    diseases.sort(key=lambda d: -d["confidence"])

    if sev == "healthy":
        overall = f"The leaf looks mostly green, with about {pct}% discoloured."
        treatments = [
            {"treatment_name": "Keep scouting weekly", "treatment_type": "preventive", "urgency": "seasonal",
             "instructions": "1. Check the undersides of leaves too.\n2. Photograph any new spots and compare next week."},
            {"treatment_name": "Water at the base", "treatment_type": "preventive", "urgency": "seasonal",
             "instructions": "Water the soil rather than the leaves, in the morning, so leaves dry quickly."}]
    else:
        overall = f"About {pct}% of the coloured leaf area looks yellow, brown or red, which suggests {sev} stress."
        treatments = [
            {"treatment_name": "Remove the worst leaves", "treatment_type": "organic",
             "urgency": "immediate" if sev in ("moderate", "severe", "critical") else "within_week",
             "instructions": "1. Cut off badly spotted or yellow leaves.\n2. Bag them and keep them out of the field and compost.\n3. Wipe your cutters with alcohol between plants."},
            {"treatment_name": "Neem oil spray", "treatment_type": "organic", "urgency": "within_week",
             "instructions": "1. Mix as the product label says.\n2. Spray both sides of the leaves in the early morning or evening.\n3. Repeat after 7 to 10 days if new spots appear."},
            {"treatment_name": "Water at the base and space plants", "treatment_type": "preventive", "urgency": "seasonal",
             "instructions": "Water the soil, not the leaves, and leave room between plants for airflow."}]
        if sev in ("severe", "critical"):
            treatments.insert(1, {"treatment_name": "Ask for a matching fungicide", "treatment_type": "chemical", "urgency": "immediate",
                                  "instructions": "Show a leaf to a local agriculture shop or extension officer and use only the product and dose they recommend for your crop."})

    return {**base, "crop_detected": "Plant (not identified)", "severity": sev, "diseases": diseases, "treatments": treatments,
            "overall_health": overall, "additional_notes": NOTE}
