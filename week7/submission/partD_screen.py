"""Part D — the one screen.   Run: python3 partD_screen.py   -> partD_screen.png

Also appends the channel plan (channel_conflicts) and cvd_report to partA_audit.txt.
Reading order: 1 headline tile -> 2 is it real? -> 3 why (mix) -> 4 where -> 5 money -> 6 why money rose.
"""
import io
import contextlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import textwrap

from _common import (HERE, DATA, AUDIT, MODES, MODE_COLOR, MODE_MARKER, SOURCE, Q_BEFORE, Q_AFTER,
                     load_clean, punctual_rows, between, LAST_COMPLETE_MONTH)
import vizlib
import geolib
import dashlib
from vizlib import PALETTE

vizlib.style_defaults()
d, rt, reg, fare = load_clean()

# ------------------------------------------------------------ the numbers
b, a = punctual_rows(between(d, Q_BEFORE)), punctual_rows(between(d, Q_AFTER))
dec = dashlib.rate_decomposition(b, a, "mode", "trips_on_time", "trips_operated")
g = dec["groups"].reindex(MODES)
assert dec["reversal"], "the screen is built on the reversal"
fc = fare[fare.month <= LAST_COMPLETE_MONTH]
j = fc.groupby(["month", "mode"]).trips.sum().unstack()[MODES]
rev = fc.groupby(["month", "mode"]).revenue_pkr.sum().unstack()[MODES]
j_chg = (j.iloc[-1] / j.iloc[0] - 1) * 100
tot_j, tot_r = j.sum(axis=1), rev.sum(axis=1)
j_tot, r_tot = (tot_j.iloc[-1] / tot_j.iloc[0] - 1) * 100, (tot_r.iloc[-1] / tot_r.iloc[0] - 1) * 100
fpj_chg = ((rev / j).iloc[-1] / (rev / j).iloc[0] - 1) * 100
print(f"network {dec['rate_before']:.2f} -> {dec['rate_after']:.2f} ({dec['change']:+.2f}); within {dec['within']:+.2f}, "
      f"mix {dec['mix']:+.2f}; reversal={dec['reversal']}; journeys {j_tot:+.1f}%, revenue {r_tot:+.1f}%")

# ------------------------------------------------------------ the channel plan
panels = [
    {"panel": "1 headline tile"},
    {"panel": "2 is it real (slope)", "x": "quarter", "y": "on-time %", "hue": "mode", "shape": "mode"},
    {"panel": "3 why (mix dumbbell)", "x": "share of departures %", "y": "mode", "hue": "mode", "shape": "mode"},
    {"panel": "4 where (map)", "lightness": "boardings per 1,000 residents"},
    {"panel": "5 revenue tile"},
    {"panel": "6 journeys by mode (bars)", "x": "mode", "y": "journeys change %", "hue": "mode"},
]
cc = dashlib.channel_conflicts(panels)
used = list(MODE_COLOR.values())
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    print("PART D — CHANNEL PLAN (dashlib.channel_conflicts)")
    print("  conflicts :", cc["conflicts"] or "none", "| ok =", cc["ok"])
    print("  redundant (deliberate, Week 2):", cc["redundant"])
    print("  positional (reported, not flagged):", cc["positional"])
    print("  one meaning per channel: hue = mode (every panel); lightness = boardings per 1,000 (map only);")
    print("  ink / grey carry no variable (network line, tiles, grid).")
    print("\nPART D — PALETTE ACTUALLY USED (vizlib.cvd_report), hues = Metro, BRT, Bus, Ferry")
    for kind in ("deutan", "protan", "tritan"):
        vizlib.cvd_report(used, kind)
    print("\n  worst pair (OKLab delta-E), sim deutan:")
    try:
        print("  ", vizlib.worst_pair(used, kind="deutan"))
    except Exception as exc:
        print("  worst_pair unavailable:", exc)
    print("  identity is never colour alone: every mode also has its own marker shape "
          f"({MODE_MARKER}) and a direct label.")
