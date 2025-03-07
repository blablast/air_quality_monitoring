# file: backend/db_import.py
import json
import os
import logging
from influxdb_client import InfluxDBClient, Point
from dotenv import load_dotenv
load_dotenv()

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

# Validate environment variables
if not all([INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET]) :
    raise ValueError("Missing required InfluxDB environment variables")

client = InfluxDBClient(url = INFLUXDB_URL, token = INFLUXDB_TOKEN, org = INFLUXDB_ORG)
write_api = client.write_api()

def import_from_json(input_file: str = "air_quality_export.json") :
    """Import air quality data from a JSON file to InfluxDB."""
    try :
        # Read JSON file
        with open(input_file, "r") as f :
            data = json.load(f)

        logging.info(f"Loaded {len(data)} records from {input_file}")

        # Prepare points for InfluxDB
        points = []
        for entry in data :
            point = Point("air_quality").tag("station_id", entry["station_id"]).time(entry["timestamp"])
            for field in ["pm25", "pm10", "no2", "so2", "o3", "co", "c6h6"] :
                if entry[field] is not None :
                    point.field(field, float(entry[field]))
            points.append(point)

        # Write to InfluxDB
        write_api.write(bucket = INFLUXDB_BUCKET, record = points)
        logging.info(f"Imported {len(points)} points to target InfluxDB")
    except Exception as e :
        logging.error(f"Error importing data: {e}")
        raise

if __name__ == "__main__":
    import_from_json()