# Part A — decisions

One row per decision. *Rows affected* counts rows changed or removed (0 = a finding that is reported, not a row edit).

| # | What | How detected | Rule applied | Rows affected |
|---|---|---|---|---|
| 1 | Register keys mis-typed (`d13`, `D 20`) | GeoJSON join matched only 22 of 24; regex ^D\d\d$ on `code` | strip whitespace + upper-case the key (repair: the true key is unambiguous) | 2 |
| 2 | Row D00 'Qilabad Capital Territory' is not a district | no polygon in regions.geojson; pop 2,890,000 overlaps D17 Qilabad; population sum 60,747,000 != federation's 57,857,000 | drop (accurate row, but it does not belong in a one-row-per-district sum) | 1 |
| 3 | `fare_concession_pct` filed as a fraction in 4 rows (0.327 …) | 20 of 24 values are 20.9–42.6; four are < 1 | repair x100 (a share cannot be 0.3%; the other 20 are percent) | 4 |
| 4 | `boardings_annual` filed in thousands for 3 districts (D05, D15, D23) | boardings per resident < 1 (e.g. 14,551 boardings for 712,000 people) | repair x1000; cross-checked: register total then matches the route table to within 700 | 3 |
| 5 | `road_km` = -1 (operator 'not surveyed' code, D06 and D16) | impossible negative length | set to NaN — missing is not zero, and I cannot state the true value | 2 |
| 6 | Route `mode` has 6 labels for 4 modes (`brt`, `Bus Rapid Transit`) | value_counts() on `mode` | map to canonical BRT (repair: same mode, different spelling) | 3 |
| 7 | `punctuality_pct` = 999 (operator code) | value > 100 is impossible for a percentage | set NaN; never averaged as a number | 3 |
| 8 | `cost_recovery_pct` = 0.0 on R022 and R033 (code for 'not reported') | exact 0.0 on routes that are carrying 5–10 M boardings a year and sell tickets | set NaN (a route with fares cannot recover exactly 0) | 2 |
| 9 | Register total and route-table total disagree by 690 boardings (0.0001%) | sum of register `boardings_annual` vs sum of route `boardings_annual` | REPORTED, not smoothed: rounding in the source; the two files agree to 0.0001% | 0 |
| 10 | `districts_served` is a list: summing by district counts a route up to 4 times | dashlib.overlap_factor(routes, ...) -> 3.096x | route-level sums use the route table once; district-level figures come from the register, which is exclusive | 28 |
| 11 | `date` in two formats; 385 rows are dd/mm/yyyy | regex on the string; month-first parse fails on 230 and silently mis-dates 155 (e.g. 02/12/2025 is 2 Dec, not 12 Feb) | parse each format explicitly (ISO, then %d/%m/%Y) — never one `to_datetime` guess | 385 |
| 12 | 30 exact re-submitted rows (one mode, one month: Bus, 2026-05) | full-row duplicated() after dates parsed | keep first, drop the rest (a return filed twice is one return) | 30 |
| 13 | 7 rows with more departures on time than departures run | trips_on_time > trips_operated (cannot happen) | repair the impossible field only: trips_on_time -> NaN (true value unknowable); the row's boardings and delay are independent and kept. Row excluded from punctuality ratios, included in boardings | 7 |
| 14 | 63 slots nobody filed (22 Ferry, 19 Bus, 18 Metro, 4 BRT); longest gap 14 days (2026-02-09, Metro) -> 2026-02-22 | reindex against the full day x mode calendar | NOT filled and NOT zero: left absent. Sums over a gap are reported as 'filed days'; trends use ratios of sums | 63 |
| 15 | Bus and Ferry stop filing after 2026-09-21; September 2026 is a partial period | slots filed from 2026-09-22: 18 of 36 | series cut at the last complete month (2026-08) for levels; September drawn hatched/greyed if shown | 18 |
| 16 | Register's annual boardings (873.6 M) exceed what the returns account for (845.5 M) | 12-month sum of clean daily boardings vs register total | REPORTED: returns cover 96.8%; the gap is the 63 unfiled days, not an error in either file | 0 |
| 17 | `All tickets` rows (72) are the publisher's own subtotal filed beside the parts | summing every row gives exactly 200.0%; drilldown_check() agrees parts = subtotal for every month/mode | split: parts -> fare_revenue.csv (216 rows); subtotals -> fare_published_totals.csv (72 rows), kept for reconciliation | 72 |
| 18 | Fare table's last month (2026-09) is not a whole month | daily returns for Bus and Ferry stop 2026-09-21; month is below the trend | kept in clean/, flagged by the analysis window: every comparison uses complete months 2025-04 -> 2026-08 | 0 |
