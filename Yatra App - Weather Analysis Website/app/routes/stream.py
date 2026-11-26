from fastapi import APIRouter, HTTPException
from services.currency import fetch_currency_rates
from services.places import fetch_places
from services.utils import describe_error, validate_trip
from services.weather import fetch_weather
from model import TravelRequestModel
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import date, datetime
import json

router = APIRouter(
    prefix="/stream",
    tags=["Stream"],
)


def _jsonable(value):
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    return value


def format_sse(data: str, event: str = None) -> str:
    json_data = json.dumps(_jsonable(data))
    return f"data: {json_data}\n\n" if event is None else f"event: {event}\ndata: {json_data}\n\n"

async def stream_generator(travel_request: TravelRequestModel):
    yield format_sse({"message": "Starting travel plan aggregation..."}, event="start")

    steps = [
        ("weather", "Fetching weather data...", "weather_data", lambda: fetch_weather(
            destination=travel_request.destination,
            start_date=travel_request.start_date,
            end_date=travel_request.end_date,
        )),
        ("options", "Fetching travel options...", "places_data", lambda: fetch_places(travel_request.destination)),
        ("currency", "Fetching currency data...", "currency_data", lambda: fetch_currency_rates(travel_request.base_currency)),
    ]
    complete_event = {"weather": "weather_complete", "options": "options_complete", "currency": "currency_complete"}

    for step, message, key, fetch in steps:
        yield format_sse({"message": message}, event=step)
        try:
            data = await fetch()
            yield format_sse({key: data}, event=complete_event[step])
        except Exception as exc:  # keep streaming so the other sections still arrive
            yield format_sse({"step": step, "error": describe_error(exc)}, event="step_error")

    yield format_sse({"message": "Travel plan aggregation complete!"}, event="complete")


@router.post("/plan", response_class=StreamingResponse)
async def stream_travel_plan(travel_request: TravelRequestModel):
    validate_trip(travel_request)

    return StreamingResponse(
        stream_generator(travel_request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
