import pandas as pd
from pathlib import Path

# Files
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

input_file = DATA_DIR / "Dataset.csv"
output_file = DATA_DIR / "Dataset_clean.csv"

# Read CSV
df = pd.read_csv(input_file)

# Check required columns
required_columns = ["center_x", "center_y"]
missing = [col for col in required_columns if col not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# Rename risk column if needed
if "risk1" in df.columns and "risk" not in df.columns:
    df = df.rename(columns={"risk1": "risk"})

# Find minima
min_x = df["center_x"].min()
min_y = df["center_y"].min()

# Recenter coordinates directly
df["center_x"] = (df["center_x"] - min_x).round(3)
df["center_y"] = (df["center_y"] - min_y).round(3)

# Optional: reorder columns
preferred_order = ["id", "risk", "center_x", "center_y", "lon", "lat"]
existing_first = [col for col in preferred_order if col in df.columns]
remaining = [col for col in df.columns if col not in existing_first]
df = df[existing_first + remaining]

# Save cleaned file
df.to_csv(output_file, index=False)

print("Dataset cleaned successfully.")
print(f"Output file: {output_file}")
print(f"Original min center_x = {min_x}")
print(f"Original min center_y = {min_y}")