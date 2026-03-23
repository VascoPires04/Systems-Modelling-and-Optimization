import pandas as pd
import numpy as np
from pathlib import Path

# =========================
# Global parameter
# =========================
R = 1500  # coverage radius in meters (change later)

# =========================
# Paths
# =========================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

input_file = DATA_DIR / "Dataset_clean.csv"
distance_output = DATA_DIR / "distance_matrix.csv"
coverage_output = DATA_DIR / "coverage_matrix.csv"

# =========================
# Read dataset
# =========================
df = pd.read_csv(input_file)

required_columns = ["real_id", "center_x", "center_y"]
missing = [col for col in required_columns if col not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

coords = df[["center_x", "center_y"]].to_numpy()
point_ids = df["real_id"].tolist()

# =========================
# Distance matrix
# =========================
diff = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
dist_matrix = np.sqrt((diff ** 2).sum(axis=2))

# =========================
# Coverage matrix
# =========================
coverage_matrix = (dist_matrix <= R).astype(int)

# =========================
# Save outputs
# =========================
dist_df = pd.DataFrame(dist_matrix, index=point_ids, columns=point_ids)
cov_df = pd.DataFrame(coverage_matrix, index=point_ids, columns=point_ids)

dist_df.to_csv(distance_output)
cov_df.to_csv(coverage_output)

print(f"Dataset read from: {input_file}")
print(f"Distance matrix saved to: {distance_output}")
print(f"Coverage matrix saved to: {coverage_output}")
print(f"Coverage radius R = {R} meters")