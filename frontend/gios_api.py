#file: frontend/gios_api.py

import logging
import requests
GIOS_API_URL = "https://api.gios.gov.pl/pjp-api/rest/station/findAll"

def fetch_gios_stations() :
    """Fetch station list from GIOŚ API."""
    try:
        response = requests.get(GIOS_API_URL)
        response.raise_for_status()
        stations = response.json()
        return {
            str(station["id"]): {
                "name": station.get("stationName", f"Station {station['id']}"),
                "lat": float(station.get("gegrLat", 0)),
                "lon": float(station.get("gegrLon", 0))
            }
            for station in stations
        }
    except requests.RequestException as e:
        logging.error(f"Error fetching stations from GIOŚ: {e}")
        return {}
