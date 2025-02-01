import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
FRED_API_KEY = os.getenv("FRED_API_KEY")
BLS_API_KEY = os.getenv("BLS_API_KEY")

# --- Function to Fetch Data from FRED ---
@st.cache_data
def fetch_fred_data(series_id, start_year, end_year):
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": f"{start_year}-01-01",
        "observation_end": f"{end_year}-12-31",
        "frequency": "a"
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if "observations" not in data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data["observations"])
    df["Year"] = pd.to_datetime(df["date"]).dt.year
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"])
    df = df.groupby("Year", as_index=False)["value"].mean()
    df.rename(columns={"value": series_id}, inplace=True)
    return df

# --- Function to Fetch National Unemployment Data from BLS ---
@st.cache_data
def fetch_bls_unemployment(start_year, end_year):
    headers = {"Content-Type": "application/json"}
    series = ["LNS14000000"]
    
    all_records = []
    for y in range(start_year, end_year+1):
        
        data = json.dumps({
            "seriesid": ['LNS14000000'],
            "startyear": str(y),
            "endyear": str(y),
            "registrationkey": BLS_API_KEY
        })
        
        response = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
        response_json = response.json()
        unemployment_rates = [
            float(entry["value"]) for series in response_json["Results"]["series"]
            for entry in series["data"] if "value" in entry
        ]
        # Compute average
        avg_unemployment = sum(unemployment_rates) / len(unemployment_rates) if unemployment_rates else 0
 
        all_records.append({
            "Year": int(y),
            "Unemployment Rate": float(avg_unemployment)
                })
    
    df = pd.DataFrame(all_records)
    return(df)

# --- Streamlit UI ---
st.title("\U0001F4CA U.S. Economic Dashboard")
st.write("Real-Time National Economic Data from FRED & BLS")

# --- User Inputs ---
st.sidebar.header("Filters")
selected_years = st.sidebar.slider("Select Year Range", 1950, 2024, (1950, 2024))

show_gdp = st.sidebar.checkbox("Show GDP Growth (%)", value=True)
show_cpi = st.sidebar.checkbox("Show Inflation Rate (%)", value=True)
show_unemployment = st.sidebar.checkbox("Show Unemployment", value=True)
show_recessions = st.sidebar.checkbox("Highlight Recessions", value=True)

# --- Fetch Data ---
gdp_df = fetch_fred_data("GDP", selected_years[0], selected_years[1]) if show_gdp else pd.DataFrame()
cpi_df = fetch_fred_data("CPIAUCSL", selected_years[0], selected_years[1]) if show_cpi else pd.DataFrame()
unemployment_df = fetch_bls_unemployment(selected_years[0], selected_years[1]) if show_unemployment else pd.DataFrame()

# --- Compute GDP Growth ---
if not gdp_df.empty:
    gdp_df["GDP Growth (%)"] = gdp_df["GDP"].pct_change() * 100
    gdp_df.drop(columns=["GDP"], inplace=True)
    gdp_df.ffill()

# --- Compute Inflation Rate ---
if not cpi_df.empty:
    cpi_df["Inflation Rate (%)"] = cpi_df["CPIAUCSL"].pct_change() * 100
    cpi_df.drop(columns=["CPIAUCSL"], inplace=True)
    cpi_df.ffill()

# --- Merge Data ---
merged_df = pd.DataFrame({"Year": range(selected_years[0], selected_years[1] + 1)})
for df in [gdp_df, cpi_df, unemployment_df]:
    if not df.empty:
        merged_df = pd.merge(merged_df, df, on="Year", how="left")

merged_df.ffill()
# --- Display Chart ---
import plotly.express as px
import streamlit as st

# Ensure merged_df is not empty
if not merged_df.empty:
    # Melt the dataframe to get a long-form structure for Plotly
    df_melted = merged_df.melt(id_vars=["Year"], 
                                var_name="Indicator", 
                                value_name="Value")
    
    # Create a line chart using Plotly
    fig = px.line(
        df_melted, 
        x="Year", 
        y="Value", 
        color="Indicator",  # Different colors for each column
        markers=True,
        title="U.S. Economic Trends",
        labels={"Value": "Percentage (%)", "Year": "Year", "Indicator": "Economic Indicator"}
    )
    
    # Display chart in Streamlit
    st.subheader("\U0001F4C8 Economic Trends Over Time")
    st.plotly_chart(fig)

else:
    st.warning("No data available to plot. Try adjusting your year range or enabling more indicators.")

# --- Display Data ---
st.subheader("\U0001F4CA National Economic Data")
if not merged_df.empty:
    st.dataframe(merged_df)
else:
    st.warning("No data selected or available for the chosen years.")
