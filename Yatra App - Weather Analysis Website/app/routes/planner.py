import asyncio

from fastapi import APIRouter
from services.cache import cache_stats, clear_cache
from services.currency import fetch_currency_rates
from services.places import fetch_places
from services.utils import describe_error, validate_trip
from services.weather import fetch_weather
from model import TravelRequestModel

router = APIRouter(
    prefix="/plan",
    tags=["Travel Plan"],
)


@router.post("")
async def create_travel_plan(travel_request: TravelRequestModel):
    """Aggregate Weather, Currency, and Places data into a single travel plan."""
    validate_trip(travel_request)

    results = await asyncio.gather(
        fetch_weather(
            destination=travel_request.destination,
            start_date=travel_request.start_date,
            end_date=travel_request.end_date,
        ),
        fetch_places(travel_request.destination),
        fetch_currency_rates(travel_request.base_currency),
        return_exceptions=True,  # one failing service should not sink the whole plan
    )
    names = ("weather_data", "places_data", "currency_rates")
    plan, errors = {}, {}
    for name, result in zip(names, results):
        if isinstance(result, Exception):
            plan[name], errors[name] = None, describe_error(result)
        else:
            plan[name] = result

    return {"message": "Travel plan created successfully", **plan, "errors": errors}


@router.get("/cache-stats")
async def get_cache_stats():
    return cache_stats()


@router.delete("/cache")
async def delete_cache():
    clear_cache()
    return {"message": "Cache cleared"}