txt = buf.getvalue()
print(txt)
assert cc["ok"], "channel conflicts — fix before drawing"
base = AUDIT.read_text().split("PART D — CHANNEL PLAN")[0].rstrip() + "\n\n"
AUDIT.write_text(base + txt)

# ------------------------------------------------------------ the screen
fig = plt.figure(figsize=(15, 9.2))
axd = dashlib.dashboard_grid(
    fig, [["kpi", "slope", "mix"], ["map", "fare_kpi", "fare"]],
    headline="On-time rose 1.7 points only because the mix moved to Metro — every one of the four modes got less punctual",
    standfirst=("Departures operated, 2025 Q2 → 2026 Q2 (complete quarters) · on-time = departures on time ÷ departures operated · "
                "fares in JOURNEYS, 2025-04 → 2026-08 · map in boardings per 1,000 residents, 12 months to 2026-08-31"),
    height_ratios=[1, 1.25], width_ratios=[1.0, 1.2, 1.2], hspace=0.42, wspace=0.42, top=0.86)
fig.subplots_adjust(bottom=0.07)
W = lambda t, n: "\n".join(textwrap.wrap(t, n))

# 1 headline tile — the number, with its caveat inside the tile
dashlib.kpi_tile(axd["kpi"], "Network on-time, 2026 Q2", dec["rate_after"], delta=f"{dec['change']:+.2f} pts vs 2025 Q2",
                 note=W(f"…but all 4 modes fell ({g.delta.min():+.2f} to {g.delta.max():+.2f} pts). "
                      "'Improving' is mix, not performance.", 34),
                 good="neutral", fmt="{:.2f}%")
axd["kpi"].set_title("1  The Authority's headline", loc="left", fontsize=10.5)

# 2 is it real? slope chart, one line per mode, network in ink
ax = axd["slope"]
xs = [0, 1]
for mode in MODES:
    ax.plot(xs, [g.rate_before[mode], g.rate_after[mode]], color=MODE_COLOR[mode], marker=MODE_MARKER[mode], ms=7, lw=2)
    ax.text(-0.04, g.rate_before[mode], f"{mode} {g.rate_before[mode]:.1f}", ha="right", va="center", fontsize=8.5,
            color=MODE_COLOR[mode], fontweight="bold")
    ax.text(1.04, g.rate_after[mode], f"{g.rate_after[mode]:.1f}  ({g.delta[mode]:+.2f})", ha="left", va="center", fontsize=8.5,
            color=MODE_COLOR[mode], fontweight="bold")
ax.plot(xs, [dec["rate_before"], dec["rate_after"]], color=PALETTE["ink"], lw=2.6, ls="--", marker="o", ms=6, mfc="white")
ax.text(-0.04, dec["rate_before"] - 0.2, f"NETWORK {dec['rate_before']:.1f}", ha="right", va="top", fontsize=8.5, fontweight="bold")
ax.text(1.04, dec["rate_after"] + 0.9, f"NETWORK {dec['rate_after']:.1f}  ({dec['change']:+.2f})", ha="left", va="bottom",
        fontsize=8.5, fontweight="bold")
ax.set_xlim(-0.8, 1.9); ax.set_ylim(70, 99)
ax.set_xticks(xs); ax.set_xticklabels(["2025 Q2", "2026 Q2"])
ax.set_ylabel("")
ax.grid(False)
ax.set_title("2  Is it real? Departures on time, %: each mode fell", loc="left", fontsize=10.5)
ax.text(0.5, 0.03, f"+{dec['change']:.2f} = within {dec['within']:+.2f} + mix {dec['mix']:+.2f} pts",
        transform=ax.transAxes, ha="center", fontsize=9, fontweight="bold", color=PALETTE["ink"])

# 3 why — dumbbell of departure share by mode
ax = axd["mix"]
for i, mode in enumerate(MODES[::-1]):
    s0, s1 = g.share_before[mode], g.share_after[mode]
    ax.annotate("", xy=(s1, i), xytext=(s0, i), arrowprops=dict(arrowstyle="-|>", color=MODE_COLOR[mode], lw=2))
    ax.plot([s0], [i], marker=MODE_MARKER[mode], mfc="white", mec=MODE_COLOR[mode], mew=1.8, ms=8, ls="none", zorder=5)
    ax.plot([s1], [i], marker=MODE_MARKER[mode], color=MODE_COLOR[mode], ms=8, ls="none")
    ax.text(max(s0, s1) + 4.5, i, f"{s0:.1f} → {s1:.1f}%", va="center", fontsize=8.5, color=MODE_COLOR[mode], fontweight="bold")
