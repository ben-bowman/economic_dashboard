import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import json  # ✅ Fixed missing import

# --- LOAD API KEYS FROM SECRETS ---
FRED_API_KEY = st.secrets["FRED_API_KEY"]
BLS_API_KEY = st.secrets["BLS_API_KEY"]

# --- FUNCTION TO FETCH GDP, INFLATION FROM FRED ---
@st.cache_data
def fetch_fred_data(series_id, start_year=2000, end_year=2024):
    """Fetches data from FRED API and handles errors."""
    url = f"https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": f"{start_year}-01-01",
        "observation_end": f"{end_year}-12-31",
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        st.error(f"❌ Error fetching {series_id} data from FRED API. Status Code: {response.status_code}")
        return pd.DataFrame()  # Return an empty DataFrame to prevent crashes
    
    data = response.json()

    if "observations" not in data:
        st.error(f"❌ 'observations' key missing in API response for {series_id}.")
        st.json(data)  # Display raw response for debugging
        return pd.DataFrame()
    
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
    
    if response.status_code != 200:
        st.error(f"❌ Error fetching unemployment data from BLS API. Status Code: {response.status_code}")
        return pd.DataFrame()
    
    bls_data = response.json()

    records = []
    for series in bls_data.get("Results", {}).get("series", []):
        state = series["seriesID"][3:5]
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

# --- GDP CHART ---
st.subheader("📈 GDP Data (U.S.)")
if not gdp_df.empty:
    st.line_chart(gdp_df.set_index("date")["value"])
else:
    st.warning("No GDP data available.")

# --- INFLATION CHART ---
st.subheader("📉 Inflation Rate (CPI)")
if not cpi_df.empty:
    st.line_chart(cpi_df.set_index("date")["value"])
else:
    st.warning("No Inflation data available.")

# --- UNEMPLOYMENT DATA ---
st.subheader("💼 Unemployment Data (Selected States)")
if not unemployment_df.empty:
    fig = px.line(
        unemployment_df,
        x="Year",
        y="Unemployment Rate",
        color="State",
        title="State-wise Unemployment Rate Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No unemployment data available.")
