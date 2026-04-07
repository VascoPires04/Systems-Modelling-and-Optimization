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
│   ├── config.json
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

### 6. `model_2` — `solve_model_2.py`

This script solves the budget-constrained maximum coverage model, maximizing covered wildfire risk.

Parameters are read from `model_2/config.json`:

- `S` (autonomy in seconds)
- `V` (speed in m/s)
- `theta` (safety margin)
- `W` (effective sensing swath width in meters)
- `eta` (operational efficiency)
- `c` (cost per base)
- `B` (budget)

Coverage radius is computed as:

$$
A = S \cdot V \cdot (1-\theta) \cdot W \cdot \eta, \qquad R_{\max} = \sqrt{\frac{A}{\pi}}
$$

#### Run:
```bash
python3 model_2/scripts/solve_model_2.py
```

#### Optional arguments:
```bash
python3 model_2/scripts/solve_model_2.py <use_warm:true|false> [budget_override] [eta_override]
```

#### Output:
```text
model_2/results/model_2_selected_bases.csv
model_2/results/model_2_covered_points.csv
model_2/results/model_2_last_run.json
```

---

### 7. `model_2` — `generate_model_2_map.py`

This script generates an interactive map with wildfire risk grid, selected bases, and the model_2 coverage radius.

#### Run:
```bash
python3 model_2/scripts/generate_model_2_map.py
```

#### Output:
```text
model_2/results/model_2_map.html
```

---

### 8. `model_2` — `run_model_2_multiple.py`

This script runs `solve_model_2.py` multiple times and summarizes runtime and solution stability.

#### Run:
```bash
python3 model_2/scripts/run_model_2_multiple.py 10 false
```

#### Output:
```text
model_2/results/model_2_multiple_runs.csv
model_2/results/model_2_multiple_runs_summary.json
```

---

### 9. `model_2` — `run_budget_sensitivity.py`

This script evaluates solution quality and selected bases across predefined budget values.

#### Run:
```bash
python3 model_2/scripts/run_budget_sensitivity.py
```

#### Output:
```text
model_2/results/model_2_budget_sensitivity.csv
model_2/results/model_2_budget_sensitivity_summary.json
model_2/results/model_2_budget_vs_risk_coverage.png
model_2/results/model_2_budget_vs_bases.png
```

---

### 10. `model_2` — `run_eta_sensitivity.py`

This script evaluates how `eta` affects `R_max`, covered risk, and selected bases.

#### Run:
```bash
python3 model_2/scripts/run_eta_sensitivity.py
```

#### Output:
```text
model_2/results/model_2_eta_sensitivity.csv
model_2/results/model_2_eta_sensitivity_summary.json
model_2/results/model_2_eta_vs_risk_coverage.png
model_2/results/model_2_eta_vs_rmax.png
```

---

### 11. `model_2` — `find_high_risk_coverage_budget.py`

This script scans budgets and tracks progress in covering points with very high risk (`risk = 5`).

#### Run:
```bash
python3 model_2/scripts/find_high_risk_coverage_budget.py
```

#### Output:
```text
model_2/results/model_2_very_high_risk_coverage_progress.csv
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

```bash
python3 model_2/scripts/solve_model_2.py
python3 model_2/scripts/generate_model_2_map.py
```

Optional (multiple runs):

```bash
python3 model_2/scripts/run_model_2_multiple.py 10 false
```

Optional (sensitivity analyses):

```bash
python3 model_2/scripts/run_budget_sensitivity.py
python3 model_2/scripts/run_eta_sensitivity.py
python3 model_2/scripts/find_high_risk_coverage_budget.py
```

---

## Notes

- The optimization model assumes one drone per base.
- `model_1` uses a baseline full-coverage formulation, while `model_2` uses a budget-constrained maximum coverage formulation.
- For `model_2`, all tunable parameters are centralized in `model_2/config.json`.
- Gurobi must be installed and licensed for both `model_1/scripts/solve_model_1.py` and `model_2/scripts/solve_model_2.py`.