"""
Week 6 · Task B — three charts, three question types.
  B1 TREND        grid_daily.csv      how much energy is the grid delivering, month by month?
  B2 COMPOSITION  generation_mix.csv  is the rise in solar real, or arithmetic?
  B3 RELATIONSHIP district_grid.csv   do interruption counts measure reliability, or population?

    python3 partA_process.py && python3 partB_charts.py
"""
import os
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import vizlib
from vizlib import PALETTE, style_defaults, save_fig

HERE = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(HERE, "clean")
style_defaults(); plt.rcParams["axes.titlesize"] = 11
BLUE, ORANGE, GREEN = PALETTE["series"]; PINK, GREY = PALETTE["series_4th"], PALETTE["muted"]
SRC = "Synthetic course data, CDB601220 Week 6."


def wrap(s, w=170): return "\n".join(textwrap.wrap(s, w))


# --------------------------------------------------------------------- B1
d = pd.read_csv(os.path.join(C, "grid_daily_clean.csv"), parse_dates=["date"])
d["month"] = d.date.dt.to_period("M")
ok = d[d.energy_mwh.notna() & d.days_spanned.notna()]
zm = ok.groupby(["zone", "month"]).agg(e=("energy_mwh", "sum"), days=("days_spanned", "sum"))
zm["per_day"] = zm.e / zm.days
tot = zm.per_day.groupby("month").sum()                       # sum of six zones' mean daily energy
ndays = d.groupby("month").date.nunique()
full_months = tot.index[:-1]; last = tot.index[-1]
print(f"B1 monthly energy: {len(tot)} months; last month {last} has {int(d[d.month == last].date.nunique())} reporting days (partial)")
print(f"   peak {tot.idxmax()} {tot.max() / 1000:,.0f} GWh/day? -> MWh/day {tot.max():,.0f}; trough {tot[:-1].idxmin()} {tot[:-1].min():,.0f}")
yoy = {str(m): round(tot[m] / tot[m - 12] - 1, 3) for m in tot.index[:-1] if (m - 12) in tot.index}
print("   same month a year earlier (MWh/day change):", yoy)
fig, ax = plt.subplots(figsize=(10.5, 4.8))
x = tot.index.to_timestamp()
ax.plot(x[:-1], tot.values[:-1], color=BLUE, marker="o", ms=4)
ax.plot(x[-2:], tot.values[-2:], color=BLUE, ls=":", marker="o", ms=4, mfc="white")
ax.annotate(f"{last} partial:\n11 days only", (x[-1], tot.values[-1]), xytext=(-60, -42), textcoords="offset points", fontsize=8, color=ORANGE,
            arrowprops=dict(arrowstyle="-", color=ORANGE))
ax.set_ylim(0)
ax.set_ylabel("Energy delivered, MWh per day (six zones)")
ax.ticklabel_format(axis="y", style="plain")
i1 = tot[:-1].idxmax(); i0 = tot[:-1].idxmin()
ax.set_title(f"Delivered energy peaks in {i1.strftime('%b %Y')} (trough {i0.strftime('%b %Y')}) and runs {min(yoy.values()):.0%}–{max(yoy.values()):.0%} above the same month a year earlier")
cap = ("Supports: scheduling maintenance outages for the low-demand months. Delivered energy is up year on year while published generation is down 5% (B2); the six zone meters need not cover all generation, so I do not reconcile them here. "
       "Energy = change in the zone meter reading (never the sum of readings), divided by the days spanned. 128 unreported zone-days not filled; "
       "P4's meter-reset day excluded.")
save_fig(fig, os.path.join(HERE, "partB_1.png"), note=wrap(cap + "  " + SRC + " Aggregation: monthly mean of daily energy per zone, summed over zones; dotted = partial month."))
plt.close(fig)

# --------------------------------------------------------------------- B2
gp = pd.read_csv(os.path.join(C, "generation_parts.csv")); gt = pd.read_csv(os.path.join(C, "generation_totals.csv")).set_index("month").mwh
piv = gp.pivot_table(index="month", columns="subsource", values="mwh", aggfunc="sum")
assert (piv.sum(axis=1) - gt).abs().max() <= 2
tot_g = piv.sum(axis=1)
sol = piv["Solar"]; share = sol / tot_g * 100
m0, m1 = piv.index[0], piv.index[-1]
print(f"\nB2 generation {m0}->{m1}: {tot_g[m1] / tot_g[m0] - 1:+.1%}; solar MWh {sol[m0]:,}->{sol[m1]:,} ({sol[m1] / sol[m0] - 1:+.1%}); solar share {share[m0]:.1f}% -> {share[m1]:.1f}%")
for a_, b_ in [("2025-04", "2026-04"), ("2025-09", "2026-09")]:
    print(f"   like-for-like {a_} vs {b_}: total {tot_g[b_] / tot_g[a_] - 1:+.1%}, solar {sol[b_] / sol[a_] - 1:+.1%}, solar share {share[a_]:.1f}% -> {share[b_]:.1f}%")
