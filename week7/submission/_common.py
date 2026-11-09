"""Shared paths and loaders. Every path is relative to this file."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# the course toolkits and raw data live in assignments/ (next to this folder,
# or inside it if the folder was zipped together)
ASSIGN = next(p for p in (HERE / "assignments", HERE.parent / "assignments") if p.exists())
sys.path.insert(0, str(ASSIGN))

DATA = ASSIGN / "data"          # raw, never modified
CLEAN = HERE / "clean"          # written by partA_process.py
AUDIT = HERE / "partA_audit.txt"

import pandas as pd  # noqa: E402

MODES = ["Metro", "BRT", "Bus", "Ferry"]
# window used everywhere (declared on every figure): complete quarters
Q_BEFORE = ("2025-04-01", "2025-06-30")   # 2025 Q2
Q_AFTER = ("2026-04-01", "2026-06-30")    # 2026 Q2
LAST_COMPLETE_DAY = pd.Timestamp("2026-08-31")
LAST_COMPLETE_MONTH = "2026-08"


def load_clean():
    d = pd.read_csv(CLEAN / "ridership_daily.csv", parse_dates=["date"])
    r = pd.read_csv(CLEAN / "routes.csv")
    g = pd.read_csv(CLEAN / "district_transit.csv")
    f = pd.read_csv(CLEAN / "fare_revenue.csv")
    return d, r, g, f

# one hue per mode, on every figure; shape repeats it so identity is never
# colour alone (Week 2, redundant coding)
MODE_COLOR = {"Metro": "#0072B2", "BRT": "#D55E00", "Bus": "#009E73", "Ferry": "#CC79A7"}
MODE_MARKER = {"Metro": "o", "BRT": "s", "Bus": "^", "Ferry": "D"}
SOURCE = "Source: Federal Transit Authority returns, routes, register and ministry fare table (synthetic, CDB601220), cleaned by partA_process.py."


def punctual_rows(d):
    """Rows usable for punctuality: both counts present (7 impossible rows excluded)."""
    u = d.dropna(subset=["trips_on_time"]).copy()
    u["trips_on_time"] = u.trips_on_time.astype(float)
    return u


def ontime_rate(d, by):
    """Punctuality = sum(on time) / sum(operated). Never a mean of daily %."""
    u = punctual_rows(d)
    g = u.groupby(by)[["trips_on_time", "trips_operated"]].sum()
    return g.trips_on_time / g.trips_operated * 100


def between(d, window):
    return d[(d.date >= window[0]) & (d.date <= window[1])]
