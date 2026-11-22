import asyncio
import base64
import json
import os
import re

from openai import OpenAI

from services.offline import analyse_offline


class VisionError(Exception):
    """Raised when the vision model can't give a usable diagnosis."""


CROP_ANALYSIS_PROMPT = """
You are an expert agricultural scientist specializing in crop disease detection.
Analyze this image of a crop/plant and provide a detailed disease assessment.

Respond with ONLY a JSON object (no markdown, no code fences) with exactly this structure:

{
"crop_detected": "Name of the crop or plant visible in the image",
"severity": "healthy" or "mild" or "moderate" or "severe" or "critical",
"diseases": [
        {
            "name": "Disease name",
            "confidence": 0.0 to 1.0,
            "description": "Brief description of the disease and visible symptoms"
        }
    ],
"treatments": [
        {
            "treatment_name": "Name of treatment",
            "treatment_type": "organic" or "chemical" or "preventive",
            "instructions": "Step by step treatment instructions",
            "urgency": "immediate" or "within_week" or "seasonal"
        }
    ],
    "overall_health": "One sentence summary of plant health",
    "additional_notes": "Any other observations or recommendations"
}

If the plant is healthy, return an empty "diseases" list and only preventive treatments.
If the image does not show a plant, set "crop_detected" to "No plant detected" and "severity" to "healthy".
"""

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def parse_json(text: str) -> dict:
    """Parse the model's reply, tolerating ```json fences or stray text around the object."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", (text or "").strip(), flags=re.I)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise VisionError("The model did not return a diagnosis. Please try again.")
    try:
        data = json.loads(cleaned[start:end + 1])
    except json.JSONDecodeError:
        raise VisionError("The model returned an unreadable diagnosis. Please try again.")
    if not isinstance(data, dict):
        raise VisionError("The model returned an unexpected diagnosis format.")
    data.setdefault("diseases", [])
    data.setdefault("treatments", [])
    return data


def _api_key() -> str | None:
    key = (os.getenv("OPENAI_API_KEY") or "").strip()
    return None if key in ("", "your-key-here") else key


def _call_model(image_path: str, content_type: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": CROP_ANALYSIS_PROMPT},
                {"type": "input_image", "image_url": f"data:{content_type};base64,{encode_image(image_path)}"},
            ],
        }],
    )
    return response.output_text


async def analyse_image(image_path: str, content_type: str) -> dict:
    """Analyse the image. Uses the OpenAI model when a key is set, otherwise the offline colour check."""
    key = _api_key()
    if not key or os.getenv("NETRA_OFFLINE") == "1":
        return await asyncio.to_thread(analyse_offline, image_path)
    try:
        text = await asyncio.to_thread(_call_model, image_path, content_type, key)
    except Exception as exc:  # network, auth, quota...
        raise VisionError(f"The vision service failed ({type(exc).__name__}). Check your API key and quota, or clear the key to use offline mode.")
    return parse_json(text)
