"""Week 5 · D2 — parallel coordinates. python3 partD_pcp.py -> partD_pcp.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import geolib
from vizlib import PALETTE, style_defaults, save_fig

HERE = os.path.dirname(os.path.abspath(__file__))
style_defaults(); plt.rcParams["axes.titlesize"] = 11
hi = pd.read_csv(os.path.join(HERE, "data", "health_indicators.csv"))
COLS = ["gdp_pc", "healthcare_access", "urban_pct", "median_age", "cases_per_100k"]
HOW = "rank"
order = geolib.corr_chain(hi, COLS)       # computed before looking at the plot
r = hi[COLS].corr()
print("scaling:", HOW, "| axis order (greedy |r| chain):", order)
print("adjacent r:", {f"{a}~{b}": round(float(r.loc[a, b]), 3) for a, b in zip(order, order[1:])})
print(f"r(healthcare_access, cases_per_100k) = {r.loc['healthcare_access', 'cases_per_100k']:+.3f}")
means = hi.groupby("region").cases_per_100k.mean().sort_values(ascending=False)
BRUSH = means.index[0]
print(f"brushed region: {BRUSH} (highest mean cases_per_100k {means.iloc[0]:.1f}, n={int((hi.region == BRUSH).sum())}); rule fixed before plotting")

fig, ax = plt.subplots(figsize=(11, 7))
mask = (hi.region == BRUSH).values
geolib.pcp(ax, hi, order, how=HOW, highlight=mask, lw_hl=2.2)
ax.set_title("Where healthcare access is high, case rates are low: lines cross between the first two axes (r = −0.80)")
fig.subplots_adjust(bottom=0.27)
fig.text(0.07, 0.12, f"All axes percentile-rank scaled (not min–max: one country's GDP is 9.2x the next, which flattens a min–max axis).\n"
         f"Axis order = greedy chain by |r| (geolib.corr_chain), fixed before plotting. Axis end labels = raw min / max.\n"
         f"Grey: all 60 countries. Orange: {BRUSH} region (n={mask.sum()}), the region with the highest mean case rate ({means.iloc[0]:.0f} per 100,000).",
         fontsize=8.5, color=PALETTE["ink_soft"], va="top")
ax.text(0.5, 0.5, "X-shaped waist", ha="center", va="center", fontsize=9, color=PALETTE["ink"],
        bbox=dict(boxstyle="round", fc="white", ec=PALETTE["grid"], alpha=0.85))
ax.text(2.5, 1.0, "urban share and median age rise together (r +0.64)", ha="center", fontsize=8.5, color=PALETTE["ink"])
save_fig(fig, os.path.join(HERE, "partD_pcp.png"),
         note="Source: health_indicators.csv, synthetic course data, CDB601220 Week 5, 60 fictional countries; pop_m not plotted (it is the bubble area in D1).")
plt.close(fig)
print("wrote partD_pcp.png")
