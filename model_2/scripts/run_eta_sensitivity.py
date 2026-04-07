# model_2/scripts/run_eta_sensitivity.py

import json
import math
import subprocess
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


USE_WARM = False
BUDGET = 850000

ETAS = [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00]

def compute_rmax(S, V, theta, W, eta):
    area = S * V * (1 - theta) * W * eta
    return math.sqrt(area / math.pi)


def main():
    repo_root = Path(__file__).resolve().parents[2]
    scripts_dir = Path(__file__).resolve().parent
    model_2_dir = repo_root / "model_2"
    results_dir = model_2_dir / "results"
    results_dir.mkdir(exist_ok=True)

    config_path = model_2_dir / "config.json"
    solve_script = scripts_dir / "solve_model_2.py"

    with open(config_path, "r") as f:
        config = json.load(f)

    S = config["S"]
    V = config["V"]
    theta = config["theta"]
    W = config["W"]
    c = config["c"]

    all_results = []

    for eta in ETAS:
        print(f"Running eta = {eta}")

        cmd = [
            "python3",
            str(solve_script),
            str(USE_WARM).lower(),
            str(BUDGET),
            str(eta),
        ]

        completed = subprocess.run(cmd, capture_output=True, text=True, check=True)

        lines = [line for line in completed.stdout.splitlines() if line.strip()]
        run_result = json.loads(lines[-1])

        rmax = compute_rmax(S, V, theta, W, eta)

        all_results.append({
            "eta": eta,
            "budget": BUDGET,
            "cost_per_base": c,
            "R_max": rmax,
            "bases": run_result["bases"],
            "covered_points": run_result["covered_points"],
            "risk_coverage_percent": run_result["risk_coverage_percent"],
            "runtime_seconds": run_result["runtime_seconds"],
            "objective": run_result["objective"],
            "solution_ids": ",".join(map(str, run_result["solution_ids"])),
        })

    df = pd.DataFrame(all_results).sort_values("eta")
    df.to_csv(results_dir / "model_2_eta_sensitivity.csv", index=False)

    summary = {
        "budget": BUDGET,
        "cost_per_base": c,
        "etas": ETAS,
        "min_risk_coverage_percent": float(df["risk_coverage_percent"].min()),
        "max_risk_coverage_percent": float(df["risk_coverage_percent"].max()),
        "min_rmax": float(df["R_max"].min()),
        "max_rmax": float(df["R_max"].max()),
    }

    with open(results_dir / "model_2_eta_sensitivity_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    plt.figure(figsize=(8, 5))
    plt.plot(df["eta"], df["risk_coverage_percent"], marker="o")
    plt.xlabel("Efficiency parameter η")
    plt.ylabel("Covered wildfire risk (%)")
    plt.title("Operational parameter sensitivity")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(results_dir / "model_2_eta_vs_risk_coverage.png", dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(df["eta"], df["R_max"], marker="o")
    plt.xlabel("Efficiency parameter η")
    plt.ylabel("Coverage radius R_max (m)")
    plt.title("Coverage radius as a function of η")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(results_dir / "model_2_eta_vs_rmax.png", dpi=300)
    plt.close()

    print("\nSaved:")
    print(results_dir / "model_2_eta_sensitivity.csv")
    print(results_dir / "model_2_eta_sensitivity_summary.json")
    print(results_dir / "model_2_eta_vs_risk_coverage.png")
    print(results_dir / "model_2_eta_vs_rmax.png")


if __name__ == "__main__":
    main()