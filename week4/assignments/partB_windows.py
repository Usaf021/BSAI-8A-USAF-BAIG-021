"""
Week 4 · Part B — smoothing, windows and panel shape, computed.
Runs on the cleaned daily series from Part D.

    python3 partB_windows.py | tee partB_output.txt
"""
import io
import contextlib
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

import cleaning
import tslib

with contextlib.redirect_stdout(io.StringIO()):
    h, daily, L = cleaning.load_clean(lambda *a: None)
s = daily.sessions
sf = s.interpolate(limit_area="inside")   # used ONLY where a method needs a gap-free series (decompose); flagged below
n_gap = int(s.isna().sum())
print(f"Series: {len(s)} days, {n_gap} never recorded. audit_index:",
      {k: v for k, v in tslib.audit_index(s.dropna(), 'D').items() if k in ('monotonic', 'n_duplicated', 'n_missing', 'span', 'partial_tail', 'tail_period', 'tail_count')})

# ------------------------------------------------------------------ Q1
print("\n== Q1  window_report (centred) on the daily series, gaps left as NaN ==")
wr = tslib.window_report(s, (7, 28, 91))
cyc = {7: "weekly cycle (period 7)", 28: "weekly cycle (exactly 4 periods) + month-to-month noise",
       91: "weekly + monthly; starts to remove a quarter of the real trajectory"}
wr["cycle_removed"] = wr.window.map(cyc)
print(wr.to_string(index=False))
print("Choice: 7 days. A window must be a whole multiple of the cycle you want cancelled, otherwise the cycle leaks "
      "through as a ripple. 7 cancels the weekend rhythm completely and loses only 3 days at each end; "
      "28 also cancels it but erases the Black Friday and spring-2025 dip I want to show; 91 buries them. "
      "Chosen before plotting, for the cycle, not for smoothness.")

# ------------------------------------------------------------------ Q2
print("\n== Q2  three smoothers at 2024-11-29 (Black Friday) ==")
bf = pd.Timestamp("2024-11-29")
raw = s[bf]
med14 = s[bf - pd.Timedelta(days=15):bf + pd.Timedelta(days=15)].median()
mean14 = s.rolling(14, center=True, min_periods=7).mean()[bf]
median14 = s.rolling(14, center=True, min_periods=7).median()[bf]
ewma = s.ewm(span=14, adjust=False).mean()[bf]
print(f"raw {raw:,.0f}  | fortnight median around it ~{s[bf - pd.Timedelta(days=7):bf + pd.Timedelta(days=7)].median():,.0f}")
print(f"14-day centred MEAN   {mean14:,.0f}  (spike inflates it by {mean14 / median14 - 1:+.0%} vs the median)")
print(f"14-day centred MEDIAN {median14:,.0f}")
print(f"EWMA (span 14)        {ewma:,.0f}  (one-sided, spike enters at ~{2 / 15:.0%} weight and decays)")
print("Dashboard (monitoring): the mean/EWMA — a spike must be visible, that is what an alert is for. "
      "Quarterly report: the median — one event should not drag the trajectory, and the spike is annotated separately.")

# ------------------------------------------------------------------ Q3
print("\n== Q3  seasonal_decompose (additive; gaps linearly interpolated for this call only — "
      f"{n_gap} days, flagged) ==")
d7 = seasonal_decompose(sf.dropna(), model="additive", period=7)
sea = d7.seasonal.iloc[:7]
print(f"weekly seasonal peak-to-trough: {sea.max() - sea.min():,.0f} sessions/day "
      f"(peak {sea.idxmax().day_name()} {sea.max():+,.0f}, trough {sea.idxmin().day_name()} {sea.min():+,.0f})")
res = d7.resid.dropna()
print(f"largest residual: {res.abs().idxmax().date()} ({res[res.abs().idxmax()]:+,.0f})")
print("top 3 |residual| days:", [(str(i.date()), round(v)) for i, v in res.abs().nlargest(3).items()])
try:
    d365 = seasonal_decompose(sf.dropna(), model="additive", period=365)
    print(f"period=365: seasonal amplitude {d365.seasonal.max() - d365.seasonal.min():,.0f}; resid SD "
          f"{d7.resid.std():,.0f} (p=7) -> {d365.resid.std():,.0f} (p=365)")
except ValueError as e:
    print("period=365 failed:", e)
print("period=365 is refused by statsmodels: it needs two full cycles (730 days) and the file has 529. "
      "What it WOULD do, given enough data: the annual swing moves out of trend/resid and into 'seasonal'. "
      "With 1.4 years that swing cannot be separated from the trend at all, which is itself the finding.")

# ------------------------------------------------------------------ Q4
print("\n== Q4  lag_at_turn, 31-day window ==")
sg = sf.dropna()
lg = tslib.lag_at_turn(sg, 31, how="min")
print(f"trailing minimum {lg['trailing_turn'].date()}, centred minimum {lg['centred_turn'].date()}, lag {lg['lag_periods']} days vs half-window {lg['half_window']}")
print("A live dashboard refreshing each morning can only show the TRAILING mean (the future does not exist yet); "
      "its caption must say '31-day trailing mean — turning points appear ~15 days late'.")

# ------------------------------------------------------------------ Q5
print("\n== Q5  12 start months x 5 windows, straight line fitted to the rolling mean of the last window days ==")
rows = []
starts = pd.date_range("2024-04-01", periods=12, freq="MS")
for st in starts:
    for w in (7, 14, 28, 56, 91):
        seg = s[st:].rolling(w, min_periods=max(2, w // 2)).mean().dropna()
        t = np.arange(len(seg))
        sl = np.polyfit(t, seg.values, 1)[0]
        rows.append((st.strftime("%Y-%m"), w, sl))
tab = pd.DataFrame(rows, columns=["start", "window", "slope"])
rising, falling = int((tab.slope > 0).sum()), int((tab.slope < 0).sum())
print(f"{len(tab)} combinations: RISING {rising}, FALLING {falling}")
print(tab.assign(dir=np.where(tab.slope > 0, "up", "down")).pivot(index="start", columns="window", values="dir").to_string())
print("By start month alone (window changes little):", tab.groupby("start").slope.apply(lambda x: "up" if (x > 0).all() else ("down" if (x < 0).all() else "mixed")).value_counts().to_dict())
print("Lie Factor = (effect shown)/(effect in the data) presumes there IS one agreed 'effect in the data' — a single "
      "true change between two defined points. A cherry-picked window has no such denominator: the same series carries "
      f"{rising} rising and {falling} falling answers, so the ratio is undefined (its denominator can be made any number). "
      "Honest substitute: report the whole-series slope plus the distribution of slopes across all reasonable windows/starts "
      "(a sensitivity range), and state the window and start date were fixed before plotting.")
