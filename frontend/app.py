#file: frontend/app.py

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Monitor jakości powietrza", page_icon="🌍", layout="wide")
pd.options.display.float_format = "{:.2f}".format

from frontend.gios_api import fetch_gios_stations
from frontend.data_fetch import fetch_air_quality, fetch_influx_stations, fetch_time_range, fetch_user_stations
from frontend.utils import format_station_data, get_station_names_and_dict, process_air_quality_data
from frontend.ui_elements import display_map, display_charts

# Streamlit UI
st.title("Monitor jakości powietrza")
# Fetch station data
gios_stations = fetch_gios_stations()
influx_station_ids = asyncio.run(fetch_influx_stations())
user_stations = asyncio.run(fetch_user_stations())

timestamp_range = asyncio.run(fetch_time_range())

# Format station data
available_stations = format_station_data(gios_stations, influx_station_ids, user_stations)

# Get station names and mapping
station_names, station_dict = get_station_names_and_dict(available_stations)
station_names.sort()  # Sort stations alphabetically

col1, col2 = st.columns([1, 2])
with col1:
    # Station selection
    selected_stations = st.multiselect("Wybierz stacje", station_names, default = station_names[:1])

    if not selected_stations :
        st.error("Zaznacz proszę przynajmniej jedną stację.")
        st.stop()
    selected_ids = [station_dict[name] for name in selected_stations]

with col2:
    # Display map
    if available_stations :
        station_map_data = [dict(id = station_id, **available_stations[station_id]) for station_id in selected_ids]
        station_df = pd.DataFrame(station_map_data)
        display_map(station_df)

# Intelligent date selection
if timestamp_range:
    min_date, max_date = pd.to_datetime(timestamp_range[0]), pd.to_datetime(timestamp_range[1])

    # Select date range using Streamlit's date input with two columns
    col1, col2, col3 = st.columns([3, 3, 2])
    with col1:
        date_range = st.date_input("Wybierz zakres dat", (min_date.date(), max_date.date()),
                                   min_value=min_date.date(), max_value=max_date.date(), key="date_range")

    # Handle different cases when date_range is not a tuple
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date.date(), max_date.date()  # Default values

    with col2:
        # Ensure end_date is not earlier than start_date
        if end_date < start_date:
            end_date = start_date

    # Dynamic aggregation options
    aggregation_options = {"Godzinowe": "1h"}
    if (end_date - start_date).days >= 1:
        aggregation_options["Dzienne"] = "1d"
    if (end_date - start_date).days >= 7:
        aggregation_options["Tygodniowe"] = "7d"
    if (end_date - start_date).days >= 30:
        aggregation_options["Miesięczne"] = "30d"

    with col3:
        selected_aggregation = st.selectbox("Grupowanie danych", list(aggregation_options.keys()), key="aggregation")

else:
    st.warning("Brak danych.")
    st.stop()


# Fetch data
if selected_ids :
    air_quality_data = asyncio.run(fetch_air_quality(selected_ids, start_date, end_date, aggregation_options[selected_aggregation]))
    if not air_quality_data :
        st.warning("Brak danych dla wybranej stacji.")
else :
    air_quality_data = []

# Data visualization
if air_quality_data :
    df = pd.DataFrame(air_quality_data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["station_name"] = df["station_id"].map(lambda x : available_stations[x]["name"])

    display_charts(df)

# About the author
# st.markdown("---")
# st.subheader("About the Author")
# col1, col2 = st.columns([1, 3])
# with col1:
#     st.image(
#         "https://media.licdn.com/dms/image/v2/D4E03AQE7JnBb64dkPA/profile-displayphoto-shrink_200_200/B4EZVtsmKAHUAY-/0/1741302162624?e=1746662400&v=beta&t=BFSbvrgNMpQ0bvhhxjm1mu-6Iot6zdZ1u_7HTS1hrco")
# with col2:
#     st.markdown("""
#         **Blazej Strus**
#         Data Scientist | Machine Learning Enthusiast
#         Experienced in developing machine learning models and implementing NLP solutions.
#
#         📫 [b.strus@gmail.com](mailto:b.strus@gmail.com)
#         🌐 [LinkedIn](https://www.linkedin.com/in/b%C5%82a%C5%BCej-strus-7716192a/)
#     """)