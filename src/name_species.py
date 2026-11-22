"""Add scientific names from the GBIF species API to the main per-species table.
Writes results/fronts_main_named.csv."""
import json, urllib.request
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = pd.read_csv(ROOT / "results" / "fronts_main.csv")
def name(k):
    try:
        return json.load(urllib.request.urlopen(f"https://api.gbif.org/v1/species/{int(k)}", timeout=60)).get("canonicalName", str(k))
    except Exception:
        return str(k)
with ThreadPoolExecutor(8) as ex:
    R.insert(1, "species", list(ex.map(name, R.species_key)))
R.sort_values("departure_slope").to_csv(ROOT / "results" / "fronts_main_named.csv", index=False)
print(R.sort_values("departure_slope")[["species", "bands", "arrival_slope", "departure_slope"]].round(2).to_string(index=False))