ax.set_yticks(range(4)); ax.set_yticklabels(MODES[::-1])
ax.set_xlim(0, 100); ax.set_ylim(-0.6, 3.6)
ax.set_xlabel("Share of all departures operated, % (hollow = 2025 Q2, solid = 2026 Q2)")
ax.set_title("3  Why: Metro doubled its share, Bus shrank", loc="left", fontsize=10.5)

# 4 where — normalized map, lightness only
ax = axd["map"]
feats = geolib.read_geojson(DATA / "regions.geojson")
rate = (reg.set_index("code").boardings_annual / reg.set_index("code").population * 1000)
edges = geolib.choropleth(ax, feats, rate.reindex([f["code"] for f in feats]).to_dict(), scheme="natural", k=5, cmap="Greys",
                          legend_title="Boardings per 1,000 residents\n(Jenks breaks)", legend_loc="lower left",
                          legend_anchor=(1.0, 0.0))
ax.set_title("4  Where: riding per head, not per district", loc="left", fontsize=10.5)
top3 = ", ".join(rate.nlargest(3).index)
ax.text(1.0, 1.0, f"Highest rate:\n{top3}\n(a count map says\nD17, D09, D13:\na population map)", transform=ax.transAxes,
        fontsize=8, va="top", color=PALETTE["ink_soft"])

# 5 revenue tile
dashlib.kpi_tile(axd["fare_kpi"], "Fare revenue, 2025-04 → 2026-08", f"{r_tot:+.1f}%", delta=f"journeys only {j_tot:+.1f}%",
                 note=W(f"Fare per journey is flat in every mode ({fpj_chg.min():+.1f}% to {fpj_chg.max():+.1f}%): revenue rose by "
                      "mix toward the dearer Metro, not by price.", 36), good="neutral")
axd["fare_kpi"].set_title("5  Is the fare box recovering?", loc="left", fontsize=10.5)

# 6 journeys change by mode, zero baseline
ax = axd["fare"]
ax.bar(MODES, j_chg.values, color=[MODE_COLOR[m] for m in MODES], width=0.6,
       hatch=None, edgecolor="white")
for i, m in enumerate(MODES):
    ax.text(i, j_chg[m] + (4 if j_chg[m] >= 0 else -4), f"{MODE_MARKER[m] and ''}{j_chg[m]:+.1f}%", ha="center",
            va="bottom" if j_chg[m] >= 0 else "top", fontsize=9, fontweight="bold", color=MODE_COLOR[m])
ax.axhline(0, color=PALETTE["ink"], lw=0.9)
ax.set_ylim(-55, 120)
ax.set_ylabel("Change in journeys, %")
ax.set_title("6  Journeys: Metro doubled, Bus and Ferry fell", loc="left", fontsize=10.5)

vizlib.save_fig(fig, HERE / "partD_screen.png", textwrap.fill(
    "Windows: punctuality 2025 Q2 (Apr–Jun 2025) vs 2026 Q2 (Apr–Jun 2026), both complete; on-time is a ratio of sums, mix/within by "
    "dashlib.rate_decomposition (exact, Kitagawa). 7 rows with impossible on-time counts excluded; 63 unfiled mode-days are gaps, "
    "not zeros. Fares: JOURNEYS (not boardings; 1,000 journeys ≈ 1,300 boardings), complete months 2025-04 to 2026-08, "
    "'All tickets' subtotal rows excluded, 2026-09 partial and omitted. Map: boardings attributed by the register ÷ residents, "
    "equal-area, Jenks breaks "
    + ", ".join(f"{e:,.0f}" for e in edges) + "; D00 excluded. " + SOURCE, 190))
print("wrote partD_screen.png")
