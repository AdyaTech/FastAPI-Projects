from fastapi import APIRouter, HTTPException, Query

from services.storage import clear_analyses, delete_analysis, get_analysis, list_analyses

router = APIRouter(prefix="/analyses", tags=["History"])


@router.get("")
async def all_analyses(limit: int = Query(100, ge=1, le=500), offset: int = Query(0, ge=0)):
    return {"analyses": list_analyses(limit, offset)}


@router.get("/{analysis_id}")
async def one_analysis(analysis_id: str):
    record = get_analysis(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return record


@router.delete("/{analysis_id}")
async def remove_analysis(analysis_id: str):
    if not delete_analysis(analysis_id):
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"deleted": analysis_id}


@router.delete("")
async def remove_all():
    return {"deleted": clear_analyses()}
