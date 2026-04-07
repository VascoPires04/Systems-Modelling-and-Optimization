# model_2/scripts/run_budget_sensitivity.py

import json
import subprocess
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


USE_WARM = False

BUDGETS = [
    700000,
    850000,
    1000000,
    1250000,
    1500000,
    1750000,
    2000000,
    2250000,
    2500000,
    2750000,
    3000000,
]


def main():
    repo_root = Path(__file__).resolve().parents[2]
    scripts_dir = Path(__file__).resolve().parent
    results_dir = repo_root / "model_2" / "results"
    results_dir.mkdir(exist_ok=True)

    solve_script = scripts_dir / "solve_model_2.py"

    all_results = []

    for budget in BUDGETS:
        print(f"Running budget = {budget} €")

        cmd = [
            "python3",
            str(solve_script),
            str(USE_WARM).lower(),
            str(budget),
        ]

        completed = subprocess.run(cmd, capture_output=True, text=True, check=True)

        lines = [line for line in completed.stdout.splitlines() if line.strip()]
        run_result = json.loads(lines[-1])

        all_results.append({
            "budget": budget,
            "cost_per_base": run_result["cost_per_base"],
            "bases": run_result["bases"],
            "covered_points": run_result["covered_points"],
            "risk_coverage_percent": run_result["risk_coverage_percent"],
            "runtime_seconds": run_result["runtime_seconds"],
            "objective": run_result["objective"],
            "solution_ids": ",".join(map(str, run_result["solution_ids"])),
        })

    df = pd.DataFrame(all_results).sort_values("budget")
    df.to_csv(results_dir / "model_2_budget_sensitivity.csv", index=False)

    summary = {
        "budgets": BUDGETS,
        "cost_per_base": float(df["cost_per_base"].iloc[0]),
        "max_risk_coverage_percent": float(df["risk_coverage_percent"].max()),
        "min_risk_coverage_percent": float(df["risk_coverage_percent"].min()),
        "max_bases": int(df["bases"].max()),
        "min_bases": int(df["bases"].min()),
    }

    with open(results_dir / "model_2_budget_sensitivity_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    plt.figure(figsize=(10, 5))
    plt.plot(df["budget"], df["risk_coverage_percent"], marker="o")
    plt.xlabel("Budget (k€)")
    plt.ylabel("Covered wildfire risk (%)")
    plt.title("Budget sensitivity analysis")
    plt.xticks(df["budget"], [f"{int(b/1000)}" for b in df["budget"]], rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(results_dir / "model_2_budget_vs_risk_coverage.png", dpi=300)
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(df["budget"], df["bases"], marker="o")
    plt.xlabel("Budget (k€)")
    plt.ylabel("Selected bases")
    plt.title("Number of bases by budget")
    plt.xticks(df["budget"], [f"{int(b/1000)}" for b in df["budget"]], rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(results_dir / "model_2_budget_vs_bases.png", dpi=300)
    plt.close()

    print("\nSaved:")
    print(results_dir / "model_2_budget_sensitivity.csv")
    print(results_dir / "model_2_budget_sensitivity_summary.json")
    print(results_dir / "model_2_budget_vs_risk_coverage.png")
    print(results_dir / "model_2_budget_vs_bases.png")


if __name__ == "__main__":
    main()