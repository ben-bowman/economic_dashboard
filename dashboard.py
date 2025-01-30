import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import json

# --- LOAD API KEYS FROM SECRETS ---
FRED_API_KEY = st.secrets["FRED_API_KEY"]
BLS_API_KEY = st.secrets["BLS_API_KEY"]

# --- Define Full State Mapping ---
state_code_map = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT",
    "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL",
    "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD",
    "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE",
    "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
    "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV",
    "55": "WI", "56": "WY"
}
# Reverse mapping for API calls
state_abbreviation_to_code = {v: k for k, v in state_code_map.items()}

# --- SIDEBAR FILTERS ---
st.sidebar.title("🔧 Dashboard Filters")
selected_years = st.sidebar.slider("Select Year Range", 2000, 2024, (2010, 2024))

# --- State Selection ---
state_options = ["All"] + list(state_abbreviation_to_code.keys())  # Add "All" option
selected_state_abbrs = st.sidebar.multiselect(
    "Select States for Unemployment Data",
    state_options,  # Show full state list + "All"
    default=["All"]  # Default to U.S. overall
)

# Convert selected states to numeric codes for API call
if "All" in selected_state_abbrs:
    selected_state_codes = ["00000"]  # Special code for U.S. overall unemployment
else:
    selected_state_codes = [state_abbreviation_to_code[abbr] for abbr in selected_state_abbrs]

# --- FUNCTION TO FETCH UNEMPLOYMENT DATA FROM BLS ---
@st.cache_data
def fetch_bls_unemployment(state_codes, start_year=2000, end_year=2024):
    """Fetches state-level unemployment data from BLS API with enhanced debugging."""
    headers = {{"Content-Type": "application/json"}}
    series = [f"LAU{{state_code}}0000000000003" for state_code in state_codes]

    data = json.dumps({{
        "seriesid": series,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": BLS_API_KEY
    }})
    
    response = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", headers=headers, data=data)

    st.subheader("🔍 Debugging: BLS API Response")
    if response.status_code != 200:
        st.error(f"❌ Error fetching unemployment data from BLS API. Status Code: {{response.status_code}}")
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
            records.append({{
                "Year": int(item["year"]),
                "State": state_code_map.get(state, state),  # Convert back to state abbreviation
                "Unemployment Rate": float(item["value"])
            }})
    
    df = pd.DataFrame(records)

    if df.empty:
        st.warning("⚠️ No unemployment data was retrieved. Check API response above.")
    else:
        st.success("✅ Unemployment data retrieved successfully!")
        st.dataframe(df)  # Show the data in Streamlit

    return df

# --- FETCH DATA ---
unemployment_df = fetch_bls_unemployment(selected_state_codes, selected_years[0], selected_years[1])

# --- UNEMPLOYMENT DATA ---
st.subheader("💼 Unemployment Data (Selected States)")
if not unemployment_df.empty:
    fig_unemployment = px.line(
        unemployment_df, x="Year", y="Unemployment Rate", color="State",
        labels={{"Unemployment Rate": "Unemployment Rate (%)"}},
        title="State-wise Unemployment Rate Over Time"
    )
    st.plotly_chart(fig_unemployment, use_container_width=True)
else:
    st.warning("No unemployment data available.")
