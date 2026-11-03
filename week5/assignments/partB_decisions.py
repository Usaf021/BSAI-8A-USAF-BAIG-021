"""
Week 5 · Part B — the five decisions, computed.

    python3 partB_decisions.py | tee partB_output.txt     (also writes partB_overplot.png)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from sklearn.decomposition import PCA

import geolib
from vizlib import PALETTE, style_defaults, save_fig

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "data")
style_defaults(); plt.rcParams["axes.titlesize"] = 10
hi = pd.read_csv(f"{D}/health_indicators.csv")
FIVE = ["gdp_pc", "healthcare_access", "urban_pct", "median_age", "cases_per_100k"]

# ---------------------------------------------------------------- 1
print("== B1  the size range ==")
LO, HI = 12, 1500                      # marker area in points^2
pop = hi.pop_m
s = LO + (HI - LO) * (pop - pop.min()) / (pop.max() - pop.min())      # AREA, linear in population
print(f"sizes=(lo, hi) = ({LO}, {HI}) points^2, applied as AREA (ax.scatter s=, which is points^2).")
print(f"  smallest mark: area {LO} pt^2 -> diameter {2 * np.sqrt(LO / np.pi):.1f} pt (about {2 * np.sqrt(LO / np.pi) / 72 * 25.4:.1f} mm): "
      "the smallest that still shows a filled disc with an edge at 300 dpi and 6 inch panels.")
print(f"  largest mark: area {HI} pt^2 -> diameter {2 * np.sqrt(HI / np.pi):.1f} pt ({2 * np.sqrt(HI / np.pi) / 72:.2f} in): "
      "covers ~1/8 of a 5-inch axis; the 3 largest countries are far apart in GDP so they do not swallow neighbours.")
print(f"  area ratio {HI / LO:.0f}x  ->  DIAMETER ratio {np.sqrt(HI / LO):.1f}x (= sqrt of area ratio; radius-driven would be {HI / LO:.0f}x).")
print(f"  population range is {pop.max() / pop.min():.0f}x, so the 125x area range COMPRESSES it; the size legend carries the real values.")
chk = np.sqrt(s)
print(f"  check area-not-radius: sqrt(s) is not linear in pop (r = {np.corrcoef(chk, pop)[0, 1]:.3f}) while s is (r = {np.corrcoef(s, pop)[0, 1]:.3f}).")

# ---------------------------------------------------------------- 2
print("\n== B2  overplotting: 9,000 points, an 800-point cluster at (3.1, 3.0) ==")
d = pd.read_csv(f"{D}/scatter_dense.csv"); x, y = d.x.values, d.y.values
near = np.hypot(x - 3.1, y - 3.0) < 0.35
print(f"points within 0.35 of (3.1, 3.0): {near.sum()} of 9,000 (the cluster is a tight blob in the upper-right tail)")
ALPHA, GRID = 0.12, 40
fig, axs = plt.subplots(2, 2, figsize=(11, 9)); axs = axs.ravel()
axs[0].scatter(x, y, s=8, color=PALETTE["series"][0]); axs[0].set_title("Opaque (s=8)")
axs[1].scatter(x, y, s=8, color=PALETTE["series"][0], alpha=ALPHA, linewidths=0); axs[1].set_title(f"Transparent (alpha={ALPHA})")
hb = axs[2].hexbin(x, y, gridsize=GRID, cmap="Blues", mincnt=1); axs[2].set_title(f"Hexbin (gridsize={GRID})")
kd = gaussian_kde(np.vstack([x, y])); gx, gy = np.meshgrid(np.linspace(x.min(), x.max(), 160), np.linspace(y.min(), y.max(), 160))
z = kd(np.vstack([gx.ravel(), gy.ravel()])).reshape(gx.shape)
axs[3].contourf(gx, gy, z, levels=12, cmap="Blues"); axs[3].set_title("2-D KDE (Scott bandwidth)")
for a_ in axs:
    a_.scatter([3.1], [3.0], s=300, facecolor="none", edgecolor=PALETTE["highlight"], lw=1.2); a_.set_xlabel("x"); a_.set_ylabel("y")
save_fig(fig, os.path.join(HERE, "partB_overplot.png"), note="Orange ring marks (3.1, 3.0). Synthetic course data, CDB601220 Week 5."); plt.close(fig)
H, xe, ye = np.histogram2d(x, y, bins=GRID)
cxs, cys = (xe[:-1] + xe[1:]) / 2, (ye[:-1] + ye[1:]) / 2
CX, CY = np.meshgrid(cxs, cys, indexing="ij"); incl = np.hypot(CX - 3.1, CY - 3.0) < 0.8
print(f"points within 0.9 of (3.1, 3.0): {(np.hypot(x - 3.1, y - 3.0) < 0.9).sum()} (the 800-point cluster). "
      f"Densest 40x40 bin: cluster {H[incl].max():.0f} points vs main cloud {H[~incl].max():.0f}; median occupied bin of the cloud {np.median(H[~incl & (H > 0)]):.0f}")
kz = kd([[3.1], [3.0]])[0]
print("  opaque:      the cluster is visible as an isolated blob — but it looks exactly as dense as the 8,200-point cloud, "
      "which is a solid slab. Density cannot be read: 800 points and 80 would look the same. Location yes, amount no.")
print(f"  transparent: alpha={ALPHA}. Cluster visible and darker than the cloud edge; inside the cloud the darkness saturates "
      "in the middle, so relative density is only roughly readable. Visible, weakly quantitative.")
print(f"  hexbin:      gridsize={GRID}. Cluster is visible AND is the densest region (max bin {H[incl].max():.0f} vs {H[~incl].max():.0f} for "
      "the whole cloud); the colour bar gives counts.")
print(f"  KDE:         visible as a second hill; density at the cluster {kz:.3f} vs main peak {z.max():.3f} ({kz / z.max():.0%}); "
      "smooth, but depends on the bandwidth and gives no counts.")
print(f"Publish: hexbin (gridsize={GRID}) with a count colour bar — the cluster is visible, countable, and there is no bandwidth "
      f"to defend. Declared parameters: gridsize={GRID}; (alpha={ALPHA} and the KDE bandwidth are on the comparison figure only).")

# ---------------------------------------------------------------- 3
print("\n== B3  scaling three ways, then PCA ==")
for how in ("minmax", "zscore", "rank"):
    sc = geolib.scale_frame(hi, FIVE, how)["gdp_pc"]
    extra = f"{(sc < 0.1).sum()} of 60 below 0.10" if how != "zscore" else f"{(sc.abs() < 0.5).sum()} of 60 within ±0.5 sd"
    print(f"  {how:<7} gdp_pc axis: min {sc.min():.3f} median {sc.median():.3f} max {sc.max():.3f} | {extra}"
          + (f" | Aldonia at {sc.max():.2f} sd, the other 59 span {sc.sort_values().iloc[:-1].min():.2f}..{sc.sort_values().iloc[-2]:.2f}" if how == "zscore" else ""))
Z = (hi[FIVE] - hi[FIVE].mean()) / hi[FIVE].std(ddof=0)
pca = PCA().fit(Z); ev = pca.explained_variance_ratio_
print(f"  PCA on standardised columns: explained variance ratio {np.round(ev, 3).tolist()}")
print(f"  first two components hold {ev[:2].sum():.1%}; a two-axis picture misses {1 - ev[:2].sum():.1%} of the variance")

# ---------------------------------------------------------------- 4
print("\n== B4  project before you measure ==")
feats = geolib.read_geojson(f"{D}/districts.geojson")
sph = np.array([geolib.polygon_area_km2(f["ring"]) for f in feats])
def shoelace(xs, ys):
    xs, ys = np.asarray(xs), np.asarray(ys); return abs(np.sum(xs * np.roll(ys, -1) - np.roll(xs, -1) * ys)) / 2
deg = np.array([shoelace([p[0] for p in f["ring"]], [p[1] for p in f["ring"]]) for f in feats])
merc = np.array([shoelace(*geolib.mercator_xy([p[0] for p in f["ring"]], [p[1] for p in f["ring"]])) for f in feats])
lat = np.array([geolib.representative_point(f["ring"])[1] for f in feats])
north = np.argsort(lat)[::-1][:4]
codes = [f["code"] for f in feats]
print("four northernmost districts (by representative-point latitude):", [codes[i] for i in north])
print(f"  share of total area, spherical: {sph[north].sum() / sph.sum():.2%}   raw lon/lat shoelace: {deg[north].sum() / deg.sum():.2%}")
sh_s, sh_d = sph / sph.sum(), deg / deg.sum()
dist = (sh_d / sh_s - 1) * 100; k = np.abs(dist).argmax()
print(f"  most distorted single district: {codes[k]} (lat {lat[k]:.1f}): {sh_s[k]:.2%} true vs {sh_d[k]:.2%} in degrees ({dist[k]:+.1f}%)")
print(f"  the degree shoelace weights every district equally per square degree; a degree of longitude at 36N is "
      f"{np.cos(np.radians(36)):.2f} as wide as at the equator, so the north is over-weighted.")
infl = merc.sum() / sph.sum()
print(f"  Mercator area inflation across the federation: total Mercator area / true area = {infl:.3f}x "
      f"(district range {np.min(merc / sph):.2f}x at the south edge to {np.max(merc / sph):.2f}x in the north)")
print("  Why it matters (slide 34): in a choropleth the colour covers an area, so area is the encoding channel; Mercator makes the "
      f"north {np.max(merc / sph) / np.min(merc / sph):.2f}x heavier than the south for identical true size, so the map weights the same data differently by latitude.")

# ---------------------------------------------------------------- 5
print("\n== B5  small-area stability, funnel plot ==")
sm = pd.read_csv(f"{D}/smallarea_cases.csv"); sm["rate"] = sm.cases / sm.population * 1e5
p = sm.cases.sum() / sm.population.sum() * 1e5
fl = geolib.funnel_limits(sm.population, p)
lo_i = np.interp(sm.population, fl.population, fl.lo); hi_i = np.interp(sm.population, fl.population, fl.hi)
out = (sm.rate < lo_i) | (sm.rate > hi_i)
print(f"pooled rate {p:.2f} per 100,000; units outside the 95% limits: {int(out.sum())} of 40 {list(sm.unit[out])} "
      f"(chance alone predicts ~{0.05 * 40:.0f})")
print("So the map in case 6 is almost entirely noise: only U32 is flagged, and even it is the expected one-or-two false alarm; "
      "all units share one true rate.")
for pop_ in np.arange(10000, 20_000_000, 10000):
    l1, l2 = 9e-5 * pop_, 18e-5 * pop_
    if l1 + 1.96 * np.sqrt(l1) < l2 - 1.96 * np.sqrt(l2):
        print(f"minimum population at which 9 vs 18 per 100,000 separate (95% Poisson intervals just stop overlapping): ~{int(pop_):,}")
        break
print("(at 95% limits on both sides; a stricter comparison needs more)")
