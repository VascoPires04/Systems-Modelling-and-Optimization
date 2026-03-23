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
        5: "#8B0000",
        4: "#FF0000",
        3: "#FFA500",
        2: "#FFD700",
        1: "#008000",
    }.get(r, "#9E9E9E")

def cell_bounds(lat, lon, size_m=500):
    half = size_m / 2
    dlat = half / 111320
    dlon = half / (111320 * math.cos(math.radians(lat)))
    return [[lat - dlat, lon - dlon], [lat + dlat, lon + dlon]]

center_lat = df["lat"].mean()
center_lon = df["lon"].mean()

m = folium.Map(
    location=[center_lat, center_lon],
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
position: fixed; 
bottom: 40px; left: 40px; width: 180px; z-index:9999;
background-color: white; border:2px solid grey; padding: 10px;
font-size:14px;
">
<b>Wildfire risk</b><br>
<div><span style="display:inline-block;width:14px;height:14px;background:#8B0000;"></span> 5 - Very high</div>
<div><span style="display:inline-block;width:14px;height:14px;background:#FF0000;"></span> 4 - High</div>
<div><span style="display:inline-block;width:14px;height:14px;background:#FFA500;"></span> 3 - Medium</div>
<div><span style="display:inline-block;width:14px;height:14px;background:#FFD700;"></span> 2 - Low</div>
<div><span style="display:inline-block;width:14px;height:14px;background:#008000;"></span> 1 - Very low</div>
<div><span style="display:inline-block;width:14px;height:14px;background:#9E9E9E;"></span> Missing</div>
<hr style="margin:6px 0;">
<div><span style="display:inline-block;width:14px;height:14px;border:2px solid black;border-radius:50%;"></span> Base</div>
<div><span style="display:inline-block;width:14px;height:14px;background:rgba(0,0,0,0.08);border:1px solid black;border-radius:50%;"></span> Coverage radius</div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

folium.LayerControl(collapsed=False).add_to(m)

out_file = results / "model_1_map.html"
m.save(out_file)

print(f"Map saved to: {out_file}")