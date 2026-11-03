"""Shared cleaning for Parts B and D: raw hourly sessions -> clean hourly + daily."""
import os
import numpy as np
import pandas as pd

import tslib

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")


def parse_ts(ts: pd.Series) -> pd.Series:
    """Two loggers, two formats. ISO is unambiguous. The slash format is
    DD/MM/YYYY: 2,151 of its rows have a first field > 12 and none has a
    second field > 12, so MM/DD is impossible. Parsed with explicit formats,
    never format='mixed' (which would read 05/10 as 10 May)."""
    slash = ts.str.contains("/")
    out = pd.Series(pd.NaT, index=ts.index, dtype="datetime64[ns]")
    out[~slash] = pd.to_datetime(ts[~slash], format="%Y-%m-%d %H:%M:%S")
    out[slash] = pd.to_datetime(ts[slash], format="%d/%m/%Y %H:%M")
    return out


def load_clean(log=print):
    raw = pd.read_csv(os.path.join(D, "sessions_hourly.csv"))
    L = {"rows_raw": len(raw)}
    log(f"[1] raw rows: {len(raw):,}")

    slash = raw.ts.str.contains("/")
    log(f"[2] two timestamp formats: ISO {int((~slash).sum()):,} rows, DD/MM/YYYY {int(slash.sum()):,} rows")
    a = raw.ts[slash].str[:2].astype(int); b = raw.ts[slash].str[3:5].astype(int)
    log(f"    ambiguity test: first field>12 in {int((a > 12).sum()):,} rows, second field>12 in {int((b > 12).sum())} rows -> DD/MM")
    raw["t"] = parse_ts(raw.ts)
    wrong = pd.to_datetime(raw.ts, format="mixed")
    n_moved = int((wrong != raw.t).sum())
    log(f"    range {raw.t.min()} -> {raw.t.max()}; format='mixed' would silently misdate {n_moved:,} rows")
    L["misdated_if_mixed"] = n_moved

    n_dev = raw.device.nunique()
    raw["device"] = raw.device.str.strip().str.lower()
    log(f"[3] device: {n_dev} spellings stripped + lower-cased -> {raw.device.value_counts().to_dict()} (0 rows dropped)")

    nd = int(raw.duplicated(["t", "sessions", "orders", "revenue_pkr", "device"]).sum())
    df = raw.drop_duplicates(["t", "sessions", "orders", "revenue_pkr", "device"]).copy()
    assert not df.t.duplicated().any()
    log(f"[4] exact duplicate hours removed (same timestamp and identical values): {nd}")
    L["dups"] = nd

    ns = int((df.sessions == -1).sum())
    df.loc[df.sessions == -1, "sessions"] = np.nan
    log(f"[5] sentinel sessions == -1 set to NaN: {ns} hours (orders>0 in all of them: "
        f"{bool((df.loc[df.sessions.isna(), 'orders'] > 0).all())})")
    L["sentinels"] = ns

    h = df.set_index("t").sort_index()
    au = tslib.audit_index(h, "h")
    log(f"[6] hourly audit: monotonic={au['monotonic']} dupes={au['n_duplicated']} "
        f"missing hours={au['n_missing']} ({au['n_missing'] // 24} whole days), span {au['span']}")
    full = pd.date_range(h.index.min(), h.index.max(), freq="h")
    miss_days = pd.Series(full.difference(h.index).normalize()).drop_duplicates()
    log(f"    missing days: {[str(d.date()) for d in miss_days]}")
    L["missing_hours"] = au["n_missing"]; L["missing_days"] = list(miss_days)
    h = h.reindex(full)

    # daily flow: sum. NaN hours (sentinels) filled with that weekday-hour's median for the SUM only.
    key = [h.index.dayofweek, h.index.hour]
    med = h.sessions.groupby(key).transform("median")
    filled = h.sessions.fillna(med)
    imputed_day = h.sessions.isna() & h.sessions.index.normalize().isin(
        h.index.normalize()[h.orders.notna()])
    day_sum = filled.where(h.orders.notna()).resample("D").sum(min_count=1)
    day_raw_obs = h.sessions.where(h.orders.notna()).resample("D").sum(min_count=1)
    n_imp = int(imputed_day.sum())
    log(f"[7] daily sessions = sum of hours (flow). {n_imp} sentinel hours imputed by weekday-hour median "
        f"(+{(day_sum.sum() / day_raw_obs.sum() - 1) * 100:.2f}% on total); missing days left NaN, not 0")
    daily = pd.DataFrame({"sessions": day_sum,
                          "orders": h.orders.resample("D").sum(min_count=1),
                          "revenue_pkr": h.revenue_pkr.resample("D").sum(min_count=1)})
    daily["imputed"] = imputed_day.resample("D").sum().astype(int)
    last = daily.index.max()
    tail = daily.index[daily.index >= last.replace(day=1)]
    log(f"[8] partial final month: {last.strftime('%Y-%m')} holds {len(tail)} days (to {last.date()}); "
        "marked on figures, excluded from monthly comparisons")
    L["tail_start"] = tail[0]
    return h, daily, L