print(f"   share of solar's share rise caused by the shrinking total: share ratio {share[m1] / share[m0]:.2f}x = solar growth {sol[m1] / sol[m0]:.2f}x / total {tot_g[m1] / tot_g[m0]:.3f}x")
order = ["Coal", "Furnace oil", "Gas", "Dam", "Run-of-river", "Wind", "Imported", "Solar"]
groups = {"Fossil (coal, gas, furnace oil)": ["Coal", "Furnace oil", "Gas"], "Hydro (dam, run-of-river)": ["Dam", "Run-of-river"],
          "Wind": ["Wind"], "Imported": ["Imported"], "Solar": ["Solar"]}
cols = [GREY, BLUE, GREEN, "#B9C3CF", ORANGE]
fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [1.35, 1]})
xs = pd.to_datetime(piv.index + "-01"); bottom = np.zeros(len(piv))
for (lab, mem), c in zip(groups.items(), cols):
    v = piv[mem].sum(axis=1).values / 1e6
    a.bar(xs, v, bottom=bottom, width=24, color=c, label=lab); bottom += v
a.set_ylabel("Energy generated, million MWh per month (sum)"); a.set_ylim(0)
a.set_title(f"Total generation fell {abs(tot_g[m1] / tot_g[m0] - 1):.1%} ({m0} to {m1}):\na share can rise on arithmetic alone")
a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=8)
b.bar(xs, sol / 1e3, width=24, color=ORANGE)
b.set_ylim(0); b.set_ylabel("Solar generation, thousand MWh per month (sum)")
for i in (0, 5, 11, 17):
    b.text(xs[i], sol.iloc[i] / 1e3 + 15, f"{share.iloc[i]:.1f}%\nof mix", ha="center", fontsize=8)
yo = [sol["2026-04"] / sol["2025-04"] - 1, sol["2026-09"] / sol["2025-09"] - 1]
b.set_title(f"Solar is up {min(yo):.0%}–{max(yo):.0%} year on year in MWh\n(+{sol[m1] / sol[m0] - 1:.0%} compares April with September)")
import matplotlib.dates as mdates
for ax_ in (a, b):
    ax_.xaxis.set_major_locator(mdates.MonthLocator(interval=3)); ax_.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))
fig.tight_layout()
cap = ("Supports: the communications line on rooftop solar. Say 'solar generation is up 35–48% on a year ago while total generation is down about 5%'. "
       "The +82.1% and 4.1% → 7.9% endpoints (Apr 2025 vs Sep 2026) are true but cross two seasons. Parts only (144 rows); the published 'Total' rows are excluded, so the shares sum to 100%.")
save_fig(fig, os.path.join(HERE, "partB_2.png"), note=wrap(cap + "  " + SRC + " Aggregation: monthly sums, 18 complete months, 8 categories grouped to 5, no 'Other' bucket."))
plt.close(fig)

# --------------------------------------------------------------------- B3
g = pd.read_csv(os.path.join(C, "district_grid_clean.csv"))
g["per1000"] = g.outages / g.households * 1000
pooled = g.outages.sum() / g.households.sum() * 1000
r1 = np.corrcoef(g.outages, g.households)[0, 1]; r2 = np.corrcoef(g.per1000, g.households)[0, 1]
print(f"\nB3 r(interruptions, households) = {r1:+.3f}; r(per 1,000 households, households) = {r2:+.3f}; pooled {pooled:.1f}")
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.8))
a.scatter(g.households / 1e3, g.outages / 1e3, color=BLUE)
k = np.polyfit(g.households / 1e3, g.outages / 1e3, 1); xx = np.array([0, g.households.max() / 1e3]); a.plot(xx, np.polyval(k, xx), color=GREY, lw=1.2)
a.set_xlim(0); a.set_ylim(0)
a.set_xlabel("Households (thousand)"); a.set_ylabel("Supply interruptions, 12 months (thousand, count)")
a.set_title(f"Counts just track population: r = {r1:+.2f}")
b.scatter(g.households / 1e3, g.per1000, color=BLUE); b.axhline(pooled, color=GREY, lw=1.2)
b.text(g.households.max() / 1e3, pooled + 2, f"national {pooled:.1f}", ha="right", fontsize=8, color=PALETTE["ink_soft"])
for code in ("D12", "D11", "D13"):
    r_ = g[g.code == code].iloc[0]
    b.annotate(f"{code} {r_.district}", (r_.households / 1e3, r_.per1000), xytext=(6, 6), textcoords="offset points", fontsize=8)
b.set_xlim(0); b.set_ylim(0, 60)
b.set_xlabel("Households (thousand)"); b.set_ylabel("Interruptions per 1,000 households")
b.set_title(f"Per household the link is gone: r = {r2:+.2f}")
fig.tight_layout()
cap = ("Supports: the reliability budget split. Allocate on interruptions per 1,000 households, not on interruption counts, which only say which districts are biggest. "
       "n = 24 districts; D21 households repaired (182 → 182,000), D11 duplicate dropped.")
save_fig(fig, os.path.join(HERE, "partB_3.png"), note=wrap(cap + "  " + SRC + " Denominator: billed domestic households; rate pooled nationally."))
plt.close(fig)
print("\nwrote partB_1.png partB_2.png partB_3.png")
