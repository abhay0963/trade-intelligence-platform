import requests
import pandas as pd
import plotly.express as px
import streamlit as st

# The base URL of your FastAPI server
# Make sure uvicorn is running before starting the dashboard
API_BASE = "http://127.0.0.1:8000"

# --- Page config ---
# This must be the first Streamlit command in the file
st.set_page_config(
    page_title="Trade Intelligence Platform",
    page_icon="🌍",
    layout="wide"
)

# --- Title ---
st.title("🌍 Global Trade Intelligence Platform")
st.markdown("Real-time trade and economic data analytics")

# --- Sidebar ---
# st.sidebar puts things in the left panel
st.sidebar.header("Filters")

# Dropdown to select country
# For now we only have India — more countries come when real API is live
country = st.sidebar.selectbox(
    "Select Country",
    ["India"]
)

# --- Fetch data from FastAPI ---
# This calls your API endpoint and gets the JSON back
@st.cache_data(ttl=300)  # cache result for 5 minutes — avoids hitting API repeatedly
def fetch_gdp(country_name):
    """
    Calls the FastAPI endpoint and returns a DataFrame.
    ttl=300 means: reuse this result for 300 seconds before fetching again.
    """
    try:
        response = requests.get(f"{API_BASE}/api/gdp/{country_name}", timeout=10)
        response.raise_for_status()
        json_data = response.json()

        # Turn the list of records into a DataFrame
        df = pd.DataFrame(json_data["data"])
        df["gdp_usd"] = df["gdp_usd"] / 1e12  # convert to trillions for readability
        df["year"] = df["year"].astype(str)    # year as string for cleaner x-axis
        return df, json_data["country"]

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure uvicorn is running.")
        return None, None

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None, None


# --- Main content ---
df, country_name = fetch_gdp(country)

if df is not None:

    # --- Metric cards at the top ---
    # st.columns splits the page into side-by-side sections
    col1, col2, col3 = st.columns(3)

    latest_gdp  = df.iloc[0]["gdp_usd"]   # first row = most recent year
    earliest_gdp = df.iloc[-1]["gdp_usd"] # last row = oldest year
    growth = ((latest_gdp - earliest_gdp) / earliest_gdp) * 100

    with col1:
        st.metric(
            label="Latest GDP",
            value=f"${latest_gdp:.2f}T"
        )

    with col2:
        st.metric(
            label="GDP in 2018",
            value=f"${earliest_gdp:.2f}T"
        )

    with col3:
        st.metric(
            label="Growth (2018-2023)",
            value=f"{growth:.1f}%"
        )

    st.divider()

    # --- Bar chart ---
    st.subheader(f"📊 GDP Over Time — {country_name}")

    fig = px.bar(
        df,
        x="year",
        y="gdp_usd",
        labels={"year": "Year", "gdp_usd": "GDP (Trillion USD)"},
        color="gdp_usd",               # color bars by value
        color_continuous_scale="teal", # color theme
        text_auto=".2f"                # show value on top of each bar
    )

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",  # transparent background
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Line chart ---
    st.subheader("📈 GDP Trend")

    fig2 = px.line(
        df,
        x="year",
        y="gdp_usd",
        markers=True,   # show dots on each data point
        labels={"year": "Year", "gdp_usd": "GDP (Trillion USD)"}
    )

    fig2.update_traces(line_color="#0ea5e9", line_width=3)
    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)")

    st.plotly_chart(fig2, use_container_width=True)

    # --- Raw data table ---
    st.subheader("📋 Raw Data")
    st.dataframe(
        df.rename(columns={"year": "Year", "gdp_usd": "GDP (Trillion USD)"}),
        use_container_width=True
    )