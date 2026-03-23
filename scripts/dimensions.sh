python3 - <<'PY'
import pandas as pd
df = pd.read_csv("data/Dataset_clean.csv")
print("lon:", df["lon"].min(), df["lon"].max())
print("lat:", df["lat"].min(), df["lat"].max())
print("center_x:", df["center_x"].min(), df["center_x"].max())
print("center_y:", df["center_y"].min(), df["center_y"].max())
print("n_points:", len(df))
PY
