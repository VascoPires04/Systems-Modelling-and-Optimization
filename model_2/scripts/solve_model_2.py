# model_2/scripts/solve_model_2.py

import sys
import time
import math
import json
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
from pathlib import Path

use_warm = False
budget_override = None
eta_override = None

if len(sys.argv) > 1:
    use_warm = sys.argv[1].lower() == "true"

if len(sys.argv) > 2:
    budget_override = float(sys.argv[2])

if len(sys.argv) > 3:
    eta_override = float(sys.argv[3])

repo_root = Path(__file__).resolve().parents[2]
model_2_dir = repo_root / "model_2"
config_path = model_2_dir / "config.json"

with open(config_path, "r") as f:
    config = json.load(f)

S = config["S"]
V = config["V"]
theta = config["theta"]
W = config["W"]
eta = eta_override if eta_override is not None else config["eta"]
c = config["c"]
B = budget_override if budget_override is not None else config["B"]

data = repo_root / "data"
results = model_2_dir / "results"
results.mkdir(exist_ok=True)

area = S * V * (1 - theta) * W * eta
R_max = math.sqrt(area / math.pi)


df = pd.read_csv(data / "Dataset_clean.csv")
A = pd.read_csv(data / "distance_matrix.csv", index_col=0)

A.index = A.index.astype(int)
A.columns = A.columns.astype(int)

df["risk"] = pd.to_numeric(df["risk"], errors="coerce").fillna(0.0)

I = A.index.tolist()
J = A.columns.tolist()

risk_map = df.set_index("real_id")["risk"].to_dict()

A = {(i, j): 1 if float(A.loc[i, j]) <= R_max else 0 for i in I for j in J}

m = gp.Model("model_2")
y = m.addVars(J, vtype=GRB.BINARY, name="y")
z = m.addVars(I, vtype=GRB.BINARY, name="z")

m.setObjective(gp.quicksum(float(risk_map.get(i, 0.0)) * z[i] for i in I), GRB.MAXIMIZE)

for i in I:
    m.addConstr(z[i] <= gp.quicksum(A[i, j] * y[j] for j in J), name=f"cover_{i}")

m.addConstr(gp.quicksum(c * y[j] for j in J) <= B, name="budget")

warm_file = results / "model_2_selected_bases.csv"
if use_warm and warm_file.exists():
    prev = pd.read_csv(warm_file)
    chosen_prev = set(prev["real_id"].tolist())
    for j in J:
        y[j].Start = 1 if j in chosen_prev else 0

m.setParam("NodefileStart", 0.5)

best_obj = {"value": None}

def save_incumbent(model, where):
    if where == GRB.Callback.MIPSOL:
        obj = model.cbGet(GRB.Callback.MIPSOL_OBJ)

        if best_obj["value"] is None or obj > best_obj["value"]:
            best_obj["value"] = obj

            vals = model.cbGetSolution([y[j] for j in J])
            chosen = sorted([J[k] for k, v in enumerate(vals) if v > 0.5])

            out = df[df["real_id"].isin(chosen)].copy()
            out["selected"] = 1
            out.to_csv(results / "model_2_selected_bases.csv", index=False)

            print(f"Objective = {obj} | bases = {len(chosen)}")

start = time.time()

if use_warm:
    m.optimize(save_incumbent)
else:
    m.optimize()

elapsed = time.time() - start

chosen = []
covered_ids = []
total_risk = sum(float(risk_map.get(i, 0.0)) for i in I)
covered_risk = 0.0
risk_coverage_ratio = None
risk_coverage_percent = None

if m.SolCount > 0:
    chosen = sorted([j for j in J if y[j].X > 0.5])
    covered_ids = sorted([i for i in I if z[i].X > 0.5])

    covered_risk = sum(float(risk_map.get(i, 0.0)) for i in covered_ids)
    risk_coverage_ratio = covered_risk / total_risk if total_risk > 0 else None
    risk_coverage_percent = 100 * risk_coverage_ratio if risk_coverage_ratio is not None else None

    out = df[df["real_id"].isin(chosen)].copy()
    out["selected"] = 1
    out.to_csv(results / "model_2_selected_bases.csv", index=False)

    covered_df = df[df["real_id"].isin(covered_ids)].copy()
    covered_df["covered"] = 1
    covered_df.to_csv(results / "model_2_covered_points.csv", index=False)

result = {
    "use_warm": use_warm,
    "status": int(m.Status),
    "objective": float(m.ObjVal) if m.SolCount > 0 else None,
    "bases": len(chosen),
    "covered_points": len(covered_ids),
    "total_risk": total_risk,
    "covered_risk": covered_risk,
    "risk_coverage_ratio": risk_coverage_ratio,
    "risk_coverage_percent": risk_coverage_percent,
    "runtime_seconds": elapsed,
    "solution_ids": chosen,
    "covered_ids": covered_ids,
    "R_max": R_max,
    "Autonomy": S,
    "Speed": V,
    "theta": theta,
    "W": W,
    "eta": eta,
    "cost_per_base": c,
    "Budget": B
}

with open(results / "model_2_last_run.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result))