# model_2/scripts/check_very_high_risk_coverage_progress.py

import json
import subprocess
from pathlib import Path

import pandas as pd

USE_WARM = False
BUDGETS = list(range(1500000, 3000001, 50000))
VERY_HIGH_RISK_CLASS = 5


def run_model(solve_script, budget):
    cmd = [
        "python3",
        str(solve_script),
        str(USE_WARM).lower(),
        str(budget),
    ]

    completed = subprocess.run(cmd, capture_output=True, text=True, check=True)
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    return json.loads(lines[-1])


def main():
    repo_root = Path(__file__).resolve().parents[2]
    scripts_dir = Path(__file__).resolve().parent
    data_dir = repo_root / "data"
    results_dir = repo_root / "model_2" / "results"
    results_dir.mkdir(exist_ok=True)

    solve_script = scripts_dir / "solve_model_2.py"

    df = pd.read_csv(data_dir / "Dataset_clean.csv")
    df["risk"] = pd.to_numeric(df["risk"], errors="coerce")

    very_high_ids = set(
        df.loc[df["risk"] == VERY_HIGH_RISK_CLASS, "real_id"].astype(int).tolist()
    )

    if not very_high_ids:
        raise ValueError("No points with risk = 5 were found.")

    print(f"Total very high-risk points: {len(very_high_ids)}\n")

    rows = []

    for budget in BUDGETS:
        print(f"Running budget = {budget} €")

        run_result = run_model(solve_script, budget)
        covered_ids = set(run_result["covered_ids"])

        covered_very_high = very_high_ids & covered_ids
        uncovered_very_high = very_high_ids - covered_ids

        row = {
            "budget": budget,
            "bases": run_result["bases"],
            "covered_points": run_result["covered_points"],
            "risk_coverage_percent": run_result["risk_coverage_percent"],
            "covered_very_high_risk_points": len(covered_very_high),
            "total_very_high_risk_points": len(very_high_ids),
            "very_high_risk_coverage_percent": 100 * len(covered_very_high) / len(very_high_ids),
            "all_very_high_risk_covered": len(uncovered_very_high) == 0,
            "uncovered_very_high_risk_ids": ",".join(map(str, sorted(uncovered_very_high))),
        }

        rows.append(row)

    out_df = pd.DataFrame(rows)
    out_csv = results_dir / "model_2_very_high_risk_coverage_progress.csv"
    out_df.to_csv(out_csv, index=False)

    print(f"\nSaved table to: {out_csv}")


if __name__ == "__main__":
    main()