"""
Week 4 · Part D — the 2x2 e-commerce review figure.

    python3 partD_figure.py   ->  partD_figure.png (300 dpi) + partD_log.txt
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
import numpy as np
import pandas as pd
import squarify

import cleaning
from vizlib import PALETTE, style_defaults, save_fig

HERE = os.path.dirname(os.path.abspath(__file__))
style_defaults()
plt.rcParams["axes.titlesize"] = 10.5
WINDOW = 7                      # fixed before plotting: the cycle removed is weekly (Part B.1)
BLUE, ORANGE, GREEN = PALETTE["series"]
PARENT_HUES = {"Mobile": BLUE, "Computing": ORANGE, "Lifestyle": GREEN, "Audio & Imaging": PALETTE["series_4th"]}

lines = []
def log(*a):
    s = " ".join(str(x) for x in a); print(s); lines.append(s)

# ---------------------------------------------------------------- sessions
h, daily, L = cleaning.load_clean(log)
s = daily.sessions
roll = s.rolling(WINDOW, center=True, min_periods=5).mean().where(s.notna())

# ---------------------------------------------------------------- catalogue
cat = pd.read_csv(os.path.join(cleaning.D, "revenue_catalogue.csv"))
n0 = len(cat)
dup = cat[cat.sku.duplicated(keep=False)]
log(f"\n[9] catalogue: {n0} SKU rows; SKU {dup.sku.iloc[0]} appears under two parents "
    f"({' and '.join(dup.category + '/' + dup.subcategory)}); sku_name '{dup.sku_name.iloc[0]}' belongs to Audio -> "
    "dropped the Lifestyle/Wearables copy (1 row). A child must have one parent.")
cat = cat[~(cat.sku.duplicated(keep=False) & (cat.subcategory == "Wearables"))]
neg = cat[cat.net_revenue_pkr_m < 0]
log(f"[10] {len(neg)} SKUs have negative net revenue (total {neg.net_revenue_pkr_m.sum():.2f} PKR m, "
    f"{neg.net_revenue_pkr_m.sum() / cat.net_revenue_pkr_m.sum() * 100:.3f}% of the whole). They are netted inside their "
    "sub-category (every sub-category total stays positive); no SKU-level area is drawn, so no negative is ever an area.")
sub = cat.groupby(["category", "subcategory"]).net_revenue_pkr_m.sum().reset_index()
assert (sub.net_revenue_pkr_m > 0).all()
sub["share"] = sub.net_revenue_pkr_m / sub.net_revenue_pkr_m.sum() * 100
assert abs(sub.share.sum() - 100) < 1e-6
ref = pd.read_csv(os.path.join(cleaning.D, "shares_eight.csv")).set_index("subcategory").share_pct
dev = (sub.set_index("subcategory").share - ref).abs()
log(f"[11] self-check vs shares_eight.csv: max deviation {dev.max():.2f} pp (limit 0.3) -> "
    f"{'PASS' if dev.max() < 0.3 else 'FAIL'}")
log("     tree check: every sub-category has exactly one parent:",
    bool((cat.groupby('subcategory').category.nunique() == 1).all()))
log("     'Other' bucket: none needed — 4 parents, 8 children; nothing folded away.")

# ---------------------------------------------------------------- figure
fig, axs = plt.subplots(2, 2, figsize=(15, 10.5))
a1, a2, a3, a4 = axs.ravel()

# panel 1: daily sessions
a1.plot(s.index, s, color=PALETTE["grid"], lw=0.9, label="raw daily sessions")
a1.plot(roll.index, roll, color=BLUE, lw=2.2, label=f"{WINDOW}-day centred rolling mean")
for d in L["missing_days"]:
    a1.axvspan(d, d + pd.Timedelta(days=1), color=PALETTE["muted"], alpha=0.35, lw=0)
a1.axvspan(L["tail_start"], s.index.max() + pd.Timedelta(days=1), color=ORANGE, alpha=0.12, lw=0)
a1.text(L["tail_start"], s.max() * 0.98, " partial\n Sep (11 d)", fontsize=7.5, color=ORANGE, va="top", ha="right")
bf = pd.Timestamp("2024-11-29")
a1.annotate("Black Friday\n113,710", (bf, s[bf]), xytext=(bf + pd.Timedelta(days=25), s[bf] * 0.93),
            arrowprops=dict(arrowstyle="-", color=PALETTE["ink_soft"]), fontsize=8)
a1.set_ylim(0)
r0, r1 = roll["2024-04-04":].dropna().iloc[0], roll.dropna().iloc[-1]
a1.set_title(f"Daily sessions rose from {r0 / 1000:.0f}k to {r1 / 1000:.0f}k a day, with a dip in spring 2025 ({WINDOW}-day rolling mean)")
a1.set_ylabel("Sessions per day (sum of hours)")
a1.legend(loc="upper left")
a1.text(0.99, 0.02, f"grey bars = {len(L['missing_days'])} days never recorded (gap, not zero)", transform=a1.transAxes,
        ha="right", fontsize=7.5, color=PALETTE["ink_soft"])

# panel 2: dow x hour heat map (hourly mean, observed values only)
hh = h.sessions.dropna()
heat = hh.groupby([hh.index.dayofweek, hh.index.hour]).mean().unstack()
im = a2.imshow(heat.values, aspect="auto", cmap=PALETTE["sequential"], origin="upper")
a2.set_yticks(range(7)); a2.set_yticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
a2.set_xticks(range(0, 24, 3)); a2.set_xticklabels([f"{x:02d}:00" for x in range(0, 24, 3)])
a2.grid(False)
for sp in a2.spines.values(): sp.set_visible(False)
pk = np.unravel_index(np.nanargmax(heat.values), heat.shape)
a2.set_title(f"Traffic peaks {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][pk[0]]} {pk[1]:02d}:00 and bottoms out at night, all week")
a2.set_xlabel("Hour of day"); a2.set_ylabel("Day of week")
cb = fig.colorbar(im, ax=a2, fraction=0.04, pad=0.02)
cb.set_label("Mean sessions per hour (mean of observed hours)"); cb.outline.set_visible(False)

# panel 3: nested treemap
a3.set_xlim(0, 100); a3.set_ylim(0, 100); a3.invert_yaxis(); a3.axis("off")
cats = sub.groupby("category").net_revenue_pkr_m.sum().sort_values(ascending=False)
crects = squarify.squarify(squarify.normalize_sizes(cats.values, 100, 100), 0, 0, 100, 100)
for (cname, cval), cr in zip(cats.items(), crects):
    kids = sub[sub.category == cname].sort_values("net_revenue_pkr_m", ascending=False)
    krects = squarify.squarify(squarify.normalize_sizes(kids.net_revenue_pkr_m.values, cr["dx"], cr["dy"]),
                               cr["x"], cr["y"], cr["dx"], cr["dy"])
    for i, ((_, k), kr) in enumerate(zip(kids.iterrows(), krects)):
        a3.add_patch(mp.Rectangle((kr["x"], kr["y"]), kr["dx"], kr["dy"], facecolor=PARENT_HUES[cname],
                                  alpha=1.0 if i == 0 else 0.62, edgecolor="white", lw=1.2))
        a3.text(kr["x"] + kr["dx"] / 2, kr["y"] + kr["dy"] / 2,
                f"{k.subcategory}\n{k.net_revenue_pkr_m:,.0f}\n{k.share:.1f}%", ha="center", va="center",
                color="white", fontsize=8.5 if kr["dx"] > 14 and kr["dy"] > 14 else 7, fontweight="bold",
                linespacing=1.2)
    a3.add_patch(mp.Rectangle((cr["x"], cr["y"]), cr["dx"], cr["dy"], fill=False, edgecolor="white", lw=3))
a3.legend([mp.Patch(color=PARENT_HUES[c]) for c in cats.index],
          [f"{c} ({v / cats.sum() * 100:.0f}%)" for c, v in cats.items()], loc="upper center",
          bbox_to_anchor=(0.5, 0.0), ncol=4, fontsize=8)
a3.set_title(f"Mobile and Computing hold {(cats['Mobile'] + cats['Computing']) / cats.sum():.0%} of the money — mass sits in a few blocks")
a3.text(0.5, -0.08, "block area = net revenue (PKR m); one hue per parent category", transform=a3.transAxes,
        ha="center", fontsize=7.5, color=PALETTE["ink_soft"])

# panel 4: sorted bars with values
bars = sub.sort_values("net_revenue_pkr_m")
a4.barh(bars.subcategory, bars.net_revenue_pkr_m, color=[PARENT_HUES[c] for c in bars.category])
for y, (_, r) in enumerate(bars.iterrows()):
    a4.text(r.net_revenue_pkr_m + 6, y, f"{r.net_revenue_pkr_m:,.1f}  ({r.share:.1f}%)", va="center", fontsize=8.5)
a4.set_xlim(0, bars.net_revenue_pkr_m.max() * 1.25)
a4.set_xlabel("Net revenue over the period, PKR million (sum of SKUs, returns deducted)")
a4.set_title(f"Phones lead Laptops by {bars.net_revenue_pkr_m.iloc[-1] - bars.net_revenue_pkr_m.iloc[-2]:,.0f} m; Drones are only {bars.share.iloc[0]:.1f}%")
a4.grid(axis="y", visible=False)

fig.tight_layout(h_pad=3, w_pad=2.5)
out = save_fig(fig, os.path.join(HERE, "partD_figure.png"),
               note=("Source: synthetic course data, CDB601220 Week 4 (sessions_hourly.csv, revenue_catalogue.csv). "
                     f"Cleaned: {L['dups']} duplicate hours removed, {L['sentinels']} sentinel (-1) hours treated as missing, "
                     f"{len(L['missing_days'])} unrecorded days left as gaps, 1 duplicate SKU dropped. Window {WINDOW} days, centred."))
plt.close(fig)
log("\nwrote", out)
open(os.path.join(HERE, "partD_log.txt"), "w").write("\n".join(lines))
