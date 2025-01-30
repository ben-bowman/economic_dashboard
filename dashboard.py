import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import json

# --- LOAD API KEYS FROM SECRETS ---
FRED_API_KEY = st.secrets["FRED_API_KEY"]
BLS_API_KEY = st.secrets["BLS_API_KEY"]

# --- SIDEBAR FILTERS ---
st.sidebar.title("🔧 Dashboard Filters")
selected_years = st.sidebar.slider("Select Year Range", 2000, 2024, (2010, 2024))
selected_state_abbrs = st.sidebar.multiselect(
    "Select States for Unemployment Data",
    ['CA', 'TX', 'NY', 'FL', 'IL'],  # Display state abbreviations
    default=["CA", "TX"]  # Default to California and Texas
)

# Convert selected state abbreviations to numeric codes for API call
selected_state_codes = [state_abbreviation_to_code[abbr] for abbr in selected_state_abbrs]

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
    """Fetches state-level unemployment data from BLS API with enhanced debugging."""
    headers = {"Content-Type": "application/json"}
    series = [f"LAU{state_code}0000000000003" for state_code in state_codes]

    data = json.dumps({
        "seriesid": series,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": BLS_API_KEY
    })
    
    response = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", headers=headers, data=data)

    st.subheader("🔍 Debugging: BLS API Response")
    if response.status_code != 200:
        st.error(f"❌ Error fetching unemployment data from BLS API. Status Code: {response.status_code}")
        return pd.DataFrame()
    
    bls_data = response.json()
    
    # Display raw API response for debugging
    st.json(bls_data)

    if "Results" not in bls_data or "series" not in bls_data["Results"]:
        st.error("❌ Unexpected BLS API response format.")
        return pd.DataFrame()
    
    records = []
    for series in bls_data["Results"]["series"]:
        state = series["seriesID"][3:5]  # Extracting state code
        for item in series["data"]:
            records.append({
                "Year": int(item["year"]),
                "State": state_code_map.get(state, state),  # Convert back to state abbreviation
                "Unemployment Rate": float(item["value"])
            })
    
    df = pd.DataFrame(records)

    if df.empty:
        st.warning("⚠️ No unemployment data was retrieved. Check API response above.")
    else:
        st.success("✅ Unemployment data retrieved successfully!")
        st.dataframe(df)  # Show the data in Streamlit

    return df

# --- FETCH DATA ---
gdp_df = fetch_fred_data("GDP", selected_years[0], selected_years[1])
cpi_df = fetch_fred_data("CPIAUCSL", selected_years[0], selected_years[1])
unemployment_df = fetch_bls_unemployment(selected_state_codes, selected_years[0], selected_years[1])

# --- DISPLAY RESULTS ---
st.title("📊 U.S. Economic Dashboard")
st.markdown("### Real-Time Economic Data from FRED & BLS")

# KPI Metrics
col1, col2 = st.columns(2)
if not gdp_df.empty:
    latest_gdp = f"${gdp_df['value'].iloc[-1]:,.2f} B"  # GDP in billions
else:
    latest_gdp = "N/A"
col1.metric("📈 Latest GDP", latest_gdp)

if not cpi_df.empty:
    latest_inflation = f"${cpi_df['value'].iloc[-1]:,.2f}"  # CPI index value as it was before
else:
    latest_inflation = "N/A"
col2.metric("📉 Latest Inflation Index", latest_inflation)

# --- GDP CHART ---
st.subheader("📈 GDP Data (U.S.)")
if not gdp_df.empty:
    fig_gdp = px.line(
        gdp_df, x="date", y="value",
        labels={"value": "GDP ($Billion)", "date": "Year"},
        title="U.S. GDP Over Time"
    )
    st.plotly_chart(fig_gdp, use_container_width=True)
else:
    st.warning("No GDP data available.")

# --- INFLATION CHART ---
st.subheader("📉 Inflation Index (CPI)")
if not cpi_df.empty:
    fig_cpi = px.line(
        cpi_df, x="date", y="value",
        labels={"value": "CPI Index", "date": "Year"},
        title="Inflation Index Over Time"
    )
    st.plotly_chart(fig_cpi, use_container_width=True)
else:
    st.warning("No Inflation data available.")

# --- UNEMPLOYMENT DATA ---
st.subheader("💼 Unemployment Data (Selected States)")
if not unemployment_df.empty:
    fig_unemployment = px.line(
        unemployment_df, x="Year", y="Unemployment Rate", color="State",
        labels={"Unemployment Rate": "Unemployment Rate (%)"},
        title="State-wise Unemployment Rate Over Time"
    )
    st.plotly_chart(fig_unemployment, use_container_width=True)
else:
    st.warning("No unemployment data available.")
