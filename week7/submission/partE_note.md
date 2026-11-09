# Part E — the note

**Message (one sentence).** The Authority's "punctuality is improving" (+1.73 pts, 78.87% → 80.60%, 2025 Q2 → 2026 Q2) is a mix effect — every one of the four modes got *worse* (−0.85 to −1.31 pts); within-mode change is **−1.10** and the shift of departures to the punctual Metro adds **+2.82**. For the Secretary, who reads the top-left tile for thirty seconds; the finance director and the journalist get the same screen with the caveat built into the tile.

**Parameters, each with a reason**

| Parameter | Choice | Why |
|---|---|---|
| Window | 2025 Q2 vs 2026 Q2 | two complete quarters, same season; 2026-09 is partial (Bus and Ferry stopped filing on the 21st) and is left out. First-3 vs last-3 months gives +2.02, first-6 vs last-6 +1.52, all four modes down both times |
| Unit | departures (punctuality), **journeys** (fares), **boardings** (map) | never mixed on one axis: 1,000 journeys ≈ 1,300 boardings |
| Aggregation | ratio of sums, Σ on-time ÷ Σ operated | a mean of daily % would weight a 300-departure Sunday like a 3,000 Tuesday |
| Denominator (map) | residents of the district (register), per 1,000 | a count map is a population map (r = +0.945) |
| Breaks | Jenks, 5 classes: 4,683 / 8,090 / 11,921 / 16,179 / 20,437 / 30,655 | natural groupings in 24 values; printed on the figure |
| Projection | equal-area | colour fills area, so area must be honest |
| Fares | parts only (216 rows) | the 72 "All tickets" rows are the publisher's subtotal; summing everything gives exactly 200% |
| Revenue vs journeys | headline revenue +26.9% against journeys +12.1% | fare per journey is flat (−0.1% to +2.8%) in every mode, so the gap is **mix** toward Metro (48.3 PKR vs 26.1 for Bus), not price. At constant 2025-04 fares volume + mix alone give +26.3% of the +26.9% |

**Counterfactual.** The raw-count map of boardings would have pointed the next corridor at **D17, D09, D13** — the biggest districts (r(boardings, population) = **+0.945**; the five most populous hold 59.9% of people on 12.6% of the land). The rate map (boardings per 1,000 residents, r with population only **+0.249**) points at **D12, D21, D09**. Only **D09** is on both lists, and it is on both because it is large *and* heavily ridden. The count version would take the corridor *away from* D12 and D21, small districts whose residents ride most per head, and send it to D17 and D13, which are big but ride 16,179 and 15,328 per 1,000 residents, close to the pooled national 15,099.

**Ethics clause.** This screen is being used to site infrastructure, so the choice of denominator is a choice about who gets served. I did not suppress or merge any district for small numbers: all 24 are shown (smallest population 468,000, so no rate rests on a handful of events). Rows removed for other reasons are counted in `partA_decisions.md` — the capital-territory row D00 (2,890,000 people who overlap D17) was dropped, 30 re-submitted returns were dropped, and 63 days nobody filed are shown as gaps rather than zeros. Two things a reader should not over-read: the register's boardings are the route table's boardings re-attributed to districts, and the returns account for only 96.8% of them (the missing 3.2% is unfiled days).
