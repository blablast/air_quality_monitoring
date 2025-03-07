#file: frontend/data_fetch.py

import aiohttp
import logging

FASTAPI_URL = "http://localhost:8000"

async def fetch_any(url_suffix, error_msg = "Error fetching data", return_none_on_error=False):
    """Fetch data from FastAPI asynchronously."""
    url = f"{FASTAPI_URL}/{url_suffix}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        logging.error(f"{error_msg}: {e}")
        return None if return_none_on_error else []

async def fetch_influx_stations():
    """Fetch unique station IDs from FastAPI asynchronously."""
    return await fetch_any("stations")

async def fetch_user_stations():
    """Fetch metadata for user stations from FastAPI asynchronously."""
    return await fetch_any("user_stations", "Error fetching user stations")

async def fetch_time_range():
    """Fetch the earliest and latest available timestamp from FastAPI asynchronously."""
    return await fetch_any("time_range", "Error fetching time range", return_none_on_error=True)

async def fetch_air_quality(station_ids=None, start_date=None, end_date=None, aggregation="1h"):
    """Fetch air quality data asynchronously from FastAPI with aggregation."""

    station_params = "&".join([f"station_id={station}" for station in station_ids]) if station_ids else ""
    params = filter(None, [
        station_params,
        f"start_date={start_date}" if start_date else None,
        f"end_date={end_date}" if end_date else None,
        f"aggregation={aggregation}" if aggregation else None
    ])

    return await fetch_any(f"air_quality?{'&'.join(params)}", "Error fetching air quality data")