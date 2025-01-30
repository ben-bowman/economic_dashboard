import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json

# --- CONFIG ---
st.set_page_config(page_title="📊 U.S. Economic Dashboard", page_icon="📉", layout="wide")

# --- API KEYS (replace with your own) ---
FRED_API_KEY = "YOUR_FRED_API_KEY"
BLS_API_KEY = "YOUR_BLS_API_KEY"

# --- FUNCTIONS TO FETCH DATA ---
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

@st.cache_data
def fetch_bls_unemployment():
    """Simulated Unemployment Data (Replace with BLS API Calls)"""
    data = {
        "Year": list(range(2000, 2025)),
        "Unemployment Rate": [4.0 + i * 0.1 for i in range(25)]
    }
    return pd.DataFrame(data)

# --- FETCH REAL DATA ---
gdp_df = fetch_fred_data("GDP", 2000, 2024)  # U.S. GDP
cpi_df = fetch_fred_data("CPIAUCSL", 2000, 2024)  # Inflation (CPI)
unemployment_df = fetch_bls_unemployment()

# --- UI COMPONENTS ---
st.title("📊 U.S. Economic Dashboard")
st.markdown("### Explore key economic indicators over time.")

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")
year_range = st.sidebar.slider("Select Year Range", 2000, 2024, (2010, 2024))
indicator = st.sidebar.selectbox("Select Indicator", ["GDP Growth", "Unemployment Rate", "Inflation Rate"])

# --- DATA PROCESSING ---
gdp_df = gdp_df[gdp_df["date"].dt.year.between(year_range[0], year_range[1])]
cpi_df = cpi_df[cpi_df["date"].dt.year.between(year_range[0], year_range[1])]
unemployment_df = unemployment_df[unemployment_df["Year"].between(year_range[0], year_range[1])]

# --- METRIC DISPLAY ---
col1, col2, col3 = st.columns(3)
col1.metric("📈 Avg GDP Growth", f"{gdp_df['value'].pct_change().mean() * 100:.2f}%")
col2.metric("📉 Avg Unemployment", f"{unemployment_df['Unemployment Rate'].mean():.2f}%")
col3.metric("💰 Avg Inflation", f"{cpi_df['value'].pct_change().mean() * 100:.2f}%")

# --- LINE CHARTS ---
st.markdown("### 📊 Economic Indicators Over Time")

if indicator == "GDP Growth":
    fig = px.line(gdp_df, x="date", y="value", title="U.S. GDP Over Time")
elif indicator == "Inflation Rate":
    fig = px.line(cpi_df, x="date", y="value", title="Inflation Rate (CPI) Over Time")
else:
    fig = px.line(unemployment_df, x="Year", y="Unemployment Rate", title="Unemployment Rate Over Time")

st.plotly_chart(fig, use_container_width=True)

# --- TABLE ---
st.markdown("### 📊 Data Table")
if indicator == "GDP Growth":
    st.dataframe(gdp_df.rename(columns={"date": "Year", "value": "GDP"}))
elif indicator == "Inflation Rate":
    st.dataframe(cpi_df.rename(columns={"date": "Year", "value": "CPI"}))
else:
    st.dataframe(unemployment_df)
