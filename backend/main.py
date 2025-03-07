# file : /backend/main.py
import logging

import uvicorn
from fastapi import FastAPI, Query
from contextlib import asynccontextmanager
from typing import List, Optional
from backend.scheduler import run_schedule
from backend.gios_api import fetch_and_save
from backend.models import AirQualityData
from backend.database import get_air_quality, get_stations, get_time_range

@asynccontextmanager
async def lifespan(app: FastAPI) :
    """Initialize scheduler and fetch initial data on startup."""
    run_schedule()
    await fetch_and_save()
    yield


app = FastAPI(
    title = "Air Quality Monitoring - GIOŚ",
    description = "This is a FastAPI application to monitor air quality data from GIOŚ.",
    version = "0.1",
    lifespan = lifespan
)


@app.get("/stations", response_model=List[str])
async def stations():
    """Fetch unique station IDs from the database."""
    return get_stations()


@app.get("/time_range", response_model=tuple[str, str] | None)
async def time_range():
    """Fetch the earliest and latest timestamps available in the database."""
    return get_time_range()


@app.get("/air_quality", response_model=List[AirQualityData])
async def air_quality(
    station_id: Optional[List[str]] = Query(None, description="List of station IDs to filter by"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    aggregation: str = Query("1h", description="Aggregation interval (e.g., 1h, 1d)")
):
    """Fetch air quality data with optional filters and aggregation."""
    return get_air_quality(station_id, start_date, end_date, aggregation)


if __name__ == "__main__" :
    uvicorn.run(app, host = "0.0.0.0", port = 8000, log_level="info")
