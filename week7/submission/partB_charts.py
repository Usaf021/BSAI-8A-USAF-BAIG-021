"""Part B — four static charts, four kinds of question.   Run: python3 partB_charts.py

  1  TREND         monthly on-time rate by mode            (ridership_daily)
  2  COMPOSITION   mode share of journeys, per month       (fare_revenue)
  3  RELATIONSHIP  route crowding vs punctuality           (routes)
  4  COMPARISON    boardings per 1,000 residents, mapped   (register + GeoJSON)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import HERE  # sets sys.path for the course toolkits
import vizlib
import geolib
import dashlib
from vizlib import PALETTE
from _common import (HERE, DATA, MODES, MODE_COLOR, MODE_MARKER, SOURCE,
                     load_clean, punctual_rows, ontime_rate, LAST_COMPLETE_MONTH)

vizlib.style_defaults()
d, rt, reg, fare = load_clean()
d["month"] = d.date.dt.to_period("M").astype(str)
import textwrap
wrap = lambda s, n=125: "\n".join(textwrap.wrap(s, n))
_save = vizlib.save_fig
vizlib.save_fig = lambda fig, path, note=None: _save(fig, path, wrap(note) if note else None)
def caption(ax, s, n=105):
    ax.set_title(ax.get_title(loc="left"), pad=26 + 12 * (len(s) // n))
    ax.text(0, 1.015, wrap(s, n), transform=ax.transAxes, fontsize=8.5, style="italic",
            color=PALETTE["ink_soft"], va="bottom")

# ------------------------------------------------------------------- 1 trend
m = ontime_rate(d[d.month <= LAST_COMPLETE_MONTH], ["month", "mode"]).unstack()[MODES]
fig, ax = plt.subplots(figsize=(9, 5))
x = pd.PeriodIndex(m.index, freq="M").to_timestamp()
for mode in MODES:
    ax.plot(x, m[mode], color=MODE_COLOR[mode], marker=MODE_MARKER[mode], ms=4.5, lw=1.8)
    ax.text(x[-1] + pd.Timedelta(days=8), m[mode].iloc[-1], f"{mode}  {m[mode].iloc[-1]:.1f}%",
            color=MODE_COLOR[mode], va="center", fontsize=9, fontweight="bold")
ax.set_xlim(x[0] - pd.Timedelta(days=10), x[-1] + pd.Timedelta(days=95))
ax.set_ylabel("Departures on time, % of departures operated")
ax.set_title("Every mode ran a little less punctually in 2026 than a year earlier")
caption(ax, "Supports: the Board's 'is service getting better?' — read each mode, not the network average.")
vizlib.save_fig(fig, HERE / "partB_1.png",
    "On-time = sum(trips_on_time) / sum(trips_operated) per month and mode (a ratio of sums, not a mean of daily %). "
    "Window 2025-04 to 2026-08; September 2026 omitted (partial: Bus and Ferry stopped filing 21 Sep). "
    "7 rows with impossible on-time counts excluded from the ratio; 63 unfiled mode-days are gaps, not zeros. " + SOURCE)
plt.close(fig)

# ------------------------------------------------------------- 2 composition
fc = fare[fare.month <= LAST_COMPLETE_MONTH]
j = fc.groupby(["month", "mode"]).trips.sum().unstack()[MODES]
share = j.div(j.sum(axis=1), axis=0) * 100
rev = fc.groupby(["month", "mode"]).revenue_pkr.sum().unstack()[MODES]
rshare = rev.div(rev.sum(axis=1), axis=0) * 100
fig, ax = plt.subplots(figsize=(9, 5))
bottom = np.zeros(len(share))
hatches = {"Metro": "", "BRT": "//", "Bus": "..", "Ferry": "xx"}
for mode in MODES:
    ax.bar(share.index, share[mode], bottom=bottom, color=MODE_COLOR[mode], hatch=hatches[mode],
           edgecolor="white", lw=0.6, width=0.82, label=mode)
    bottom += share[mode].values
for mode in ("Metro", "Bus"):
    for i in (0, len(share) - 1):
        yc = share[MODES[:MODES.index(mode)]].iloc[i].sum() + share[mode].iloc[i] / 2
        ax.text(i, yc, f"{share[mode].iloc[i]:.1f}%", ha="center", va="center",
                color="white", fontsize=7, fontweight="bold")
ax.set_ylim(0, 100)
ax.set_xticks(range(len(share)))
ax.set_xticklabels(share.index, rotation=60, ha="right")
ax.set_ylabel("Share of journeys, % (the 4 modes sum to 100)")
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False)
ax.set_title("Metro's share of journeys rose from 28% to 49% as Bus fell from 43% to 24%")
caption(ax, "Supports: fleet re-allocation. Journeys, not revenue: in 2026-08 Metro is 49.4% of journeys but "
            f"{rshare['Metro'].iloc[-1]:.1f}% of revenue (48.3 vs 26.1 PKR per journey).")
vizlib.save_fig(fig, HERE / "partB_2.png",
    "Unit: JOURNEYS (fare table), never boardings. Denominator: all journeys that month "
    "(total journeys +12.1%, 2025-04 -> 2026-08, so share changes are not all volume changes). "
    "The 'All tickets' subtotal rows are excluded (parts only, 216 rows). Complete months 2025-04 to 2026-08; 2026-09 is partial and omitted. " + SOURCE)
plt.close(fig)
print(f"journeys {j.sum(axis=1).iloc[-1] / j.sum(axis=1).iloc[0] - 1:+.1%}, revenue "
      f"{rev.sum(axis=1).iloc[-1] / rev.sum(axis=1).iloc[0] - 1:+.1%}")
fpj = rev / j
print("fare per journey, 2025-04 -> 2026-08 by mode:", (fpj.iloc[-1] / fpj.iloc[0] - 1).round(3).to_dict())
# counterfactual: 2026-08 volumes at 2025-04 fares -> how much of revenue growth is price vs volume/mix
rev_at_old_fares = (j.iloc[-1] * fpj.iloc[0]).sum()
print(f"revenue growth explained by volume+mix at constant 2025-04 fares: "
      f"{rev_at_old_fares / rev.iloc[0].sum() - 1:+.1%} of the {rev.sum(axis=1).iloc[-1] / rev.sum(axis=1).iloc[0] - 1:+.1%}")

# ------------------------------------------------------------ 3 relationship
u = rt.dropna(subset=["punctuality_pct"])
r_all = np.corrcoef(u.crowding_index, u.punctuality_pct)[0, 1]
fig, ax = plt.subplots(figsize=(8.5, 5.4))
for mode in MODES:
    s = u[u["mode"] == mode]
    ax.scatter(s.crowding_index, s.punctuality_pct, color=MODE_COLOR[mode], marker=MODE_MARKER[mode],
               s=55, edgecolor="white", lw=0.8, label=f"{mode} (n={len(s)})", zorder=3)
ax.axvline(1.0, color=PALETTE["ink_soft"], lw=0.9, ls="--")
ax.text(1.005, ax.get_ylim()[0] + 0.5, "at capacity (1.0)", fontsize=8, color=PALETTE["ink_soft"])
worst = u.loc[u.punctuality_pct.idxmin()]
dashlib.callout(ax, (worst.crowding_index, worst.punctuality_pct), f"{worst.route_id}: {worst.punctuality_pct:.1f}%",
                xytext=(worst.crowding_index + 0.08, worst.punctuality_pct + 3))
ax.set_xlabel("Crowding index (peak passengers ÷ capacity)")
ax.set_ylabel("Route on-time, % of departures")
ax.legend(loc="lower right", frameon=False)
ax.set_title(f"Mode, not crowding, sorts a route's punctuality (pooled r = {r_all:+.2f})")
caption(ax, "Supports: where to add capacity — crowded routes are not the late ones; late routes are Bus routes.")
vizlib.save_fig(fig, HERE / "partB_3.png",
    f"n = {len(u)} of 36 routes; 3 routes with punctuality code 999 excluded (not zero, not a number). "
    "Route-level % are AVL shares, shown per route, never averaged across routes. 12 months to 2026-08-31. " + SOURCE)
plt.close(fig)

# ------------------------------------------------------------------- 4 map
feats = geolib.read_geojson(DATA / "regions.geojson")
rg = reg.set_index("code")
rate = (rg.boardings_annual / rg.population * 1000)
fig, ax = plt.subplots(figsize=(8.2, 6.4))
edges = geolib.choropleth(ax, feats, rate.reindex([f["code"] for f in feats]).to_dict(), scheme="natural", k=5,
                          cmap="Greys", legend_title="Boardings per 1,000 residents,\n12 months to 2026-08-31 (Jenks, 5 classes)")
from geolib import equal_area_xy, representative_point, _collection_lat_ts
lat_ts = _collection_lat_ts(feats)
for f in feats:
    if f["code"] in rate.nlargest(3).index:
        px, py = equal_area_xy([representative_point(f["ring"])[0]], [representative_point(f["ring"])[1]], lat_ts=lat_ts)
        ax.text(px[0], py[0], f["code"], ha="center", va="center", fontsize=8, fontweight="bold",
                color="white", path_effects=[__import__("matplotlib.patheffects", fromlist=["x"]).withStroke(linewidth=2, foreground=PALETTE["ink"])])
top = rate.nlargest(3)
ax.set_title("Riding per head peaks in " + ", ".join(top.index) + " — not where the people are")
caption(ax, "Supports: siting the next corridor by trips per resident, not by raw boardings (a population map).", n=48)
print("class breaks:", [round(e) for e in edges])
vizlib.save_fig(fig, HERE / "partB_4.png",
    "Denominator: residents of the district (register population, 57,857,000 in 24 districts). Numerator: boardings attributed "
    "to the district by the register (873,564,130; 3 districts repaired x1000, see decisions). Equal-area projection; "
    f"breaks printed: {', '.join(f'{e:,.0f}' for e in edges)}. Row D00 (capital territory) excluded. " + SOURCE)
plt.close(fig)
print("wrote partB_1..4.png")
