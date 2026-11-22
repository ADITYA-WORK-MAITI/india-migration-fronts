"""Arrival and departure fronts of winter-visiting bird species across India's latitude bands.

For each species and band, the reporting rate (species records / all records) is smoothed over
10-day periods. Arrival = the day the rate first rises through THRESHOLD x its peak (counting from
1 July); departure = the day it last falls through it. Only bands where the species truly winters
(mid-winter rate >= WINTER_MIN x peak) are used. Per species, dates are regressed on latitude.
Slope in days per degree: negative arrival slope = north first; positive departure slope = south first.

Usage: python3 src/fronts.py COUNTS_JSON THRESHOLD WINTER_MIN TAG
Writes results/fronts_TAG.csv (per species), results/bands_TAG.csv (per species x band), results/summary_TAG.json."""
import json, sys
import numpy as np, pandas as pd
from scipy import stats
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAYS_PER_PERIOD = 365.25 / 36

def period_index(month, day):            # 0..35, starting 1 July
    return ((month - 7) % 12) * 3 + {1: 0, 11: 1, 21: 2}[day]

def smooth(x):                            # circular 3-point moving average
    return (np.roll(x, 1) + x + np.roll(x, -1)) / 3

def crossings(sh, threshold):
    thr = threshold * sh.max(); above = sh >= thr
    k0 = int(np.argmax(above)); k1 = 35 - int(np.argmax(above[::-1]))
    if k0 == 0 or k1 == 35:               # present at the season boundary: no clean crossing
        return None
    arr = k0 - 1 + (thr - sh[k0 - 1]) / (sh[k0] - sh[k0 - 1])
    dep = k1 + (sh[k1] - thr) / (sh[k1] - sh[k1 + 1])
    return arr * DAYS_PER_PERIOD, dep * DAYS_PER_PERIOD

def analyze(counts_file, threshold, winter_min):
    C = json.load(open(counts_file))["rows"]
    lats = sorted({c["lat"] for c in C}); nb = len(lats)
    tot = np.zeros((nb, 36)); sp = {}
    for c in C:
        b, k = lats.index(c["lat"]), period_index(c["month"], c["dek"])
        tot[b, k] = c["total"]
        for s, n in c["sp"].items():
            sp.setdefault(s, np.zeros((nb, 36)))[b, k] = n
    winter = [period_index(m, d) for m in (12, 1, 2) for d in (1, 11, 21)]
    summer = [period_index(m, d) for m in (6, 7) for d in (1, 11, 21)]
    midwinter = [period_index(12, 21), period_index(1, 1), period_index(1, 11), period_index(1, 21), period_index(2, 1)]
    candidates = [s for s, A in sp.items()
                  if A[:, winter].sum() >= 3000 and A[:, summer].sum() / A[:, winter].sum() * (len(winter) / len(summer)) < 0.03]
    rows = []
    for s in candidates:
        A = sp[s]; share = A / np.maximum(tot, 1)
        for b in range(nb):
            if A[b, winter].sum() < 60:
                continue
            sm = smooth(share[b])
            if sm[midwinter].mean() < winter_min * sm.max():
                continue
            cr = crossings(sm, threshold)
            if cr:
                rows.append(dict(species_key=s, lat=lats[b] + 1, arrival_day=cr[0], departure_day=cr[1], records=int(A[b].sum())))
    B = pd.DataFrame(rows)
    res = []
    for s, g in B.groupby("species_key"):
        if len(g) < 4 or g.lat.max() - g.lat.min() < 8:
            continue
        sa, sd = stats.linregress(g.lat, g.arrival_day), stats.linregress(g.lat, g.departure_day)
        res.append(dict(species_key=s, bands=len(g), lat_span=g.lat.max() - g.lat.min(),
                        arrival_slope=sa.slope, arrival_slope_se=sa.stderr, departure_slope=sd.slope, departure_slope_se=sd.stderr,
                        arrival_sd_across_bands=g.arrival_day.std(), departure_sd_across_bands=g.departure_day.std(),
                        mean_arrival_day=g.arrival_day.mean(), mean_departure_day=g.departure_day.mean()))
    R = pd.DataFrame(res)
    both = R[(R.arrival_slope < 0) & (R.departure_slope > 0)]
    summary = dict(counts_file=str(counts_file), threshold=threshold, winter_min=winter_min,
                   winter_visitor_candidates=len(candidates), species_with_front=len(R),
                   arrival_slope_median=R.arrival_slope.median(), share_arriving_north_first=float((R.arrival_slope < 0).mean()),
                   arrival_sign_test_p=stats.binomtest(int((R.arrival_slope < 0).sum()), len(R)).pvalue,
                   departure_slope_median=R.departure_slope.median(), share_leaving_south_first=float((R.departure_slope > 0).mean()),
                   departure_sign_test_p=stats.binomtest(int((R.departure_slope > 0).sum()), len(R)).pvalue,
                   abs_slope_median_arrival=R.arrival_slope.abs().median(), abs_slope_median_departure=R.departure_slope.abs().median(),
                   share_departure_flatter=float((R.departure_slope.abs() < R.arrival_slope.abs()).mean()),
                   flatter_wilcoxon_p=stats.wilcoxon(R.arrival_slope.abs(), R.departure_slope.abs()).pvalue,
                   both_directions_as_expected=len(both),
                   autumn_front_km_per_day_median=float(np.median(111 / -both.arrival_slope)) if len(both) else None,
                   spring_front_km_per_day_median=float(np.median(111 / both.departure_slope)) if len(both) else None)
    return R, B, summary

if __name__ == "__main__":
    counts, th, wmin, tag = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    R, B, summary = analyze(counts, th, wmin)
    R.round(3).to_csv(ROOT / "results" / f"fronts_{tag}.csv", index=False)
    B.round(2).to_csv(ROOT / "results" / f"bands_{tag}.csv", index=False)
    json.dump(summary, open(ROOT / "results" / f"summary_{tag}.json", "w"), indent=1, default=float)
    print(json.dumps(summary, indent=1, default=float))
