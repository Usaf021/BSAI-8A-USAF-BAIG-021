"""Week 5 · D3 — normalised choropleth + the counts put back as sorted bars. python3 partD_choropleth.py"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import geolib
from vizlib import PALETTE, style_defaults, save_fig

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "data")
style_defaults(); plt.rcParams["axes.titlesize"] = 11
feats = geolib.read_geojson(f"{D}/districts.geojson")
dh = pd.read_csv(f"{D}/district_health.csv")

# 2. join, counted
fcodes = {f["code"] for f in feats}
failed = (fcodes - set(dh.code)) | (set(dh.code) - fcodes)
print(f"join on code: {len(fcodes & set(dh.code))} matched, {len(failed)} failed")
assert not failed
# 3. normalise
dh["rate"] = dh.cases / dh.population * 1e5
pooled = dh.cases.sum() / dh.population.sum() * 1e5
print(f"pooled rate {pooled:.1f} per 100,000 from {dh.cases.sum():,} cases / {dh.population.sum():,} people")
print("top 3 by rate:", list(dh.nlargest(3, "rate").code), "| by count:", list(dh.nlargest(3, "cases").code),
      "| overlap", len(set(dh.nlargest(3, 'rate').code) & set(dh.nlargest(3, 'cases').code)),
      f"| r(cases, population) = {np.corrcoef(dh.cases, dh.population)[0, 1]:+.3f}")
# 4. classify - scheme chosen by GVF, not by taste
vals = dh.rate.values
for sch in ("equal", "quantile", "natural"):
    print(f"  {sch:<8} GVF {geolib.gvf(vals, geolib.breaks(vals, sch, 5)):.3f}")
SCHEME = "natural"
fig, (a, b) = plt.subplots(1, 2, figsize=(13, 6.6), gridspec_kw={"width_ratios": [1.15, 1.25], "wspace": 0.25})
edges = geolib.choropleth(a, feats, dict(zip(dh.code, dh.rate)), scheme=SCHEME, k=5,
                          legend=False)
print("class breaks:", np.round(edges, 1))
cm = plt.get_cmap(PALETTE["sequential"])
shade = [cm(0.18 + 0.78 * c / 4) for c in range(5)]
from matplotlib.patches import Patch
a.legend(handles=[Patch(facecolor=shade[c], label=f"{edges[c]:,.1f}–{edges[c + 1]:,.1f}") for c in range(5)],
         title="Cases per 100,000 residents (natural breaks, 5 classes)", loc="upper center", bbox_to_anchor=(0.5, 0.02),
         ncol=3, fontsize=7.5, title_fontsize=8, frameon=False)
cls = geolib.class_of(dh.rate.values, edges)
lat_ts = np.mean([p[1] for f in feats for p in f["ring"]])
for f in feats:
    lon, lat = geolib.representative_point(f["ring"])
    x, y = geolib.equal_area_xy([lon], [lat], lat_ts=lat_ts)
    if f["code"] in set(dh.nlargest(3, "rate").code) | set(dh.nlargest(3, "cases").code):
        a.text(x[0], y[0], f["code"], fontsize=7.5, ha="center", va="center",
               color="white" if cls[list(dh.code).index(f["code"])] >= 3 else PALETTE["ink"], fontweight="bold")
a.set_title("Risk per resident is highest in the\nnorth (D19–D21), not in the biggest districts")
o = dh.assign(cls=cls).sort_values("cases")
b.barh(o.district + " (" + o.code + ")", o.cases, color=[shade[c] for c in o.cls], edgecolor=PALETTE["muted"], linewidth=0.4)
for y_, (_, r) in enumerate(o.iterrows()):
    b.text(r.cases + 40, y_, f"{r.cases:,}  ·  {r.rate:.0f}/100k", va="center", fontsize=7.5)
b.set_xlim(0, o.cases.max() * 1.3); b.tick_params(axis="y", labelsize=7.5)
b.set_xlabel("Confirmed cases (count); bar colour = rate class on the map")
b.set_title("The counts, put back: D17, D13, D09 lead by count\nbecause they hold the most people (r = +0.99)")
b.grid(axis="y", visible=False)
note = (f"Source: district_health.csv and districts.geojson, synthetic course data, CDB601220 Week 5 (fictional federation; boundaries as supplied, 24 districts, no year stated in the file). "
        f"Rate = cases / resident population x 100,000 (pooled national rate {pooled:.1f}). Projection: Lambert cylindrical equal-area (km), one reference latitude for all layers. "
        f"Join on code: 24 matched, 0 failed. Nothing suppressed (smallest district 468,000 people, 24 districts shown). Classes: Jenks natural breaks, 5 classes, one-hue sequential (Blues).")
import textwrap
save_fig(fig, os.path.join(HERE, "partD_choropleth.png"), note="\n".join(textwrap.wrap(note, 190)))
plt.close(fig)
print("wrote partD_choropleth.png; smallest district population:", int(dh.population.min()))
