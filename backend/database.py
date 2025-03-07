# file: backend/database.py

import os
import logging
from fastapi import HTTPException
from influxdb_client import InfluxDBClient, Point
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Any

load_dotenv()

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

# Validate environment variables
if not all([INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET]) :
    raise ValueError("Missing required InfluxDB environment variables")

client = InfluxDBClient(url = INFLUXDB_URL, token = INFLUXDB_TOKEN, org = INFLUXDB_ORG)
query_api = client.query_api()
write_api = client.write_api()


def save_to_influxdb(data: List[Dict[str, Any]]) -> None :
    """Save air quality data to InfluxDB."""
    if not data :
        logging.info("No data to save to InfluxDB")
        return

    points = [
        Point("air_quality")
        .tag("station_id", entry["station_id"])
        .time(entry["timestamp"])
        .field(field, float(entry[field]))
        for entry in data
        for field in ["pm25", "pm10", "no2", "so2", "o3", "co", "c6h6"]
        if field in entry and entry[field] is not None
    ]

    if points :
        try :
            write_api.write(bucket = INFLUXDB_BUCKET, record = points)
            logging.info(f"Saved {len(points)} data points to InfluxDB")
        except Exception as e :
            logging.error(f"Error saving data to InfluxDB: {e}")


def get_air_quality(station_ids: List[str] | None = None,
                   start_date: str | None = None,
                   end_date: str | None = None,
                   aggregation: str = "1h") -> List[Dict[str, Any]]:
    """Fetch air quality data with optional filters and aggregation."""
    try :
        start = datetime.strptime(start_date or "2025-01-01", "%Y-%m-%d").date()
        end = datetime.strptime(end_date or datetime.utcnow().strftime("%Y-%m-%d"), "%Y-%m-%d").date()
        if start > end :
            raise HTTPException(status_code = 400, detail = "Invalid date range: start_date must be ≤ end_date")
    except ValueError as e:
        raise HTTPException(status_code = 400, detail = "Invalid date format. Expected YYYY-MM-DD")

    station_filter = ""
    if station_ids :
        conditions = " or ".join([f'r["station_id"] == "{station}"' for station in station_ids])
        station_filter = f"|> filter(fn: (r) => {conditions})"

    query = f'''
            from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: {start}T00:00:00Z, stop: {end}T23:59:59Z)
            |> filter(fn: (r) => r._measurement == "air_quality")
            {station_filter}
            |> aggregateWindow(every: {aggregation}, fn: mean, createEmpty: false)
            |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
            |> yield(name: "mean")
        '''
    try :
        tables = query_api.query(query)
        return [
            {
                "station_id" : record.values["station_id"],
                "timestamp" : record.get_time().isoformat(),
                **{k: v for k, v in record.values.items() if k not in ["result", "table", "_start", "_stop", "_time", "_measurement", "station_id"]}
            }
            for table in tables
            for record in table.records
        ]
    except Exception as e :
        logging.ERROR(f"Error fetching air quality failed: {e}")
        return []


def get_stations() -> List[str] :
    """Fetch unique station IDs from InfluxDB for the last 48 hours."""
    query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -48h)
        |> filter(fn: (r) => r._measurement == "air_quality")
        |> group(columns: ["station_id"])
        |> distinct(column: "station_id")
    '''
    try :
        tables = query_api.query(query)
        return [record["_value"] for table in tables for record in table.records]
    except Exception as e :
        logging.error(f"Error fetching stations from InfluxDB: {e}")
        return []


def get_time_range() -> tuple[str, str] | None:
    """Fetch the earliest and latest timestamps available in InfluxDB."""

    def get_time(desc: str = "false") -> str | None :
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -30d)
        |> filter(fn: (r) => r._measurement == "air_quality")
        |> keep(columns: ["_time"])
        |> group(columns: [])
        |> sort(columns: ["_time"], desc: {desc})
        |> limit(n: 1)
        '''
        tables = query_api.query(query)
        timestamps = [record["_time"] for table in tables for record in table.records]
        return timestamps[0] if timestamps else None

    try :
        min_time = get_time(desc = "false")
        max_time = get_time(desc = "true")
        return (str(min_time), str(max_time)) if min_time and max_time else None

    except Exception as e :
        logging.error(f"Error fetching time range failed: {e}")
        return None
