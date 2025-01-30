import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv

# --- LOAD API KEYS ---
load_dotenv()  # Load from .env file
FRED_API_KEY = os.getenv("FRED_API_KEY")
BLS_API_KEY = os.getenv("BLS_API_KEY")

# --- FUNCTION TO FETCH GDP, INFLATION FROM FRED ---
@st.cache_data
def fetch_fred_data(series_id, start_year=2000, end_year=2024):
    """Fetches data from FRED API."""
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": f"{start_year}-01-01",
        "observation_end": f"{end_year}-12-31",
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    df = pd.DataFrame(data["observations"])
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = df["value"].astype(float)
    return df

# --- FUNCTION TO FETCH UNEMPLOYMENT DATA FROM BLS ---
@st.cache_data
def fetch_bls_unemployment(state_codes, start_year=2000, end_year=2024):
    """Fetches state-level unemployment data from BLS API."""
    headers = {"Content-Type": "application/json"}
    series = [f"LAU{state_code}0000000000003" for state_code in state_codes]
    
    data = json.dumps({
        "seriesid": series,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": BLS_API_KEY
    })
    
    response = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", headers=headers, data=data)
    bls_data = response.json()

    records = []
    for series in bls_data["Results"]["series"]:
        state = series["seriesID"][3:5]  # Extracting state code
        for item in series["data"]:
            records.append({
                "Year": int(item["year"]),
                "State": state,
                "Unemployment Rate": float(item["value"])
            })
    return pd.DataFrame(records)

# --- FETCH DATA ---
gdp_df = fetch_fred_data("GDP", 2000, 2024)  # GDP
cpi_df = fetch_fred_data("CPIAUCSL", 2000, 2024)  # Inflation (CPI)
unemployment_df = fetch_bls_unemployment(["06", "48", "36", "12", "17"], 2000, 2024)

# --- DISPLAY RESULTS ---
st.title("📊 U.S. Economic Dashboard")
st.markdown("### Real-Time Economic Data from FRED & BLS")

st.subheader("📈 GDP Data (U.S.)")
st.line_chart(gdp_df.set_index("date")["value"])

st.subheader("📉 Inflation Rate (CPI)")
st.line_chart(cpi_df.set_index("date")["value"])

st.subheader("💼 Unemployment Data (Selected States)")
st.dataframe(unemployment_df)
