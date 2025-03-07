#file: frontend/ui_elements.py

import streamlit as st
import pandas as pd
import plotly.express as px


def display_map(station_df) :
    """Display a map with station locations."""
    # if there is no column "size" in the DataFrame, add it with a default value of 20
    if "size" not in station_df.columns :
        station_df["size"] = 10

    fig_map = px.scatter_mapbox(
        station_df,
        lat = "lat",
        lon = "lon",
        hover_name = "name",
        size = "size",
        color_discrete_sequence = ["red"],
        zoom = 4.5,
        height = 500,
        title = "Station Locations"
    )
    fig_map.update_layout(
        mapbox_style = "open-street-map",
        margin = {
            "r" : 0,
            "t" : 30,
            "l" : 0,
            "b" : 0
        }
    )

    st.plotly_chart(fig_map)

def display_charts(data_frame) :
    """Display line charts for air quality data."""

    data_frame = data_frame.sort_values(by = "timestamp")

    pollutants = {"co" : "Tlenek węgla (CO)", "pm10" : "Pył zawieszony PM10", "o3" : "Ozon (O₃)",
        "pm25" : "Pył zawieszony PM2.5", "so2" : "Dwutlenek siarki (SO₂)", "no2" : "Dwutlenek azotu (NO₂)",
        "c6h6" : "Benzen (C₆H₆)"}

    for pollutant in pollutants :
        if pollutant in data_frame.columns and data_frame[pollutant].notna().any() :
            fig = px.line(
                data_frame,
                x = "timestamp",
                y = pollutant,
                color = "station_name",
                title = pollutants.get(pollutant, pollutant),
                labels = {
                    "station_name" : "Station",
                    "timestamp" : "Time",
                    pollutant : pollutant.upper()
                }
            )
            fig.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )
            st.plotly_chart(fig)
        else :
            continue
            st.info(f"Brak danych dla: {pollutants.get(pollutant, pollutant)}.")
