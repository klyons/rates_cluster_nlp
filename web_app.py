import csv
import streamlit as st
import os
import pandas as pd
import datetime
import plotly.graph_objects as go
import requests

# Set page configuration
st.set_page_config(
    page_title="Monthly food price inflation estimates by country",
    page_icon="⬇",
    layout="wide"
)

# Page title
st.title("Bond Yields for Different Countries")

# Caching data for improved performance
@st.cache_data(ttl=3600)
def get_bonds():
    data = pd.read_parquet("data/bonds.parquet")
    return data

@st.cache_data(ttl=3600)
def get_cpi():
    data = pd.read_parquet("data/cpi.parquet")
    return data

@st.cache_data(ttl=3600)
def get_3mnth_rates():
    data = pd.read_parquet("data/three_month_rates.parquet")
    return data


@st.cache_data(ttl=3600)
def get_equities():
    data = pd.read_parquet("data/df_close.parquet")
    return data 

# Loading data and preprocessing
bonds = get_bonds()
bonds.name = "Bonds"
three_mnth_rates = get_3mnth_rates()
three_mnth_rates.name = "three_mnth_rates"
cpi = get_cpi()
cpi.name = "cpi"
#data['date'] = pd.to_datetime(data['date'], format=None)
#data.set_index('date', inplace=True)
#data = data.dropna(axis=0)
datasets = [bonds, three_mnth_rates, cpi]
# Sidebar to select countries
countries = st.sidebar.multiselect(
    "Which country are we looking at?",
    bonds.columns.unique().tolist(),
    default=['usa']
)

# Visualizing selected countries' data
if countries:
    for chart in datasets:
        st.subheader(f'{chart.name}')
        st.line_chart(chart[countries])
        country = countries[0]
    #st.line_chart(three_mnth_rates[countries])
    #st.line_chart(cpi[countries])

def get_cluster(country):
    clusters = pd.read_parquet('quarterly_data/df_2023Q4.parquet')
    value = clusters.loc['usa', 'labels'] 
    filtered_df = clusters[clusters['labels'] == value]
    # Convert filtered DataFrame rows to list
    return(filtered_df.index.tolist())
    
        


def create_country_data(country_list):
    """
    Creates a dictionary containing latitude and longitude for specified countries.

    Args:
        country_list (list): List of country names.

    Returns:
        dict: A dictionary with country names as keys and latitude/longitude as values.
    """
    country_capitals = {
        "argentina": {"capital": "Buenos Aires", "latitude": -34.61, "longitude": -58.37},
        "australia": {"capital": "Canberra", "latitude": -35.31, "longitude": 149.12},
        "brazil": {"capital": "Brasília", "latitude": -15.78, "longitude": -47.92},
        "canada": {"capital": "Ottawa", "latitude": 45.42, "longitude": -75.69},
        "china": {"capital": "Beijing", "latitude": 39.90, "longitude": 116.40},
        "india": {"capital": "New Delhi", "latitude": 28.61, "longitude": 77.23},
        "indonesia": {"capital": "Jakarta", "latitude": -6.21, "longitude": 106.85},
        "italy": {"capital": "Rome", "latitude": 41.89, "longitude": 12.49},
        "japan": {"capital": "Tokyo", "latitude": 35.68, "longitude": 139.76},
        "mexico": {"capital": "Mexico City", "latitude": 19.43, "longitude": -99.13},
        "russia": {"capital": "Moscow", "latitude": 55.75, "longitude": 37.62},
        "saudi arabia": {"capital": "Riyadh", "latitude": 24.71, "longitude": 46.68},
        "south africa": {"capital": "Pretoria", "latitude": -25.75, "longitude": 28.19},
        "south korea": {"capital": "Seoul", "latitude": 37.57, "longitude": 126.98},
        "turkey": {"capital": "Ankara", "latitude": 39.93, "longitude": 32.86},
        "uk": {"capital": "London", "latitude": 51.51, "longitude": -0.13},
        "usa": {"capital": "Washington, D.C.", "latitude": 38.90, "longitude": -77.04},
        "europe": {"capital": "Brussels", "latitude": 50.85, "longitude": 4.35},
    }

    data = []  # Initialize an empty dictionary for storing data

    for country in country_list:
        if country in country_capitals:
            data.append({
                "latitude": float(country_capitals[country]["latitude"]),
                "longitude": float(country_capitals[country]["longitude"])
            })

    return data
    
clusters = get_cluster(country)
country_marker = create_country_data(clusters)


st.header('')
st.map(country_marker, zoom = 1)

equities = get_equities()
if countries:
    st.subheader(f'equities data')
    st.line_chart(equities[countries].pct_change(equities.shape[1]))