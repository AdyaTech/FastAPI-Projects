import os
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from services.image import resize_image_if_needed, save_image, validate_image
from services.storage import save_analysis
from services.vision import VisionError, analyse_image as vision_analyse_image

router = APIRouter(prefix="/analyse", tags=["Analyse"])

EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png"}


async def process_single_image(file: UploadFile) -> dict:
    """Validate, store and analyse one image. Returns the saved analysis record."""
    content = await file.read()

    validation = validate_image(content, file.content_type)
    if not validation["is_valid"]:
        raise HTTPException(status_code=400, detail=validation["message"])

    processed = resize_image_if_needed(content)

    # The extension comes from the verified content type, never from the user's filename.
    unique_name = f"{uuid.uuid4().hex}.{EXTENSIONS[file.content_type]}"
    path = save_image(processed, None, unique_name)

    try:
        result = await vision_analyse_image(path, file.content_type)
    except VisionError as exc:
        os.remove(path)
        raise HTTPException(status_code=502, detail=str(exc))

    return save_analysis(file.filename or unique_name, unique_name, file.content_type, result)


@router.post("/batch")
async def analyse_images(files: list[UploadFile] = File(...)):
    """Analyse several images. A failure on one image doesn't stop the others."""
    results = []
    for file in files:
        try:
            record = await process_single_image(file)
            results.append({"filename": file.filename, "status": "ok", "analysis": record})
        except HTTPException as exc:
            results.append({"filename": file.filename, "status": "error", "error": exc.detail})
    ok = sum(1 for r in results if r["status"] == "ok")
    return {"message": f"{ok} of {len(results)} images analysed.", "results": results}


@router.post("/")
async def analyse_image(file: UploadFile = File(...)):
    """Analyse one image for crop disease."""
    record = await process_single_image(file)
    return {
        "id": record["id"],
        "filename": record["filename"],
        "image_url": record["image_url"],
        "created_at": record["created_at"],
        "result": record["result"],
        "content_type": record["content_type"],
        "message": "Image analysed.",
    }
