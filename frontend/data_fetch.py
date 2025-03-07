#file: frontend/data_fetch.py

import aiohttp
import logging

FASTAPI_URL = "http://localhost:8000"

async def fetch_influx_stations():
    """Fetch unique station IDs from FastAPI asynchronously."""
    url = f"{FASTAPI_URL}/stations"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        logging.error(f"Error fetching stations: {e}")
        return []

async def fetch_time_range():
    """Fetch the earliest and latest available timestamp from FastAPI asynchronously."""
    url = f"{FASTAPI_URL}/time_range"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
    except aiohttp.ClientError as e:
        logging.error(f"Error fetching time range: {e}")
        return None

async def fetch_air_quality(station_ids=None, start_date=None, end_date=None, aggregation="1h"):
    """Fetch air quality data asynchronously from FastAPI with aggregation."""

    station_params = "&".join([f"station_id={station}" for station in station_ids]) if station_ids else ""
    params = filter(None, [
        station_params,
        f"start_date={start_date}" if start_date else None,
        f"end_date={end_date}" if end_date else None,
        f"aggregation={aggregation}" if aggregation else None
    ])

    url = f"{FASTAPI_URL}/air_quality?{'&'.join(params)}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            logging.error(f"[ERROR] HTTP {response.status}: {await response.text()}")
        except aiohttp.ClientError as e:
            logging.error(f"[ERROR] Network request failed: {e}")

    return []
