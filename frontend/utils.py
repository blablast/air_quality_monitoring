#file: frontend/utils.py

import pandas as pd


def format_station_data(gios_stations, influx_station_ids) :
    """Match GIOŚ stations with available InfluxDB station IDs."""
    return {
        str(station_id) : gios_stations.get(str(station_id), {
            "name" : f"Station {station_id}",
            "lat" : 0,
            "lon" : 0
        }) for station_id in influx_station_ids if str(station_id) in gios_stations}


def get_station_names_and_dict(available_stations) :
    """Generate station names and mapping dictionary."""
    station_names = [info["name"] for info in available_stations.values()]
    station_dict = {info["name"] : station_id for station_id, info in available_stations.items()}
    return station_names, station_dict


def process_air_quality_data(air_quality_data, available_stations) :
    """Convert raw air quality data into a structured DataFrame."""
    if not air_quality_data :
        return pd.DataFrame()

    df = pd.DataFrame(air_quality_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["station_name"] = df["station_id"].map(lambda x : available_stations.get(str(x), {}).get("name", "Unknown"))
    df = df.sort_values(by = "timestamp")

    return df
