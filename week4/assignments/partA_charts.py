"""
Week 4 · Part A — rebuild nine charts, then take them apart.

For every case: (left) the chart exactly as the recipe says, (right) the
redesign. Every mechanism number quoted in partA_diagnosis.pdf is printed here.

    python3 partA_charts.py        # writes partA_case01.png ... partA_case09.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import tslib
from vizlib import PALETTE, style_defaults, save_fig

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")
BLUE, ORANGE, GREEN = PALETTE["series"]
GREY = PALETTE["muted"]
SRC = "Synthetic course data, CDB601220 Week 4."
style_defaults()
plt.rcParams['axes.titlesize'] = 10


def hdr(n, title):
    print(f"\n{'=' * 72}\nCASE {n} · {title}\n{'=' * 72}")


def new(n, width=12.5, h=4.4):
    fig, (a, b) = plt.subplots(1, 2, figsize=(width, h))
    return fig, a, b


def done(fig, n, note):
    path = os.path.join(HERE, f"partA_case{n:02d}.png")
    fig.tight_layout()
    save_fig(fig, path, note=f"{note}  {SRC}")
    plt.close(fig)


# ----------------------------------------------------------------- case 1
hdr(1, "month sorted as text")
d = pd.read_csv(f"{D}/case01_orders_stringdate.csv")
bad = d.sort_values("month").reset_index(drop=True)          # the recipe
steps = np.diff(bad.orders.to_numpy())
print("recipe order (text sort):", bad.month.tolist()[:14], "...")
print("self-check drops:", steps[steps < 0].tolist(),
      "| rises before 1st drop:", int((steps[:np.argmax(steps < 0)] > 0).sum()) + 1, "points")
d["date"] = pd.to_datetime(d.month, format="%Y-%m")
good = d.sort_values("date").set_index("date")
print("is the true series monotone?", good.orders.is_monotonic_increasing,
      "| Jan24->Dec25:", good.orders.iloc[0], "->", good.orders.iloc[-1],
      f"({good.orders.iloc[-1] / good.orders.iloc[0] - 1:+.1%})")
print("worst month-on-month change in true series:",
      int(good.orders.diff().min()), "(min)", int(good.orders.diff().max()), "(max)")
print("rows whose string position != chronological position:",
      int((bad.month != good.month.str.replace(r"-(\d)$", r"-\1", regex=True).values).sum()))
fig, a, b = new(1)
a.plot(range(24), bad.orders, marker="o", color=BLUE)
a.set_ylim(0, 7000)
a.set_xticks(range(0, 24, 3)); a.set_xticklabels(bad.month.iloc[::3], fontsize=7)
a.set_title("As published: 'orders peak in Q1 and collapse'")
a.annotate("−958", (9.5, 4800), color=ORANGE, fontsize=9)
a.annotate("−978", (20.5, 5600), color=ORANGE, fontsize=9)
a.set_ylabel("Orders per month (sum)")
b.plot(good.index, good.orders, marker="o", color=BLUE)
b.set_ylim(0, 7000)
b.set_title("Parsed as dates: orders rose every month, +52%")
b.set_ylabel("Orders per month (sum)")
done(fig, 1, "Redesign: month parsed with format='%Y-%m' and sorted as datetime.")

# ----------------------------------------------------------------- case 2
hdr(2, "plotted by row number across a closure")
d = pd.read_csv(f"{D}/case02_shop_closed.csv", parse_dates=["date"])
gap_i = int(np.argmax(d.date.diff().dt.days.fillna(1) > 1))
gap = d.date.iloc[gap_i] - d.date.iloc[gap_i - 1]
print(f"rows={len(d)} first={d.sales_pkr_k.iloc[0]} last={d.sales_pkr_k.iloc[-1]} "
      f"rise={d.sales_pkr_k.iloc[-1] / d.sales_pkr_k.iloc[0] - 1:+.1%}")
print(f"calendar span = {(d.date.max() - d.date.min()).days + 1} days vs {len(d)} rows "
      f"-> {(d.date.max() - d.date.min()).days + 1 - len(d)} unrecorded days")
print(f"gap: {d.date.iloc[gap_i - 1].date()} -> {d.date.iloc[gap_i].date()} "
      f"({gap.days - 1} days with no trading)")
pre, post = d.iloc[:gap_i], d.iloc[gap_i:]
for name, x in [("before", pre), ("after", post)]:
    t = (x.date - x.date.min()).dt.days
    sl = np.polyfit(t, x.sales_pkr_k, 1)[0]
    print(f"{name}: n={len(x)} first={x.sales_pkr_k.iloc[0]} last={x.sales_pkr_k.iloc[-1]} "
          f"slope={sl:+.3f} k/day")
print(f"step across the closure: {pre.sales_pkr_k.iloc[-1]} -> {post.sales_pkr_k.iloc[0]} "
      f"= {post.sales_pkr_k.iloc[0] - pre.sales_pkr_k.iloc[-1]:+d}k in one reopening")
r = np.arange(len(d))
sl_row = np.polyfit(r, d.sales_pkr_k, 1)
t = (d.date - d.date.min()).dt.days
sl_cal = np.polyfit(t, d.sales_pkr_k, 1)
print(f"whole-series trend line: row-indexed slope {sl_row[0]:+.3f}/row, "
      f"calendar slope {sl_cal[0]:+.3f}/day — both are fitted ACROSS the step")
fig, a, b = new(2)
a.plot(r, d.sales_pkr_k, color=BLUE)
a.plot(r, np.polyval(sl_row, r), color=ORANGE, ls="--")
a.set_title("As published: 'grew steadily, +22%'")
a.set_xlabel("Row number (not a date)"); a.set_ylabel("Sales, PKR thousand per day")
a.set_ylim(0, 300)
cal = d.set_index("date").sales_pkr_k.reindex(pd.date_range(d.date.min(), d.date.max()))
b.plot(cal.index, cal, color=BLUE)
b.axvspan(d.date.iloc[gap_i - 1], d.date.iloc[gap_i], color=GREY, alpha=0.25)
b.text(d.date.iloc[gap_i - 1] + pd.Timedelta(days=2), 40, "shop closed\n21 days,\nno data", fontsize=8,
       color=PALETTE["ink_soft"])
for x, c in [(pre, GREEN), (post, GREEN)]:
    tt = (x.date - d.date.min()).dt.days
    p = np.polyfit(tt, x.sales_pkr_k, 1)
    b.plot(x.date, np.polyval(p, tt), color=c, ls="--", lw=1.4)
b.set_ylim(0, 300)
b.set_title("Calendar axis: flat either side; the whole rise is the reopening step")
b.set_ylabel("Sales, PKR thousand per day (daily, no resampling)")
done(fig, 2, "Redesign: calendar axis, gap left as NaN, separate trend per trading spell.")

# ----------------------------------------------------------------- case 3
hdr(3, "a level resampled with sum()")
bw = pd.read_csv(f"{D}/case03_bandwidth_levels.csv", parse_dates=["ts"]).set_index("ts")
a_ = tslib.audit_index(bw, "h")
print("audit:", {k: a_[k] for k in ("monotonic", "n_duplicated", "n_missing", "span")})
hrs = bw.groupby(bw.index.to_period("M")).size()
print("hours observed: June", hrs.iloc[0], "of 720 | July", hrs.iloc[1], "of 744")
sumd = bw.concurrent_users.resample("D").sum()
meand = bw.concurrent_users.resample("D").mean()
maxd = bw.concurrent_users.resample("D").max()
for lab, s in [("sum", sumd), ("mean", meand), ("max (daily peak)", maxd)]:
    j, l = s["2025-06"].mean(), s["2025-07"].mean()
    print(f"daily {lab:<17} June {j:9.1f}  July {l:9.1f}  change {l / j - 1:+.1%}")
hpd = bw.groupby(bw.index.date).size()
print("mean hours reported per day: June", round(hpd.iloc[:30].mean(), 1),
      " July", round(hpd.iloc[30:].mean(), 1))
byt = bw.bytes_served.resample("D").sum()
print(f"flow check (bytes, sum is legal) daily-sum: June {byt['2025-06'].mean():.3e} "
      f"July {byt['2025-07'].mean():.3e} change {byt['2025-07'].mean() / byt['2025-06'].mean() - 1:+.1%}"
      f"  | bytes per OBSERVED hour change "
      f"{bw.bytes_served['2025-07'].mean() / bw.bytes_served['2025-06'].mean() - 1:+.1%}")
fig, a, b = new(3)
a.plot(sumd.index, sumd, color=BLUE)
a.set_ylim(0, 16000)
a.axvline(pd.Timestamp("2025-07-01"), color=ORANGE, ls=":")
a.set_title("As published: daily sum of users, '+43% on 1 July'")
a.set_ylabel("Concurrent users, summed over reported hours (invalid)")
b.plot(maxd.index, maxd, color=BLUE, lw=1.2, label="daily peak (max)")
b.plot(meand.index, meand, color=GREEN, lw=1.2, label="daily mean")
b.set_ylim(0, 1000)
b.axvline(pd.Timestamp("2025-07-01"), color=ORANGE, ls=":")
b.set_title("A level takes mean or max: no step on 1 July")
b.set_ylabel("Concurrent users (daily mean / daily max)")
b.legend(loc="lower right")
done(fig, 3, "Redesign: level aggregated with mean and max over the hours actually recorded.")

# ----------------------------------------------------------------- case 4
hdr(4, "trailing mean reads the turn half a window late")
c = pd.read_csv(f"{D}/case04_intervention_lag.csv", parse_dates=["date"]).set_index("date").conversion_pct
lg = tslib.lag_at_turn(c, 31, how="min")
print(f"trailing-31 minimum: {lg['trailing_turn'].date()} | centred-31 minimum: "
      f"{lg['centred_turn'].date()} | lag {lg['lag_periods']} d vs half-window {lg['half_window']}")
# independent check: piecewise-linear (hinge) fit on the raw series
x = np.arange(len(c))
best = min(((((np.c_[np.ones(len(c)), x, np.maximum(0, x - k)] @
               np.linalg.lstsq(np.c_[np.ones(len(c)), x, np.maximum(0, x - k)], c.values, rcond=None)[0]
               - c.values) ** 2).sum(), k) for k in range(20, len(c) - 20)))
k_hat = best[1]
print(f"hinge (broken-stick) fit on RAW data puts the break at {c.index[k_hat].date()} "
      f"-> the checkout fix is 'live' ~{(lg['trailing_turn'] - c.index[k_hat]).days} days before the trailing line says")
print("7-day centred minimum:", c.rolling(7, center=True).mean().idxmin().date())
tr, ce = c.rolling(31).mean(), c.rolling(31, center=True).mean()
fig, a, b = new(4)
a.plot(c.index, c, color=GREY, lw=0.8, label="raw daily")
a.plot(tr.index, tr, color=BLUE, label="31-day trailing mean")
a.axvline(lg["trailing_turn"], color=ORANGE, ls="--")
a.text(lg["trailing_turn"], c.max() * 0.99, " 7 Sep", color=ORANGE, fontsize=9, va="top")
a.set_title("As published: 'started working on 7 September'")
a.set_ylabel("Conversion, % of sessions (daily)"); a.legend(loc="lower left")
b.plot(c.index, c, color=GREY, lw=0.8, label="raw daily")
b.plot(tr.index, tr, color=BLUE, label="31-day trailing (lags)")
b.plot(ce.index, ce, color=GREEN, label="31-day centred (no lag)")
b.axvline(c.index[k_hat], color=ORANGE, ls="--")
b.text(c.index[k_hat], c.max() * 0.99, f" break ≈ {c.index[k_hat].strftime('%d %b')}", color=ORANGE, fontsize=9, va="top")
b.set_title("Centred window & broken-stick fit: the turn was ~late August")
b.set_ylabel("Conversion, % of sessions (daily)"); b.legend(loc="lower left")
done(fig, 4, "Window length 31 days named on both panels; centred version for diagnosis only.")

# ----------------------------------------------------------------- case 5
hdr(5, "window starts at the seasonal peak")
rv = pd.read_csv(f"{D}/case05_revenue_window.csv")
rv["m"] = pd.to_datetime(rv.month); rv = rv.set_index("m").revenue_pkr_m
w = rv["2025-05":"2025-11"]
print(f"n={len(w)} first={w.iloc[0]:.1f} last={w.iloc[-1]:.1f} change={w.iloc[-1] / w.iloc[0] - 1:+.1%}")
for y in (2023, 2024, 2025):
    a1, a2 = rv[f"{y}-05"].iloc[0], rv[f"{y}-11"].iloc[0]
    print(f"  May->Nov {y}: {a1:.1f} -> {a2:.1f} = {a2 / a1 - 1:+.1%}")
yoy = (rv / rv.shift(12) - 1).dropna()
print(f"year-on-year growth, every month of 2024-25: min {yoy.min():+.1%}  max {yoy.max():+.1%}  "
      f"mean {yoy.mean():+.1%}  (months negative: {(yoy < 0).sum()} of {len(yoy)})")
print(f"2025 annual revenue vs 2023: {rv['2025'].sum():.0f} vs {rv['2023'].sum():.0f} ({rv['2025'].sum() / rv['2023'].sum() - 1:+.1%})")
fig, a, b = new(5)
a.plot(w.index, w, marker="o", color=BLUE); a.set_ylim(0, 180)
a.set_title("As published: 'fallen six straight months, −41.9%'")
a.set_ylabel("Revenue, PKR million per month (sum)")
cp = rv.to_frame("v"); cp["y"], cp["mo"] = cp.index.year, cp.index.month
for i, (yv, g) in enumerate(cp.groupby("y")):
    b.plot(g.mo, g.v, marker="o", ms=3.5, color=[GREY, GREEN, BLUE][i], label=str(yv))
b.set_xticks(range(1, 13)); b.set_ylim(0, 180)
b.axvspan(5, 11, color=GREY, alpha=0.12)
b.set_title("Cycle plot: same May→Nov fall every year; each year higher")
b.set_xlabel("Month"); b.set_ylabel("Revenue, PKR million per month (sum)"); b.legend()
done(fig, 5, "Redesign: each year overlaid on a Jan–Dec axis (cycle plot), y from zero.")

# ----------------------------------------------------------------- case 6
hdr(6, "partial final month")
o = pd.read_csv(f"{D}/case06_monthly_partial.csv", parse_dates=["date"]).set_index("date").orders
ms = o.resample("MS").agg(["sum", "count", "mean"])
print(ms.round(1).to_string())
print(f"Oct total {ms['sum'].iloc[-1]:,} vs Sep {ms['sum'].iloc[-2]:,} = {ms['sum'].iloc[-1] / ms['sum'].iloc[-2]:.0%}; "
      f"last day recorded {o.index.max().date()} ({ms['count'].iloc[-1]} of 31 days)")
print(f"daily mean: Sep {ms['mean'].iloc[-2]:.1f} -> Oct {ms['mean'].iloc[-1]:.1f} "
      f"({ms['mean'].iloc[-1] / ms['mean'].iloc[-2] - 1:+.1%})")
fig, a, b = new(6)
a.bar(ms.index, ms["sum"], width=22, color=BLUE)
a.set_ylim(0, 12500); a.set_title("As published: 'orders collapsed in October'")
a.set_ylabel("Orders per month (sum)")
cols = [BLUE] * (len(ms) - 1) + [ORANGE]
b.bar(ms.index, ms["mean"], width=22, color=cols)
b.bar(ms.index[-1], ms["mean"].iloc[-1], width=22, facecolor="none", edgecolor=ORANGE, hatch="///")
b.set_ylim(0, 420)
b.text(ms.index[-1], ms["mean"].iloc[-1] + 8, "partial\n11 of 31 days", ha="center", fontsize=8, color=ORANGE)
b.set_title("Orders per recorded day: October is the highest month yet")
b.set_ylabel("Orders per day (mean of recorded days)")
done(fig, 6, "Redesign: rate per recorded day; partial month hatched and labelled.")

# ----------------------------------------------------------------- case 7
hdr(7, "stacked area: volatility leaks upward")
p = pd.read_csv(f"{D}/case07_stacked_products.csv")
p["m"] = pd.to_datetime(p.month); p = p.set_index("m").drop(columns="month")
tot = p.sum(axis=1)
print(f"total envelope {tot.min():.0f} – {tot.max():.0f}")
print("level SD (PKR m):  ", p.std().round(1).to_dict())
print("month-on-month SD: ", p.diff().std().round(1).to_dict())
print(f"top edge of D (= total) month-on-month SD: {tot.diff().std():.1f}  vs D's own thickness SD {p.product_d.diff().std():.1f}")
print(f"product_b share of the volatility under D's baseline: B SD {p.product_b.std():.1f} of cumulative-below SD "
      f"{p[['product_a','product_b','product_c']].sum(axis=1).std():.1f}")
fig, a, b = new(7, width=12.5, h=4.4)
a.stackplot(p.index, [p[c] for c in p.columns], colors=[BLUE, GREY, GREEN, PALETTE["series_4th"]],
            labels=[c.replace("_", " ").title() for c in p.columns])
a.set_title("As published: stack with D on top 'looks erratic'")
a.set_ylabel("Revenue, PKR million per month"); a.legend(loc="lower left", ncol=2, fontsize=8)
for i, (c, col) in enumerate(zip(p.columns, [BLUE, ORANGE, GREEN, PALETTE["series_4th"]])):
    b.plot(p.index, p[c], color=col, lw=1.8 if c == "product_b" else 1.4,
           label=f"{c.replace('_', ' ').title()} (SD {p[c].std():.1f})")
    b.text(p.index[-1] + pd.Timedelta(days=12), p[c].iloc[-1], c[-1].upper(), color=col, fontsize=9, va="center")
b.set_ylim(0, 300)
b.set_title("Unstacked: B is the volatile one; D is the steadiest line")
b.set_ylabel("Revenue, PKR million per month"); b.legend(loc="upper left", ncol=2, fontsize=8)
done(fig, 7, "Redesign: lines on one shared zero-based axis (unstack).")

# ----------------------------------------------------------------- case 8
hdr(8, "non-exclusive parts drawn as a pie")
q = pd.read_csv(f"{D}/case08_channel_attrib.csv")
t = [c for c in q.columns if c.startswith("touch_")]
ex = tslib.exclusivity_check(q, t)
print("shares %:", ex["shares_pct"])
print(f"sum = {ex['sum_pct']}%  exclusive = {ex['exclusive']}  customers touched by 2+ channels: "
      f"{ex['n_multi']} of {ex['n']} ({ex['pct_multi']}%)  untouched: {ex['n_zero']}")
n_touch = q[t].sum(axis=1)
print("channels per customer:", n_touch.value_counts().sort_index().to_dict())
only = {c: int(((q[c]) & (n_touch == 1)).sum()) for c in t}
print("touched ONLY by that channel (n, % of customers):",
      {k: (v, round(v / len(q) * 100, 1)) for k, v in only.items()}, "sum",
      round(sum(only.values()) / len(q) * 100, 1))
# first-order revenue check: revenue per customer by number of touches
print("mean revenue (PKR) by # channels:", q.groupby(n_touch).revenue_pkr.mean().round(0).to_dict())
fig, a, b = new(8)
a.pie([ex["shares_pct"][c] for c in t], labels=[f"{c[6:].title()} {ex['shares_pct'][c]:.1f}%" for c in t],
      colors=[BLUE, ORANGE, GREEN, PALETTE["series_4th"]], startangle=90, counterclock=False)
a.set_title("As published: 'search drives 43%'\n(the four slices sum to 131%)")
sh = pd.Series({c[6:].title(): ex["shares_pct"][c] for c in t}).sort_values()
b.barh(sh.index, sh.values, color=BLUE, label="touched by this channel (any)")
b.barh(sh.index, [only["touch_" + k.lower()] / len(q) * 100 for k in sh.index], color=ORANGE, label="touched ONLY by this channel")
b.legend(loc="lower right")
for i, (k, v) in enumerate(sh.items()):
    b.text(v + 0.8, i, f"{v:.1f}% touched", va="center", fontsize=8)
b.set_xlim(0, 55); b.axvline(0, color=PALETTE["ink"], lw=0.8)
b.set_xlabel("% of 4,000 customers")
b.set_title("Bars: each channel is its own yes/no\n27.6% of customers had 2+ touches")
done(fig, 8, "Redesign: one bar per channel against all customers; shares not summed.")

# ----------------------------------------------------------------- case 9
hdr(9, "a rising share of a falling total")
z = pd.read_csv(f"{D}/case09_premium_share.csv")
z["share"] = z.premium_revenue_pkr_m / z.total_revenue_pkr_m * 100
print(z.round(1).to_string(index=False))
print(f"share {z.share.iloc[0]:.1f}% -> {z.share.iloc[-1]:.1f}% | premium revenue {z.premium_revenue_pkr_m.iloc[0]:.0f} -> "
      f"{z.premium_revenue_pkr_m.iloc[-1]:.0f} ({z.premium_revenue_pkr_m.iloc[-1] / z.premium_revenue_pkr_m.iloc[0] - 1:+.1%}) | "
      f"total {z.total_revenue_pkr_m.iloc[0]:.0f} -> {z.total_revenue_pkr_m.iloc[-1]:.0f} "
      f"({z.total_revenue_pkr_m.iloc[-1] / z.total_revenue_pkr_m.iloc[0] - 1:+.1%})")
z["other"] = z.total_revenue_pkr_m - z.premium_revenue_pkr_m
print(f"non-premium revenue {z.other.iloc[0]:.0f} -> {z.other.iloc[-1]:.0f} ({z.other.iloc[-1] / z.other.iloc[0] - 1:+.1%})")
fig, a, b = new(9)
a.plot(z.quarter, z.share, marker="o", color=BLUE); a.set_ylim(0, 45)
a.annotate("38.0%", (7, 38), xytext=(6.1, 41), color=ORANGE)
a.set_title("As published: 'premium is 38% of revenue — a record'")
a.set_ylabel("Premium share of revenue, % of quarter total")
b.bar(z.quarter, z.premium_revenue_pkr_m, color=BLUE, label="Premium")
b.bar(z.quarter, z.other, bottom=z.premium_revenue_pkr_m, color=GREY, label="Everything else")
for i, r_ in z.iterrows():
    b.text(i, r_.premium_revenue_pkr_m / 2, f"{r_.premium_revenue_pkr_m:.0f}", ha="center", color="white", fontsize=8)
b.set_title("Premium flat at ~PKR 230m; the other 40% of the base left")
b.set_ylabel("Revenue, PKR million per quarter (sum)"); b.legend(loc="upper right")
done(fig, 9, "Redesign: the two absolute quantities behind the share, stacked, zero baseline.")
print("\nAll nine rebuilt and redesigned.")
