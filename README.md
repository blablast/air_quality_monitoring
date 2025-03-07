# InfluxDB
### Instalacja
```
docker run -d -p 8086:8086 --name influxdb influxdb:latest
```
### Konfiguracja
```
http://localhost:8086/onboarding/0
username: admin
password: InfluxDB
initial organization: AHE
initial bucket: DZB
```
### Ustawienia środowiskowe (```.env```)
```
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=iiDSU4CbkqcjRtVf06koYvOm0kgW9M9kZ0XrSvL5EPZVRsm_gH3TBBq95vjbu5LPobUdS6-eg6P9gqGifmdqDA==
INFLUXDB_ORG=AHE
INFLUXDB_BUCKET=DZB
```

# Struktura projektu
### Podział backendu (FastAPI)
- ```main.py``` – główny plik FastAPI, importujący funkcje z innych modułów.
- ```database.py``` – konfiguracja InfluxDB (połączenie, zapis, odczyt).
- ```gios_api.py``` – funkcje pobierania danych z API GIOŚ.
- ```models.py``` – definicje modeli Pydantic dla walidacji danych.
- ```scheduler.py``` – obsługa harmonogramu pobierania danych (z schedule).
- ```utils.py``` – dodatkowe funkcje pomocnicze.

### Podział frontendu (Streamlit)
- ```app.py``` – główny plik uruchamiający aplikację Streamlit.
- ```data_fetch.py``` – pobieranie danych z FastAPI.
- ```gios_api.py``` – funkcje pobierania danych z API GIOŚ.
- ```ui_elements.py``` – komponenty UI, np. mapa, wykresy, filtry.
- ```utils.py``` – funkcje pomocnicze (np. formatowanie danych).