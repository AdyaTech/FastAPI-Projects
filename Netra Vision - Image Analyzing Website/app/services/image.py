import io
import os

from PIL import Image, ImageOps, UnidentifiedImageError

from services.storage import UPLOAD_DIR

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png"]
MAX_IMAGE_DIMENSION = 2048
MAX_SIZE_MB = 15


def validate_image(content: bytes, content_type: str) -> dict:
    """Validate the uploaded image content and type."""
    if not content_type or not content_type.startswith("image/"):
        return {"is_valid": False, "message": "Invalid image type"}
    if content_type not in ALLOWED_IMAGE_TYPES:
        return {"is_valid": False, "message": "Only JPEG and PNG images are supported"}

    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_SIZE_MB:
        return {"is_valid": False, "message": f"Image size exceeds {MAX_SIZE_MB} MB limit"}

    try:
        with Image.open(io.BytesIO(content)) as image:
            image.verify()
        with Image.open(io.BytesIO(content)) as image:
            width, height = image.size
    except (UnidentifiedImageError, OSError):
        return {"is_valid": False, "message": "The file is not a readable image"}

    return {"is_valid": True, "message": "Image is valid", "width": width, "height": height, "size_mb": size_mb}


def resize_image_if_needed(content: bytes) -> bytes:
    """Fix phone-photo rotation and shrink the longest side to MAX_IMAGE_DIMENSION."""
    with Image.open(io.BytesIO(content)) as opened:
        fmt = opened.format or "JPEG"
        image = ImageOps.exif_transpose(opened)
        width, height = image.size
        if max(width, height) <= MAX_IMAGE_DIMENSION:
            if image is opened:
                return content
            resized = image
        else:
            scale = MAX_IMAGE_DIMENSION / max(width, height)
            resized = image.resize((int(width * scale), int(height * scale)), Image.LANCZOS)
        if fmt == "JPEG" and resized.mode != "RGB":
            resized = resized.convert("RGB")
        out = io.BytesIO()
        resized.save(out, format=fmt)
        return out.getvalue()


def save_image(content: bytes, upload_path: str | None, filename: str) -> str:
    """Save the image to disk and return its path."""
    folder = upload_path or UPLOAD_DIR
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path
