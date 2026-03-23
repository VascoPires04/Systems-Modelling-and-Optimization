# MOS Project — Drone Base Location for Wildfire Surveillance

This project focuses on the strategic placement of drone bases in a high-risk forest area, using optimization models to support wildfire prevention and surveillance.

The study area is discretized into a regular grid, wildfire risk values are assigned to each point using official ICNF data, and optimization models are then used to determine suitable base locations.

---

## Project structure

```text
Project/
├── data/
├── results/
├── scripts/
└── README.md
```

---

## Required input

Place the raw dataset file:

```text
Dataset.csv
```

inside the `data/` folder.

---

## Scripts

### 1. `clean_dataset.py`

This script reads `Dataset.csv`, recenters the projected coordinates, and creates a cleaned version of the dataset.

#### Run:
```bash
python3 scripts/clean_dataset.py
```

#### Output:
```text
data/Dataset_clean.csv
```

---

### 2. `compute_coverage.py`

This script reads `Dataset_clean.csv` and computes:

- the pairwise distance matrix between all points
- the binary coverage matrix based on a predefined radius `R`

#### Run:
```bash
python3 scripts/compute_coverage.py
```

#### Output:
```text
data/distance_matrix.csv
data/coverage_matrix.csv
```

---

### 3. `solve_model_1_gurobi.py`

This script solves the baseline full-coverage model (Set Covering Problem), minimizing the number of drone bases required to cover the entire discretized area.

It uses the `coverage_matrix.csv` file and saves the selected base locations.

#### Run:
```bash
python3 scripts/solve_model_1_gurobi.py
```

#### Output:
```text
results/model_1_selected_bases.csv
```

This file contains the points selected as drone bases.

---

### 4. `generate_model_1_map.py`

This script generates an interactive map showing:

- the wildfire risk distribution over the study area
- the selected drone base locations
- the coverage radius of each base

#### Run:
```bash
python3 scripts/generate_model_1_map.py
```

#### Output:
```text
results/model_1_map.html
```

Open this file in a browser to visualize the results.

---

## Suggested execution order

Run the scripts in the following order:

```bash
python3 scripts/clean_dataset.py
python3 scripts/compute_coverage.py
python3 scripts/solve_model_1_gurobi.py
python3 scripts/generate_model_1_map.py
```

---

## Notes

- The optimization model assumes one drone per base.
- The coverage logic is based on a predefined radius `R`.
- The baseline model focuses only on the strategic full-coverage problem.
- Gurobi must be installed and licensed for `solve_model_1_gurobi.py` to run.