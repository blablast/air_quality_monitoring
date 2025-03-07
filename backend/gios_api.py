# file: backend/gios_api.py

import aiohttp
import asyncio
from typing import List, Dict, Any
import logging
from tqdm.asyncio import tqdm
from backend.database import save_to_influxdb
import certifi
import ssl

GIOS_URL = "https://api.gios.gov.pl/pjp-api/rest"
PARAM_MAPPING = {
    "pm10": "pm10",
    "pm2.5": "pm25",
    "no2": "no2",
    "so2": "so2",
    "o3": "o3",
    "co": "co",
    "c6h6": "c6h6"
}


async def fetch_sensors(session: aiohttp.ClientSession, station_id: str) -> List[Dict[str, Any]]:
    try:
        async with session.get(f"{GIOS_URL}/station/sensors/{station_id}") as response:
            if response.status != 200:
                logging.warning(f"Skipping station {station_id}: HTTP {response.status}")
                return []
            return await response.json()
    except Exception as e:
        logging.error(f"Error fetching sensors for station {station_id}: {e}")
        return []


async def fetch_sensor_data(session: aiohttp.ClientSession, sensor: Dict[str, Any]) -> List[Dict[str, Any]]:
    param_code = sensor["param"]["paramCode"].lower()
    if param_code not in PARAM_MAPPING:
        return []
    try:
        async with session.get(f"{GIOS_URL}/data/getData/{sensor['id']}") as response:
            if response.status != 200:
                logging.warning(f"Skipping sensor {sensor['id']}: HTTP {response.status}")
                return []
            sensor_data = await response.json()
            return [
                {
                    "station_id": str(sensor["stationId"]),
                    "timestamp": value["date"],
                    PARAM_MAPPING[param_code]: value["value"]
                }
                for value in sensor_data.get("values", [])
                if value["value"] is not None
            ]
    except Exception as e:
        logging.error(f"Error fetching data for sensor {sensor['id']}: {e}")
        return []


async def fetch_gios_data() -> List[Dict[str, Any]]:
    """Fetch air quality data from GIOŚ API using parallel requests with progress bars."""
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")  # Lower security level to match older setups
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
        try:
            async with session.get(f"{GIOS_URL}/station/findAll") as response:
                if response.status != 200:
                    logging.error(f"Failed to fetch stations: {response.status}")
                    return []
                stations = await response.json()
        except Exception as e:
            logging.error(f"Error fetching stations: {e}")
            return []

        sensor_tasks = [fetch_sensors(session, str(station["id"])) for station in stations]
        sensors_per_station = []
        with tqdm(total=len(sensor_tasks), desc="Fetching sensors") as pbar:
            for future in asyncio.as_completed(sensor_tasks):
                result = await future
                sensors_per_station.append(result)
                pbar.update(1)

        all_sensors = []
        station_ids = [str(station["id"]) for station in stations]
        for station_id, sensors in zip(station_ids, sensors_per_station):
            if isinstance(sensors, list):
                for sensor in sensors:
                    sensor["stationId"] = station_id
                    all_sensors.append(sensor)

        data_tasks = [fetch_sensor_data(session, sensor) for sensor in all_sensors]
        sensor_data = []
        with tqdm(total=len(data_tasks), desc="Fetching sensor data") as pbar:
            for future in asyncio.as_completed(data_tasks):
                result = await future
                sensor_data.append(result)
                pbar.update(1)

        data = []
        for result in sensor_data:
            if isinstance(result, list):
                data.extend(result)
        return data


async def fetch_and_save() -> None:
    try:
        data = await fetch_gios_data()
        if data:
            save_to_influxdb(data)
        else:
            logging.warning("No data fetched from GIOŚ API")
    except Exception as e:
        logging.error(f"Error in fetch_and_save: {e}")


if __name__ == "__main__":
    asyncio.run(fetch_and_save())