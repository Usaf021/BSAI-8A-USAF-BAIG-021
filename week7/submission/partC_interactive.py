"""Part C — a linked brush on the route scatter.

  python3 partC_interactive.py          headless: writes partC_default.png (default state)
                                        and partC_brushed.png (a scripted brush, via simulate())
  python3 partC_interactive.py --show   opens the interactive window: drag a rectangle on the
                                        scatter; press 'r' or click Reset to return to the default.

Left: route crowding vs on-time (each dot = one route). Right: boardings of the SELECTED routes
by mode, each route counted once. Nothing here is split by district (that would count a route
up to 4 times, 3.096x - see partC_contract.md).
"""
import sys
import matplotlib
if "--show" not in sys.argv:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import HERE, MODES, MODE_COLOR, MODE_MARKER, SOURCE, load_clean
import vizlib
import dashlib
from vizlib import PALETTE

vizlib.style_defaults()
_, rt, _, _ = load_clean()
u = rt.dropna(subset=["punctuality_pct"]).reset_index(drop=True)   # 33 routes (3 codes excluded)
TOTAL = u.boardings_annual.sum()
MIN_N = 5     # below this many routes the readout is flagged as too few to generalise

fig, (ax, bx) = plt.subplots(1, 2, figsize=(12, 5.4), gridspec_kw={"width_ratios": [1.25, 1], "wspace": 0.28})
fig.subplots_adjust(bottom=0.3, top=0.84)
dots = {}
for mode in MODES:
    s = u[u["mode"] == mode]
    dots[mode] = (ax.scatter(s.crowding_index, s.punctuality_pct, color=MODE_COLOR[mode], marker=MODE_MARKER[mode],
                             s=55, edgecolor="white", lw=0.8, label=f"{mode} ({len(s)})", zorder=3), s.index)
ax.axvline(1.0, color=PALETTE["ink_soft"], lw=0.9, ls="--")
ax.set_xlabel("Crowding index (peak passengers ÷ capacity)")
ax.set_ylabel("Route on-time, % of departures")
ax.legend(loc="lower right", frameon=False)
ax.set_title("Drag a box to select routes")
readout = fig.text(0.07, 0.17, "", fontsize=10, va="top", ha="left", color=PALETTE["ink"])


def repaint(mask):
    sel = u[mask.values]
    for mode, (sc, idx) in dots.items():
        faded = ~mask.loc[idx].values
        fc = [PALETTE["grid"] if f else MODE_COLOR[mode] for f in faded]
        sc.set_facecolor(fc)
        sc.set_alpha(1.0)
    bx.clear()
    by = sel.groupby("mode").boardings_annual.sum().reindex(MODES).fillna(0) / 1e6
    few = len(sel) < MIN_N
    bx.barh(MODES[::-1], by.values[::-1], color=[MODE_COLOR[m] for m in MODES[::-1]],
            hatch=None, alpha=0.45 if few else 1.0, height=0.6)
    bx.set_xlim(0, u.groupby("mode").boardings_annual.sum().max() / 1e6 * 1.08)
    bx.set_xlabel("Boardings, millions a year (each route counted once)")
    bx.set_title("All 33 routes" if mask.all() else f"{len(sel)} routes selected")
    share = sel.boardings_annual.sum() / TOTAL * 100
    msg = (f"n = {len(sel)} of {len(u)} routes · {sel.boardings_annual.sum() / 1e6:,.1f} M boardings "
           f"= {share:.1f}% of the 33-route total.")
    if few:
        msg += f"\nFEWER THAN {MIN_N} ROUTES — too few to say anything about a mode."
    if not mask.all():
        msg += "\nA selection is not a district: districts overlap, so do not add by district."
    readout.set_text(msg)
    fig.canvas.draw_idle()


brush = dashlib.LinkedBrush(ax, u, "crowding_index", "punctuality_pct", on_select=repaint)
brush.clear()                                   # the default state: everything selected
fig.suptitle("Route punctuality, crowding and boardings — 12 months to 2026-08-31, boardings (not journeys)",
             x=0.01, ha="left", fontsize=12, fontweight="bold")
def save(path, note):
    vizlib.save_fig(fig, path, note)
    fig.texts[-1].remove()          # the source stamp belongs to one export only


save(HERE / "partC_default.png",
     "Default state = all 33 routes, nothing selected. 3 routes with punctuality code 999 excluded. " + SOURCE)

if "--show" in sys.argv:
    from matplotlib.widgets import Button
    rb = Button(fig.add_axes([0.92, 0.93, 0.07, 0.05]), "Reset")
    rb.on_clicked(lambda _e: brush.clear())
    fig.canvas.mpl_connect("key_press_event", lambda e: brush.clear() if e.key == "r" else None)
    plt.show()
else:
    # a scripted brush, the headless way to test one: the crowded BRT/Metro corner
    mask = brush.simulate((1.0, 80.0, 1.4, 100.0))
    print(f"scripted brush selected {int(mask.sum())} routes: {u.loc[mask, 'mode'].value_counts().to_dict()}")
    save(HERE / "partC_brushed.png", "Scripted brush (simulate): crowding 1.0-1.4, on-time 80-100%. " + SOURCE)
    brush.clear()
    assert brush.mask.all(), "reset must restore the default view"
    print("reset restores all", int(brush.mask.sum()), "routes")
