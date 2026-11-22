# Audit notes

## Checks

- **Period indexing.** `period_index` maps July 1-10 to 0 and June 21-30 to 35; verified by hand for the winter and summer period lists.
- **Crossing dates.** Arrival is the first rise through the threshold and departure the last fall, each linearly interpolated. A species present at the season boundary (1 July) in a band gets no date in that band. Days per period = 365.25 / 36 (earlier code used 10.15; the difference is under 0.1%).
- **Winter-band filter.** The first version of this analysis mixed bands where a species winters with bands it only passes through, which blurred the departure dates. The filter (mid-winter rate at least 0.5 of the band's peak) was added and both values 0.5 and 0.7 are in the robustness grid.
- **Slope signs.** Arrival regressed on latitude: a negative slope means higher latitude gets an earlier date, that is north first. Departure positive means south leaves first. Checked against the per-band medians in the figure.
- **GBIF query.** `year=2015,2025` and `decimalLatitude=a,b` are inclusive ranges in the GBIF API. `facetLimit=3000` exceeds the number of bird species recorded in India, so no species is dropped from a facet.
- **Reproduction.** The consolidated `fronts.py` reproduces the earlier numbers exactly on the saved counts (71 species, arrival slope −1.27, departure +0.35, p = 0.34).

## Changes made during the audit

- Three patched copies of the analysis script (`fronts.py`, `fronts2.py`, `fronts3.py`) were merged into one `fronts.py` with the threshold, winter minimum and counts file as arguments.
- The robustness grid is now one script that writes one table, instead of shell loops whose output was only printed.
- Counts files now record which years and which dataset they came from, and the pull date.
- Sign tests for both directions are now computed and saved for every setting, not only for the main one.

## What the robustness table shows that the first summary understated

The earlier summary said spring departure has "no consistent order". That is true at thresholds 0.5 and 0.75. At threshold 0.25 there is a weak but significant south-first signal (66% of species, p = 0.009 for all years). The README now reports the whole grid.

## Second pass

- Re-read every script. The crossing interpolation cannot divide by zero: the period before the first crossing is strictly below the threshold and the period at the crossing is at or above it.
- A band and period with no records at all gives a reporting rate of 0 (division guarded), which can only delay an arrival or advance a departure in that band, never invent one.
- Species candidates are selected on raw record counts, not rates, so the 3,000-record floor is a true sample-size floor.
- The clean rerun on 2026-11-22 pulled exactly the same 49,575,530 records as the saved counts, so every saved number reproduced byte for byte that day.

## Known weaknesses that remain

- GBIF's eBird dataset changes daily; a fresh pull will not reproduce the saved counts to the record, though the conclusions should hold.
- Reporting rate is a coarse effort correction.
- Species identity was not checked for taxonomic splits or merges between 2015 and 2025 in the GBIF backbone.
