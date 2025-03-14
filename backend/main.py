# file : /backend/scheduler.py

import logging
import uvicorn
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any

from backend.gios_api import fetch_and_save
from backend.scheduler import run_schedule
from backend.models import AirQualityData, UserAirQualityData
from backend.database import get_air_quality, get_stations, get_time_range, save_to_influxdb, save_user_station, \
    get_user_stations

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
async def stations(source: Optional[str] = Query(None, description="Filter stations by source (e.g., 'gios', 'user')")):
    """Fetch unique station IDs from the database."""
    logging.info(f"Fetching stations with source filter: {source}")
    return get_stations(source)

@app.get("/time_range", response_model=tuple[str, str] | None)
async def time_range(source: Optional[str] = Query(None, description="Filter time range by source (e.g., 'gios', 'user')")):
    """Fetch the earliest and latest timestamps available in the database."""
    logging.info(f"Fetching time range with source filter: {source}")
    return get_time_range(source)


@app.get("/air_quality", response_model=List[AirQualityData])
async def air_quality(
    station_id: Optional[List[str]] = Query(None, description="List of station IDs to filter by"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    aggregation: str = Query("1h", description="Aggregation interval (e.g., 1h, 1d)"),
    source: Optional[str] = Query(None, description="Filter by source (e.g., 'gios', 'user')")
):
    """Fetch air quality data with optional filters and aggregation."""

    return get_air_quality(station_id, start_date, end_date, aggregation, source)

@app.post("/addUserData", response_model=UserAirQualityData)
async def add_user_data(data: UserAirQualityData):
    """Add air quality data from a user-defined station and update station metadata if provided."""
    try:
        data_dict = data.model_dump()
        save_to_influxdb([data_dict])
        # Save or update station metadata if lat/lon provided
        if data.lat is not None or data.lon is not None :
            station_data = {"station_id" : data.station_id, "lat" : data.lat, "lon" : data.lon}
            save_user_station(station_data)
        return data
    except Exception as e:
        logging.error(f"Error saving user data: {e}")
        raise HTTPException(status_code=500, detail="Failed to save user data")

@app.get("/user_stations", response_model=List[Dict[str, Any]])
async def user_stations():
    """Fetch metadata for all user stations."""
    return await get_user_stations()

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

if __name__ == "__main__" :
    uvicorn.run(app, host = "0.0.0.0", port = 8000, log_level="info")
