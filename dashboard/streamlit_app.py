# dashboard/streamlit_app.py

import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Inventory Rebalancing", layout="wide")
st.title("📦 AI-Based Inventory Rebalancing System")

# --- Forecast Section ---
st.header("📈 Forecast Demand")
if st.button("Generate Forecast"):
    response = requests.get("http://localhost:8000/forecast")
    if response.status_code == 200:
        forecast_data = pd.DataFrame(response.json())
        st.success("Forecast generated successfully!")
        st.dataframe(forecast_data)
    else:
        st.error("Failed to generate forecast.")

# --- Transfer Plan Section ---
st.header("♻️ Generate Transfer Plan")
if st.button("Generate Transfer Plan"):
    with st.spinner("Fetching transfer plan from FastAPI..."):
        try:
            response = requests.get("http://localhost:8000/transfer-plan")

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'message' in data:
                    st.warning(data['message'])
                else:
                    df = pd.DataFrame(data)
                    st.success("✅ Transfer Plan Generated")
                    st.dataframe(df)
            else:
                st.error(f"Failed to get transfer plan: {response.status_code}")

        except Exception as e:
            st.error(f"Request failed: {e}")
