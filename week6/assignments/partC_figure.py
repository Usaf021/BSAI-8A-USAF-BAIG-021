"""Week 6 · Task C — the board figure: where is supply least reliable? python3 partA_process.py && python3 partC_figure.py"""
import os
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

import geolib
import vizlib
from vizlib import PALETTE, style_defaults, save_fig

HERE = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(HERE, "clean")
style_defaults(); plt.rcParams["axes.titlesize"] = 11
g = pd.read_csv(os.path.join(C, "district_grid_clean.csv"))
feats = geolib.read_geojson(os.path.join(HERE, "data", "regions.geojson"))
fc = {f["code"] for f in feats}
print(f"join: {len(fc & set(g.code))} matched, {len(fc ^ set(g.code))} unmatched")
assert not fc ^ set(g.code)

g["rate"] = g.outages / g.households * 1000
pooled = g.outages.sum() / g.households.sum() * 1000
print(f"pooled national rate {pooled:.1f} interruptions per 1,000 households")
print(f"r(interruptions, households) = {np.corrcoef(g.outages, g.households)[0, 1]:+.3f}; r(rate, households) = {np.corrcoef(g.rate, g.households)[0, 1]:+.3f}")
tc = list(g.nlargest(3, "outages").code); tr = list(g.nlargest(3, "rate").code)
print("top 3 by count:", tc, "| by rate:", tr, "| on both:", sorted(set(tc) & set(tr)))
t5 = g.nlargest(5, "population"); print(f"5 most populous: {t5.area_km2.sum() / g.area_km2.sum():.1%} of land, {t5.population.sum() / g.population.sum():.1%} of people")
print("count-map winners vs rate-map winners:\n", g[g.code.isin(set(tc) | set(tr))][["code", "district", "outages", "households", "rate"]].round(1).to_string(index=False))
# what would a count-based split do? allocate 100 units of budget
share_count = g.outages / g.outages.sum(); share_hh = g.households / g.households.sum()
excess = (g.rate / pooled - 1)
print(f"D13 Mehrabad: {g[g.code == 'D13'].rate.iloc[0]:.1f}/1,000 = {g[g.code == 'D13'].rate.iloc[0] / pooled - 1:+.0%} vs national; it is on both lists because it is both large (1.11 m households) and worse than average per household")
# budget: counts-based vs rate-based allocation of 100 units by weight on excess interruptions over the pooled expectation
exp_ = g.households * pooled / 1000
excess_int = (g.outages - exp_)
print("excess interruptions over the pooled expectation (events above what the national rate predicts):")
print(excess_int.sort_values(ascending=False).round(0).head(5).to_dict(), "| below expectation (would lose money if count-based):",
      excess_int.sort_values().round(0).head(4).to_dict())
loses = g[(g.code.isin(tc)) & (g.rate < pooled)]
print("count-top-3 districts running BELOW the national rate (they would take money they do not need):", list(loses.code), loses.rate.round(1).tolist())
gain = g[(g.code.isin(tr)) & (~g.code.isin(tc))]
print("rate-top-3 districts a count map would not fund:", list(gain.code), gain.outages.tolist(), "interruptions each")
fl = geolib.funnel_limits(g.households, pooled, per=1000)
lo_ = np.interp(g.households, fl.population, fl.lo); hi_ = np.interp(g.households, fl.population, fl.hi)
n_out = int(((g.rate < lo_) | (g.rate > hi_)).sum())
print(f"funnel (Poisson, 95%): {n_out} of 24 districts outside; smallest district has {int(g.households.min()):,} households and {int(g.outages.min()):,} interruptions "
      "— counts this large make sampling noise tiny, so differences in rate are not small-number artefacts. Nothing suppressed or merged.")

edges = geolib.breaks(g.rate.values, "natural", 5)
cls = geolib.class_of(g.rate.values, edges)
print("Jenks breaks:", np.round(edges, 1), "GVF", round(geolib.gvf(g.rate.values, edges), 3))
cm = plt.get_cmap(PALETTE["sequential"]); shade = [cm(0.18 + 0.78 * c / 4) for c in range(5)]

fig, (a, b) = plt.subplots(1, 2, figsize=(13, 7), gridspec_kw={"width_ratios": [1.1, 1.25], "wspace": 0.22})
geolib.choropleth(a, feats, dict(zip(g.code, g.rate)), scheme="natural", k=5, legend=False)
lat_ts = np.mean([p[1] for f in feats for p in f["ring"]])
for f in feats:
    if f["code"] in set(tc) | set(tr):
        lon, lat = geolib.representative_point(f["ring"]); x, y = geolib.equal_area_xy([lon], [lat], lat_ts=lat_ts)
        c = cls[list(g.code).index(f["code"])]
        a.text(x[0], y[0], f["code"], ha="center", va="center", fontsize=8, fontweight="bold", color="white" if c >= 3 else PALETTE["ink"])
a.legend(handles=[Patch(facecolor=shade[c], label=f"{edges[c]:.1f}–{edges[c + 1]:.1f}") for c in range(5)],
         title="Interruptions per 1,000 households (natural breaks, 5 classes)", loc="upper center", bbox_to_anchor=(0.5, 0.02),
         ncol=3, fontsize=7.5, title_fontsize=8, frameon=False)
a.set_title("Service is worst in D12, D11 and D13,\nnot where the most interruptions are filed")
o = g.sort_values("rate")
b.barh(o.district + " (" + o.code + ")", o.rate, color=[shade[c] for c in geolib.class_of(o.rate.values, edges)], edgecolor=PALETTE["muted"], linewidth=0.4)
b.axvline(pooled, color=PALETTE["ink"], lw=1, ls="--"); b.text(pooled + 0.4, -0.9, f"national {pooled:.1f}", fontsize=8)
for y_, (_, r) in enumerate(o.iterrows()):
    b.text(r.rate + 0.5, y_, f"{r.rate:.1f}   ({r.outages:,} interruptions)", va="center", fontsize=7.2, bbox=dict(fc="white", ec="none", pad=0.6), zorder=5)
b.set_xlim(0, 75); b.tick_params(axis="y", labelsize=7.5)
b.set_xlabel("Interruptions per 1,000 households, 12 months"); b.grid(axis="y", visible=False)
b.set_title("Sorted from zero: the range is 30 to 51, and the\ncount in brackets shows size, not service")
note = ("For: the National Grid Authority board, splitting the reliability budget across 24 districts. Source: district_grid.csv and regions.geojson, synthetic course data, "
        "CDB601220 Week 6 (fictional federation; boundaries as supplied, no year stated). Rate = supply interruptions over 12 months / billed households x 1,000; national pooled rate "
        f"{pooled:.1f}. Projection: Lambert cylindrical equal-area. Classes: Jenks, 5, Blues. Cleaned by partA_process.py: duplicate D11 row dropped, D21 households repaired "
        "(182 -> 182,000). Join 24/24, 0 failed. Nothing suppressed or merged (fewest interruptions in any district: 3,234).")
save_fig(fig, os.path.join(HERE, "partC_figure.png"), note="\n".join(textwrap.wrap(note, 185)))
plt.close(fig)
print("wrote partC_figure.png")
