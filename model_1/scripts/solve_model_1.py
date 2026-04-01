# model_1/scripts/solve_model_1.py

import sys
import time
import json
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
from pathlib import Path

use_warm = False
if len(sys.argv) > 1:
    use_warm = sys.argv[1].lower() == "true"

repo_root = Path(__file__).resolve().parents[2]
data = repo_root / "data"
results = repo_root / "model_1" / "results"
results.mkdir(exist_ok=True)

df = pd.read_csv(data / "Dataset_clean.csv")
A = pd.read_csv(data / "coverage_matrix.csv", index_col=0)

A.index = A.index.astype(int)
A.columns = A.columns.astype(int)

I = A.index.tolist()
J = A.columns.tolist()

m = gp.Model("model_1")
y = m.addVars(J, vtype=GRB.BINARY, name="y")

m.setObjective(gp.quicksum(y[j] for j in J), GRB.MINIMIZE)

for i in I:
    m.addConstr(gp.quicksum(int(A.loc[i, j]) * y[j] for j in J) >= 1, name=f"cover_{i}")

warm_file = results / "model_1_selected_bases.csv"
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

        if best_obj["value"] is None or obj < best_obj["value"]:
            best_obj["value"] = obj

            vals = model.cbGetSolution([y[j] for j in J])
            chosen = sorted([J[k] for k, v in enumerate(vals) if v > 0.5])

            out = df[df["real_id"].isin(chosen)].copy()
            out["selected"] = 1
            out.to_csv(results / "model_1_selected_bases.csv", index=False)

            print(f"\n[checkpoint] incumbent saved | objective = {obj} | bases = {len(chosen)}")

start = time.time()

if use_warm:
    m.optimize(save_incumbent)
else:
    m.optimize()

elapsed = time.time() - start

chosen = []
if m.SolCount > 0:
    chosen = sorted([j for j in J if y[j].X > 0.5])

    out = df[df["real_id"].isin(chosen)].copy()
    out["selected"] = 1
    out.to_csv(results / "model_1_selected_bases.csv", index=False)

result = {
    "use_warm": use_warm,
    "status": int(m.Status),
    "objective": float(m.ObjVal) if m.SolCount > 0 else None,
    "bases": len(chosen),
    "runtime_seconds": elapsed,
    "solution_ids": chosen
}

with open(results / "model_1_last_run.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result))