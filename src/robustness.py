"""Rerun the front analysis over a grid of settings and over the two halves of the years.
Writes results/robustness.csv."""
import pandas as pd
from pathlib import Path
from fronts import analyze

ROOT = Path(__file__).resolve().parents[1]
rows = []
for counts in ["counts_2015_2025.json", "counts_2015_2020.json", "counts_2021_2025.json"]:
    for th in [0.25, 0.5, 0.75]:
        for wmin in [0.5, 0.7]:
            _, _, s = analyze(ROOT / "data" / counts, th, wmin)
            s["counts_file"] = counts; rows.append(s)
            print(counts, th, wmin, "n=%d arrival north-first %.2f (p=%.1g) departure south-first %.2f (p=%.2g)" % (
                s["species_with_front"], s["share_arriving_north_first"], s["arrival_sign_test_p"],
                s["share_leaving_south_first"], s["departure_sign_test_p"]), flush=True)
pd.DataFrame(rows).round(4).to_csv(ROOT / "results" / "robustness.csv", index=False)
