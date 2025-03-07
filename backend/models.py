#file: backend/models.py

from pydantic import BaseModel, Field
from typing import Optional

class AirQualityData(BaseModel):
    station_id: str = Field(..., description="Unique identifier of the station")
    timestamp: str = Field(..., description="Timestamp in ISO format")
    source: str = Field("gios", description="Source of the data (e.g., 'gios', 'user')")
    pm25: Optional[float] = Field(None, ge=0, description="PM2.5 concentration (µg/m³)")
    pm10: Optional[float] = Field(None, ge=0, description="PM10 concentration (µg/m³)")
    no2: Optional[float] = Field(None, ge=0, description="NO2 concentration (µg/m³)")
    so2: Optional[float] = Field(None, ge=0, description="SO2 concentration (µg/m³)")
    o3: Optional[float] = Field(None, ge=0, description="O3 concentration (µg/m³)")
    co: Optional[float] = Field(None, ge=0, description="CO concentration (mg/m³)")
    c6h6: Optional[float] = Field(None, ge=0, description="C6H6 concentration (µg/m³)")

class UserAirQualityData(AirQualityData):
    """Model for user-submitted air quality data."""
    station_id: str = Field(..., description="User-defined station ID")
    source: str = Field("user", description="Source fixed to 'user' for user data")
    lat: Optional[float] = Field(None, description = "Latitude of the user station")
    lon: Optional[float] = Field(None, description = "Longitude of the user station")