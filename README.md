# MOS Project — Drone Base Location for Wildfire Surveillance

This project focuses on the strategic placement of drone bases in a high-risk forest area, using optimization models to support wildfire prevention and surveillance.

The study area is discretized into a regular grid, wildfire risk values are assigned to each point using official ICNF data, and optimization models are then used to determine suitable base locations.

---

## Project structure

```text
Project/
├── data/
├── scripts/
├── model_1/
│   ├── scripts/
│   └── results/
├── model_2/
│   ├── scripts/
│   └── results/
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

### 3. `model_1` — `solve_model_1.py`

This script solves the baseline full-coverage model (Set Covering Problem), minimizing the number of drone bases required to cover the entire discretized area.

It uses the `coverage_matrix.csv` file and saves the selected base locations.

#### Run:
```bash
python3 model_1/scripts/solve_model_1.py
```

#### Output:
```text
model_1/results/model_1_selected_bases.csv
```

This file contains the points selected as drone bases.

---

### 4. `model_1` — `generate_model_1_map.py`

This script generates an interactive map showing:

- the wildfire risk distribution over the study area
- the selected drone base locations
- the coverage radius of each base

#### Run:
```bash
python3 model_1/scripts/generate_model_1_map.py
```

#### Output:
```text
model_1/results/model_1_map.html
```

Open this file in a browser to visualize the results.

---

### 5. `model_1` — `run_model_1_multiple.py`

This script runs `model_1/scripts/solve_model_1.py` multiple times and summarizes runtime/solution stability.

#### Run:
```bash
python3 model_1/scripts/run_model_1_multiple.py 10 false
```

#### Output:
```text
model_1/results/model_1_multiple_runs.csv
model_1/results/model_1_multiple_runs_summary.json
```

---

## Suggested execution order

### Common preprocessing (shared by all models)

```bash
python3 scripts/clean_dataset.py
python3 scripts/compute_coverage.py
```

### Model 1 pipeline

```bash
python3 model_1/scripts/solve_model_1.py
python3 model_1/scripts/generate_model_1_map.py
```

Optional (multiple runs):

```bash
python3 model_1/scripts/run_model_1_multiple.py 10 false
```

### Model 2 pipeline

`model_2/` is scaffolded but not implemented yet. When added, it should read inputs from `data/` and write outputs to `model_2/results/`.

---

## Notes

- The optimization model assumes one drone per base.
- The coverage logic is based on a predefined radius `R`.
- The baseline model focuses only on the strategic full-coverage problem.
- Gurobi must be installed and licensed for `model_1/scripts/solve_model_1.py` to run.