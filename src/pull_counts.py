"""Count eBird records in India (GBIF 'EOD - eBird Observation Dataset') for every species,
in every 2-degree latitude band (8-36 N) and every 10-day period of the year, for a range of years.
One GBIF API call per band x period (504 calls). Usage:
    python3 src/pull_counts.py 2015,2025 data/counts_2015_2025.json"""
import itertools, json, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

DATASET = "4fa7b334-ce0d-4e88-aaae-2e0c138d049e"
years, out = sys.argv[1], sys.argv[2]
bands = [(a, a + 2) for a in range(8, 36, 2)]
periods = [(1, 10), (11, 20), (21, 31)]

def query(args):
    (a, b), month, (d1, d2) = args
    url = (f"https://api.gbif.org/v1/occurrence/search?datasetKey={DATASET}&country=IN&year={years}"
           f"&decimalLatitude={a},{b}&month={month}&day={d1},{d2}&limit=0&facet=speciesKey&facetLimit=3000")
    for attempt in range(6):
        try:
            r = json.load(urllib.request.urlopen(url, timeout=60))
            sp = {c["name"]: c["count"] for c in r["facets"][0]["counts"]} if r["facets"] else {}
            return dict(lat=a, month=month, dek=d1, total=r["count"], sp=sp)
        except Exception:
            time.sleep(2 + 3 * attempt)
    raise RuntimeError(f"GBIF query failed repeatedly: {url}")

jobs = list(itertools.product(bands, range(1, 13), periods))
with ThreadPoolExecutor(4) as ex:
    rows = []
    for i, r in enumerate(ex.map(query, jobs)):
        rows.append(r)
        if i % 100 == 0:
            print(i, "/", len(jobs), flush=True)
json.dump(dict(years=years, dataset=DATASET, pulled=time.strftime("%Y-%m-%d"), rows=rows), open(out, "w"))
print("wrote", out)
