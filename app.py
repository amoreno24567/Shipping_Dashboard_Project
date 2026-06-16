import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Inter-Division Shipping Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        .main { background-color: #0f1117; }
        .block-container { padding-top: 2rem; }
        h1, h2, h3 { color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("shipping_data.csv")
    if isinstance(df["Ship_Method"].iloc[0], str) and df["Ship_Method"].iloc[0].endswith(","):
        df["Ship_Method"] = df["Ship_Method"].str.replace(",", "").str.strip()
    return df

df = load_data()

st.title("⚡ Tachyon Performance")
st.markdown("##### Inter-Division Shipping Dashboard | Real-time parts tracking across all divisions")

st.sidebar.title("🔍 Filters")
status_filter = st.sidebar.multiselect("Status", options=df["Status"].unique(), default=df["Status"].unique())
item_filter = st.sidebar.multiselect("Item", options=df["Item"].unique(), default=df["Item"].unique())
origin_filter = st.sidebar.multiselect("Origin Division", options=sorted(df["Origin"].unique()), default=df["Origin"].unique())
method_filter = st.sidebar.multiselect("Ship Method", options=["Air", "Ground"], default=["Air", "Ground"])

filtered_df = df[
    (df["Status"].isin(status_filter)) &
    (df["Item"].isin(item_filter)) &
    (df["Origin"].isin(origin_filter)) &
    (df["Ship_Method"].isin(method_filter))
]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("📦 Total Shipments", len(filtered_df))
col2.metric("💰 Total Freight Cost", f"${filtered_df['Cost'].sum():,.2f}")
col3.metric("📊 Avg Cost Per Shipment", f"${filtered_df['Cost'].mean():,.2f}")
col4.metric("⚠️ Delayed Shipments", len(filtered_df[filtered_df["Status"] == "Delayed"]))
col5.metric("✈️ Air vs 🚚 Ground", f"{len(filtered_df[filtered_df['Ship_Method']=='Air'])} / {len(filtered_df[filtered_df['Ship_Method']=='Ground'])}")

st.markdown("---")

col_legend1, col_legend2, col_legend3, col_legend4, col_legend5 = st.columns(5)
col_legend1.markdown("🟢 Delivered")
col_legend2.markdown("🟠 In Transit")
col_legend3.markdown("🔴 Delayed")
col_legend4.markdown("✈️ Air — Curved Arc")
col_legend5.markdown("🚚 Ground — Straight Line")

st.subheader("🗺️ Shipment Routes Map")

def status_color(row):
    if row["Status"] == "Delivered":
        return [0, 255, 100]
    elif row["Status"] == "In Transit":
        return [255, 165, 0]
    else:
        return [255, 50, 50]

arc_data = filtered_df.copy()
arc_data["color"] = arc_data.apply(status_color, axis=1)
arc_data = arc_data.rename(columns={
    "Origin_Lon": "origin_lon",
    "Origin_Lat": "origin_lat",
    "Destination_Lon": "dest_lon",
    "Destination_Lat": "dest_lat",
})

air_df = arc_data[arc_data["Ship_Method"] == "Air"]
ground_df = arc_data[arc_data["Ship_Method"] == "Ground"]

divisions = {
    "Oklahoma City": {"lat": 35.4676, "lon": -97.5164},
    "Tulsa": {"lat": 36.1540, "lon": -95.9928},
    "Dallas": {"lat": 32.7767, "lon": -96.7970},
    "Denver": {"lat": 39.7392, "lon": -104.9903},
    "Las Vegas": {"lat": 36.1699, "lon": -115.1398},
    "Austin": {"lat": 30.2672, "lon": -97.7431},
    "Houston": {"lat": 29.7604, "lon": -95.3698},
    "Phoenix": {"lat": 33.4484, "lon": -112.0740},
    "Washington DC": {"lat": 38.9072, "lon": -77.0369},
    "Salt Lake City": {"lat": 40.7608, "lon": -111.8910},
    "San Antonio": {"lat": 29.4241, "lon": -98.4936},
}

icon_data = pd.DataFrame([
    {
        "name": name,
        "lat": coords["lat"],
        "lon": coords["lon"],
        "icon_data": {
            "url": "https://cdn-icons-png.flaticon.com/512/1483/1483336.png",
            "width": 128,
            "height": 128,
            "anchorY": 128
        }
    }
    for name, coords in divisions.items()
])

arc_layer = pdk.Layer(
    "ArcLayer",
    data=air_df,
    get_source_position=["origin_lon", "origin_lat"],
    get_target_position=["dest_lon", "dest_lat"],
    get_source_color="color",
    get_target_color="color",
    get_width=2,
    pickable=True,
    auto_highlight=True,
)

line_layer = pdk.Layer(
    "LineLayer",
    data=ground_df,
    get_source_position=["origin_lon", "origin_lat"],
    get_target_position=["dest_lon", "dest_lat"],
    get_color="color",
    get_width=2,
    pickable=True,
    auto_highlight=True,
)

icon_layer = pdk.Layer(
    "IconLayer",
    data=icon_data,
    get_icon="icon_data",
    get_position=["lon", "lat"],
    get_size=4,
    size_scale=10,
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=37.5,
    longitude=-96.0,
    zoom=3.8,
    pitch=0,
)

r = pdk.Deck(
    layers=[arc_layer, line_layer, icon_layer],
    initial_view_state=view_state,
    map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
    tooltip={
        "text": "{name}\nFreight: {Freight_Number}\nFrom: {Origin} → {Destination}\nItem: {Item}\nCost: ${Cost}\nStatus: {Status}\nMethod: {Ship_Method}"
    }
)

st.pydeck_chart(r)

st.markdown("---")
st.subheader("📋 Shipment Details")
st.dataframe(filtered_df[[
    "Freight_Number", "Origin", "Destination", "Item",
    "Quantity", "Shipment Cost", "Ship_Date", "Est_Delivery", "Status", "Ship_Method", "UPS_Tracking"
]].sort_values("Ship_Date", ascending=False), use_container_width=True)

st.markdown("---")
st.caption("Inter-Division Shipping Dashboard | Powered by Streamlit & PyDeck")