# file: test_user_data.py

import requests
import json
from datetime import datetime, timedelta
import random

# URL Twojego endpointu
url = "http://neurotechai:8000/addUserData"
headers = {"Content-Type" : "application/json"}

# Początkowe losowe wartości w realistycznych zakresach
initial_pm25 = random.uniform(5.0, 50.0)  # PM2.5: typowy zakres 5-50 µg/m³
initial_pm10 = random.uniform(10.0, 100.0)  # PM10: typowy zakres 10-100 µg/m³
initial_no2 = random.uniform(1.0, 40.0)  # NO2: typowy zakres 1-40 µg/m³

# Generowanie danych
base_time = datetime.now()
prev_pm25 = initial_pm25
prev_pm10 = initial_pm10
prev_no2 = initial_no2

for i in range(1) :  # 5 rekordów co godzinę wstecz
    timestamp = (base_time - timedelta(hours = i+20)).isoformat()

    # Losowa modyfikacja wartości w zakresie +/- 0.0-1.0
    pm25 = prev_pm25 + random.uniform(-1.0, 1.0)
    pm10 = prev_pm10 + random.uniform(-1.0, 1.0)
    no2 = prev_no2 + random.uniform(-1.0, 1.0)

    # Upewniamy się, że wartości nie spadną poniżej 0
    pm25 = max(0.0, pm25)
    pm10 = max(0.0, pm10)
    no2 = max(0.0, no2)

    data = {"station_id" : "iot_station_1", "timestamp" : timestamp, "pm25" : round(pm25, 2), "pm10" : round(pm10, 2),
        "no2" : round(no2, 2),"lat": 52.2297, "lon": 21.0122}

    try :
        response = requests.post(url, headers = headers, data = json.dumps(data))
        if response.status_code == 200 :
            print(f"Rekord {i + 1} zapisany: {data}")
        else :
            print(f"Błąd dla rekordu {i + 1}: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e :
        print(f"Wystąpił błąd dla rekordu {i + 1}: {e}")

    # Zaktualizuj poprzednie wartości
    prev_pm25 = pm25
    prev_pm10 = pm10
    prev_no2 = no2