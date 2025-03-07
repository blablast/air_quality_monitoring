#file: frontend/utils.py

import pandas as pd


def format_station_data(gios_stations, influx_station_ids, user_stations) :
    """Match GIOŚ stations with InfluxDB station IDs and handle user stations."""
    formatted_stations = {}
    for station_id in influx_station_ids :
        station_id_str = str(station_id)
        if station_id_str in gios_stations :
            formatted_stations[station_id_str] = gios_stations[station_id_str]
    for user_station in user_stations :
        station_id = user_station["station_id"]
        station_id_str = str(station_id)
        formatted_stations[station_id] = {"name" : station_id,  # Use station_id as name per your request
            "lat" : float(user_station.get("lat", 0)), "lon" : float(user_station.get("lon", 0))}
    return formatted_stations


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
