"""Figure: per-band arrival and departure dates relative to each species' all-India mean.
Reads results/bands_main.csv and results/fronts_main.csv. Writes figures/india_fronts.png."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
B = pd.read_csv(ROOT / "results" / "bands_main.csv"); R = pd.read_csv(ROOT / "results" / "fronts_main.csv")
B = B[B.species_key.isin(R.species_key)].copy()
for col in ["arrival_day", "departure_day"]:
    B[col + "_rel"] = B[col] - B.groupby("species_key")[col].transform("mean")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
fig, ax = plt.subplots(figsize=(7.2, 6.4), dpi=200); fig.patch.set_facecolor("#fcfcfb"); ax.set_facecolor("#fcfcfb")
for col, lab, c, mk in [("arrival_day_rel", "Autumn arrival", "#eb6834", "o"), ("departure_day_rel", "Spring departure", "#2a78d6", "s")]:
    g = B.groupby("lat")[col]; lat = np.array(sorted(B.lat.unique())); n = g.size().reindex(lat)
    lat = lat[n.values >= 15]
    med, q1, q3 = g.median().reindex(lat).values, g.quantile(.25).reindex(lat).values, g.quantile(.75).reindex(lat).values
    ax.fill_between(lat, q1, q3, color=c, alpha=0.13, lw=0)
    ax.plot(lat, med, color=c, lw=2, marker=mk, ms=7, mec="#fcfcfb", mew=1.3, label=lab)
    sl = np.polyfit(lat, med, 1)[0]
    ax.text(lat[-1] + 0.4, med[-1], f"{lab}\n{sl:+.1f} days per degree", va="center", fontsize=9.5, color="#0b0b0b")
ax.axhline(0, color="#b9b8b2", lw=1)
ax.set_xlim(8, 40); ax.set_xticks(range(9, 35, 4)); ax.set_xticklabels([f"{x}°N" for x in range(9, 35, 4)])
ax.set_xlabel("Latitude band in India (2° bands, south to north)", color="#52514e")
ax.set_ylabel("Days earlier (−) or later (+) than the species' all-India average", color="#52514e")
ax.grid(color="#e6e5e0", lw=0.8); ax.set_axisbelow(True)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color("#b9b8b2")
ax.tick_params(colors="#52514e"); ax.legend(frameon=False, loc="lower left", fontsize=9.5)
ax.set_title("Winter visitors reach India as a wave from the north,\nbut leave with no consistent north–south order", loc="left", fontsize=13, fontweight="bold", color="#0b0b0b")
fig.text(0.01, 0.01, f"{R.species_key.nunique()} winter-visitor species, eBird records via GBIF, 2015–2025. Date = when a species' share of records crosses\n"
         "half its peak in that band; only bands where it truly winters. Lines: median across species; bands: middle 50%.", fontsize=8, color="#52514e")
fig.tight_layout(rect=(0, 0.05, 1, 1)); fig.savefig(ROOT / "figures" / "india_fronts.png", facecolor=fig.get_facecolor())
print("wrote figure")
