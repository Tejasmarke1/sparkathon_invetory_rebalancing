import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
forecast_df = pd.read_csv('outputs/forecasts.csv')
inventory_df = pd.read_csv('data/inventory.csv')
transfer_df = pd.read_json('outputs/transfer_plan.json')

# Merge forecast + inventory
merged_df = pd.merge(forecast_df, inventory_df, on=['SKU', 'Zone'])

# -----------------------------
st.title("📦 AI-Based Inventory Rebalancing Dashboard")

# Sidebar filters
sku_list = merged_df['SKU'].unique()
zone_list = merged_df['Zone'].unique()

selected_sku = st.sidebar.selectbox("Select SKU", sku_list)
selected_zone = st.sidebar.selectbox("Select Zone", zone_list)

# Filtered data
filtered = merged_df[
    (merged_df['SKU'] == selected_sku) & 
    (merged_df['Zone'] == selected_zone)
]

st.subheader(f"🔍 Forecast for {selected_sku} in {selected_zone}")
st.write(filtered)

# Inventory Bar Chart
st.subheader("📊 Inventory Health by Zone")
inv_chart = merged_df[merged_df['SKU'] == selected_sku].copy()
inv_chart['Gap'] = inv_chart['Current_Stock'] - inv_chart['Forecast_Quantity']
fig = px.bar(inv_chart, x='Zone', y='Gap', color='Gap', color_continuous_scale='RdYlGn')
st.plotly_chart(fig, use_container_width=True)

# Transfer Plan
st.subheader("♻️ Suggested Transfers")
st.dataframe(transfer_df)

# Optional map display if you have zones.csv with lat-long
# zones_df = pd.read_csv("data/zones.csv")
# st.map(zones_df.rename(columns={"Latitude": "lat", "Longitude": "lon"}))
