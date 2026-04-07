import sys
import json
import subprocess
import pandas as pd
from pathlib import Path

n_runs = 10
use_warm = False

if len(sys.argv) > 1:
    n_runs = int(sys.argv[1])

if len(sys.argv) > 2:
    use_warm = sys.argv[2].lower() == "true"

repo_root = Path(__file__).resolve().parents[2]
results = repo_root / "model_1" / "results"
results.mkdir(exist_ok=True)

all_runs = []

for k in range(n_runs):
    print(f"Run {k + 1}/{n_runs}")

    solve_script = Path(__file__).resolve().parent / "solve_model_1.py"
    cmd = ["python3", str(solve_script), str(use_warm).lower()]
    completed = subprocess.run(cmd, capture_output=True, text=True, check=True)

    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    run_result = json.loads(lines[-1])

    run_result["run"] = k + 1
    run_result["solution_signature"] = ",".join(map(str, run_result["solution_ids"]))
    all_runs.append(run_result)

df = pd.DataFrame(all_runs)
df.to_csv(results / "model_1_multiple_runs.csv", index=False)

same_objective = df["objective"].nunique() == 1
same_bases = df["bases"].nunique() == 1
same_solution = df["solution_signature"].nunique() == 1

summary = {
    "n_runs": n_runs,
    "use_warm": use_warm,
    "objective_unique_values": sorted(df["objective"].dropna().unique().tolist()),
    "bases_unique_values": sorted(df["bases"].dropna().unique().tolist()),
    "same_objective_all_runs": same_objective,
    "same_number_of_bases_all_runs": same_bases,
    "same_exact_facility_set_all_runs": same_solution,
    "runtime_mean_seconds": float(df["runtime_seconds"].mean()),
    "runtime_std_seconds": float(df["runtime_seconds"].std(ddof=0)),
    "runtime_min_seconds": float(df["runtime_seconds"].min()),
    "runtime_max_seconds": float(df["runtime_seconds"].max())
}

with open(results / "model_1_multiple_runs_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(json.dumps(summary, indent=2))