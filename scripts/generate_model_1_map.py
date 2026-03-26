import math
from pathlib import Path

import pandas as pd
import folium

R = 1500
CELL_SIZE = 500

root = Path(__file__).resolve().parent.parent
data = root / "data"
results = root / "results"
results.mkdir(exist_ok=True)

df = pd.read_csv(data / "Dataset_clean.csv")
bases = pd.read_csv(results / "model_1_selected_bases.csv")

df["risk"] = pd.to_numeric(df["risk"], errors="coerce")
bases["risk"] = pd.to_numeric(bases["risk"], errors="coerce")

def risk_color(r):
    if pd.isna(r):
        return "#9E9E9E"
    r = int(r)
    return {
        1: "#579723",  # rgb(87, 151, 35)
        2: "#EBFF2F",  # rgb(235, 255, 47)
        3: "#EE9B00",  # rgb(238, 155, 0)
        4: "#DC0F0F",  # rgb(220, 15, 15)
        5: "#902003",  # rgb(144, 32, 3)
    }.get(r, "#9E9E9E")

def cell_bounds(lat, lon, size_m=500):
    half = size_m / 2
    dlat = half / 111320
    dlon = half / (111320 * math.cos(math.radians(lat)))
    return [[lat - dlat, lon - dlon], [lat + dlat, lon + dlon]]

def lon_offset_for_meters(lat, meters):
    return meters / (111320 * math.cos(math.radians(lat)))

def lat_offset_for_meters(meters):
    return meters / 111320

center_lat = df["lat"].mean()
center_lon = df["lon"].mean()

min_lat = df["lat"].min()
max_lat = df["lat"].max()
min_lon = df["lon"].min()
max_lon = df["lon"].max()

right_margin_m = 2500
legend_lon = max_lon + lon_offset_for_meters(center_lat, right_margin_m)
legend_lat = max_lat - lat_offset_for_meters(800)

m = folium.Map(
    location=[center_lat, center_lon - lon_offset_for_meters(center_lat, 1200)],
    zoom_start=11,
    tiles="OpenStreetMap",
    control_scale=True
)

risk_layer = folium.FeatureGroup(name="Wildfire risk grid", show=True)
coverage_layer = folium.FeatureGroup(name="Coverage radius", show=True)
bases_layer = folium.FeatureGroup(name="Selected bases", show=True)

for _, row in df.dropna(subset=["lat", "lon"]).iterrows():
    bounds = cell_bounds(row["lat"], row["lon"], CELL_SIZE)
    color = risk_color(row["risk"])

    popup = folium.Popup(
        f"""
        <b>Point ID:</b> {int(row['real_id'])}<br>
        <b>Risk:</b> {row['risk']}<br>
        <b>Local coords:</b> ({row['center_x']}, {row['center_y']})<br>
        <b>Lat/Lon:</b> ({row['lat']}, {row['lon']})
        """,
        max_width=250
    )

    folium.Rectangle(
        bounds=bounds,
        color=None,
        weight=0,
        fill=True,
        fill_color=color,
        fill_opacity=0.35,
        popup=popup
    ).add_to(risk_layer)

for _, row in bases.dropna(subset=["lat", "lon"]).iterrows():
    folium.Circle(
        location=[row["lat"], row["lon"]],
        radius=R,
        color="black",
        weight=2,
        fill=True,
        fill_color="black",
        fill_opacity=0.08
    ).add_to(coverage_layer)

    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=4,
        color="black",
        weight=2,
        fill=True,
        fill_color="black",
        fill_opacity=1,
        popup=folium.Popup(
            f"""
            <b>Selected base</b><br>
            <b>ID:</b> {int(row['real_id'])}<br>
            <b>Risk at location:</b> {row['risk']}<br>
            <b>Local coords:</b> ({row['center_x']}, {row['center_y']})<br>
            <b>Lat/Lon:</b> ({row['lat']}, {row['lon']})
            """,
            max_width=250
        )
    ).add_to(bases_layer)

risk_layer.add_to(m)
coverage_layer.add_to(m)
bases_layer.add_to(m)

legend_html = """
<div style="
background-color: white;
border: 2px solid grey;
padding: 10px 12px;
font-size: 14px;
box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
width: 165px;
">
    <div style="font-weight: bold; margin-bottom: 8px;">Wildfire risk</div>
    <div><span style="display:inline-block;width:14px;height:14px;background:#902003;"></span> 5 - Very high</div>
    <div><span style="display:inline-block;width:14px;height:14px;background:#DC0F0F;"></span> 4 - High</div>
    <div><span style="display:inline-block;width:14px;height:14px;background:#EE9B00;"></span> 3 - Medium</div>
    <div><span style="display:inline-block;width:14px;height:14px;background:#EBFF2F;"></span> 2 - Low</div>
    <div><span style="display:inline-block;width:14px;height:14px;background:#579723;"></span> 1 - Very low</div>
    <div><span style="display:inline-block;width:14px;height:14px;background:#9E9E9E;"></span> Missing</div>
    <hr style="margin:8px 0;">
    <div><span style="display:inline-block;width:12px;height:12px;border:2px solid black;border-radius:50%;margin-right:6px;"></span> Base</div>
    <div style="margin-top:4px;"><span style="display:inline-block;width:12px;height:12px;background:rgba(0,0,0,0.08);border:1px solid black;border-radius:50%;margin-right:6px;"></span> Coverage radius</div>
</div>
"""

folium.Marker(
    location=[legend_lat, legend_lon],
    icon=folium.DivIcon(
        icon_size=(180, 220),
        icon_anchor=(0, 0),
        html=legend_html
    )
).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

out_file = results / "model_1_map.html"
m.save(out_file)

print(f"Map saved to: {out_file}")