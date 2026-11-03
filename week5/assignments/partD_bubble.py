"""Week 5 · D1 — four-variable bubble chart. python3 partD_bubble.py -> partD_bubble.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import vizlib
from vizlib import PALETTE, style_defaults, save_fig

HERE = os.path.dirname(os.path.abspath(__file__))
style_defaults(); plt.rcParams["axes.titlesize"] = 11
hi = pd.read_csv(os.path.join(HERE, "data", "health_indicators.csv"))
regions = sorted(hi.region.unique())
HUES = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]
SHAPES = ["o", "s", "^", "D", "v", "P"]
for kind in (None, "deutan", "protan", "tritan"):
    i, j, a, b, d = vizlib.worst_pair(HUES, kind)
    print(f"palette worst pair ({kind or 'normal'}): slots {i}&{j} dE {d:.1f} -> {vizlib.verdict(d)}")
print("Pairs under 8 get a second channel: every region has its own marker shape and the labelled countries carry direct labels.")

LO, HI = 12, 1500
s = LO + (HI - LO) * (hi.pop_m - hi.pop_m.min()) / (hi.pop_m.max() - hi.pop_m.min())   # AREA in points^2 (scatter s=)
print(f"sizes=({LO},{HI}) pt^2 as AREA; diameter ratio {np.sqrt(HI / LO):.1f}x; {len(hi)} countries, {len(regions)} regions")

fig, ax = plt.subplots(figsize=(11, 7))
for k, reg in enumerate(regions):
    m = hi.region == reg
    ax.scatter(hi.gdp_pc[m], hi.healthcare_access[m], s=s[m], color=HUES[k], marker=SHAPES[k], alpha=0.62,
               edgecolor="white", linewidth=0.7, label=reg)
ax.set_xscale("log")
ax.set_xlim(200, 250000); ax.set_ylim(0, 100)
ax.set_xlabel("GDP per capita, USD per person per year (log scale)")
ax.set_ylabel("Healthcare access index (0–100)")
ax.set_title("Healthcare access rises with GDP per capita; the three biggest countries span 33 to 79")
tall = {"Aldonia": (8, -22), "Wessant": (-170, 38), "Vornath": (-10, 14), "Tarrowin": (12, -22)}
for name, off in tall.items():
    r = hi[hi.country == name].iloc[0]
    ax.annotate(f"{name}  ({r.pop_m:,.1f} m people)", (r.gdp_pc, r.healthcare_access), xytext=off, textcoords="offset points",
                fontsize=8.5, arrowprops=dict(arrowstyle="-", color=PALETTE["ink_soft"], lw=0.7))
ax.annotate("Outlier kept, not dropped: Aldonia, $120,219, is 9.2x the next richest;\nthe log axis puts it in range without squashing the other 59.",
            (120219, 71), xytext=(900, 5), fontsize=8, color=PALETTE["ink_soft"])
from matplotlib.lines import Line2D
prox = [Line2D([], [], marker=SHAPES[k], color="none", markerfacecolor=HUES[k], markersize=8, label=r) for k, r in enumerate(regions)]
leg1 = ax.legend(handles=prox, title="Region (hue = identity; shape repeats it)", loc="upper left", fontsize=8, title_fontsize=8, ncol=2)
ax.add_artist(leg1)
hs = [ax.scatter([], [], s=LO + (HI - LO) * (v - hi.pop_m.min()) / (hi.pop_m.max() - hi.pop_m.min()), color=PALETTE["muted"], alpha=0.65, edgecolor="white", label=f"{v:,.0f} m")
      for v in (1, 50, 150, 350)]
ax.legend(handles=hs, title="Population (mark AREA, real values)", loc="lower right", labelspacing=1.6, borderpad=1.0, fontsize=8, title_fontsize=8)
save_fig(fig, os.path.join(HERE, "partD_bubble.png"),
         note="Source: health_indicators.csv, synthetic course data, CDB601220 Week 5 (60 fictional countries). Size = area, sizes=(12, 1500) pt², linear in population "
              "(legend gives real values). x on log scale. cases_per_100k not shown here.")
plt.close(fig)
print("wrote partD_bubble.png")
