import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Inter-Division Shipping Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("shipping_data.csv")

df = load_data()

st.title("Inter-Division Shipping Dashboard")
st.subheader("Track, analyze, and report on shipments across divisions")

st.sidebar.title("Filters")
status_filter = st.sidebar.multiselect("Status", options=df["Status"].unique(), default=df["Status"].unique())
item_filter = st.sidebar.multiselect("Item", options=df["Item"].unique(), default=df["Item"].unique())
origin_filter = st.sidebar.multiselect("Origin Division", options=sorted(df["Origin"].unique()), default=df["Origin"].unique())

filtered_df = df[
    (df["Status"].isin(status_filter)) &
    (df["Item"].isin(item_filter)) &
    (df["Origin"].isin(origin_filter))
]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Shipments", len(filtered_df))
col2.metric("Total Freight Cost", f"${filtered_df['Cost'].sum():,.2f}")
col3.metric("Avg Cost Per Shipment", f"${filtered_df['Cost'].mean():,.2f}")
col4.metric("Delayed Shipments", len(filtered_df[filtered_df["Status"] == "Delayed"]))

st.markdown("---")
st.subheader("Shipment Map")

fig = go.Figure()

for _, row in filtered_df.iterrows():
    color = "green" if row["Status"] == "Delivered" else "orange" if row["Status"] == "In Transit" else "red"
    fig.add_trace(go.Scattergeo(
        lon=[row["Origin_Lon"], row["Destination_Lon"]],
        lat=[row["Origin_Lat"], row["Destination_Lat"]],
        mode="lines",
        line=dict(width=1, color=color),
        opacity=0.5,
        showlegend=False,
        hoverinfo="skip"
    ))

divisions = {
    "Oklahoma City": (35.4676, -97.5164),
    "Tulsa": (36.1540, -95.9928),
    "Dallas": (32.7767, -96.7970),
    "Denver": (39.7392, -104.9903),
    "Las Vegas": (36.1699, -115.1398),
    "Austin": (30.2672, -97.7431),
    "Houston": (29.7604, -95.3698),
    "Phoenix": (33.4484, -112.0740),
    "Washington DC": (38.9072, -77.0369),
    "Salt Lake City": (40.7608, -111.8910),
    "San Antonio": (29.4241, -98.4936),
}

for division, coords in divisions.items():
    fig.add_trace(go.Scattergeo(
        lon=[coords[1]],
        lat=[coords[0]],
        mode="markers+text",
        marker=dict(size=10, color="blue"),
        text=division,
        textposition="top center",
        name=division,
        showlegend=False
    ))

fig.update_layout(
    geo=dict(
        scope="usa",
        projection_type="albers usa",
        showland=True,
        landcolor="lightgray",
        showlakes=True,
        lakecolor="white"
    ),
    height=500,
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Shipment Details")
st.dataframe(filtered_df[[
    "Freight_Number", "Origin", "Destination", "Item",
    "Quantity", "Cost", "Ship_Date", "Est_Delivery", "Status", "UPS_Tracking"
]].sort_values("Ship_Date", ascending=False), use_container_width=True)