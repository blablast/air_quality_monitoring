# file: backend/db_export.py

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
query_api = client.query_api()


def export_to_json(output_file: str = "air_quality_export.json") :
    """Export all air quality data from InfluxDB to a JSON file."""
    # Query to fetch all data from the bucket
    query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -10y)
        |> filter(fn: (r) => r._measurement == "air_quality")
        |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
        |> sort(columns: ["_time", "station_id"], desc: false)
    '''
    try :
        tables = query_api.query(query)
        data = []

        for table in tables :
            for record in table.records :
                entry = {"station_id" : record.values["station_id"], "timestamp" : record.get_time().isoformat(),
                    "pm25" : record.values.get("pm25"), "pm10" : record.values.get("pm10"),
                    "no2" : record.values.get("no2"), "so2" : record.values.get("so2"), "o3" : record.values.get("o3"),
                    "co" : record.values.get("co"), "c6h6" : record.values.get("c6h6")}
                data.append(entry)

        # Write to JSON file
        with open(output_file, "w") as f :
            json.dump(data, f, indent = 2)
        logging.info(f"Exported {len(data)} records to {output_file}")
    except Exception as e :
        logging.error(f"Error exporting data: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    export_to_json()