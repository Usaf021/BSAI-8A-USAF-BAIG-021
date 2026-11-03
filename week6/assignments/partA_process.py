"""
Week 6 · Task A — raw -> audit -> clean/.

    python3 partA_process.py        # prints the audit (also saved to partA_audit.txt), writes clean/ and partA_decisions.md

Reads data/ only. Never edits a raw file. Every fix is a rule with a count.
"""
import io
import os
import contextlib
import numpy as np
import pandas as pd

import geolib
import tslib

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data"); OUT = os.path.join(HERE, "clean")
os.makedirs(OUT, exist_ok=True)
buf = io.StringIO()
def P(*a):
    s = " ".join(str(x) for x in a); print(s); buf.write(s + "\n")
decisions = []
def decide(what, detected, rule, n):
    decisions.append((what, detected, rule, n))

# ============================================================== district_grid
P("=" * 70, "\nFILE 1 · district_grid.csv\n" + "=" * 70)
raw = pd.read_csv(os.path.join(D, "district_grid.csv"), dtype=str, keep_default_na=False)
P(f"rows {len(raw)}; columns {list(raw.columns)}")
g = pd.read_csv(os.path.join(D, "district_grid.csv"))
P("dtypes as pandas reads them:", {c: str(t) for c, t in g.dtypes.items() if t == object and c not in ("code", "district", "zone")}, "<- electrification_pct is text")
P(f"key uniqueness: code unique = {g.code.is_unique}; duplicated codes = {g.code[g.code.duplicated()].tolist()}")
dup = g[g.code.duplicated(keep=False)]
P("the duplicated rows differ in:", [c for c in g.columns if dup[c].nunique() > 1])
P(dup[["code", "district", "solar_kw_installed", "outages", "outage_minutes"]].to_string(index=False))
w5 = pd.read_csv(os.path.join(HERE, "..", "..", "week5", "assignments", "data", "district_health.csv"))
P("register name for D11 in Week 5's file:", w5.loc[w5.code == "D11", "district"].iloc[0])
nd = len(g) - g.code.nunique()
g = g.drop_duplicates("code", keep="first").copy()
decide("Duplicate district row D11 ('Kotla' and 'Kotla City', all identity fields identical, 3 flow fields differ by <0.1%)",
       "code not unique (25 rows, 24 codes); df.code.duplicated()",
       "Drop the second row, keep the first: its name matches Week 5's register (Kotla). Drop, not repair: neither flow value can be proven right (differences 3 interruptions, 12 kW, 410 min)", nd)

el_raw = g.electrification_pct.astype(str)
n_pct = int(el_raw.str.endswith("%").sum()); n_blank = int((el_raw.str.strip() == "").sum() + g.electrification_pct.isna().sum())
g["electrification_pct"] = pd.to_numeric(el_raw.str.replace("%", "", regex=False).str.strip().replace({"": np.nan, "nan": np.nan}), errors="coerce")
P(f"electrification_pct: {n_pct} values carry a '%' suffix, {n_blank} are blank -> numeric; range {g.electrification_pct.min()}–{g.electrification_pct.max()}, missing {int(g.electrification_pct.isna().sum())}")
decide("electrification_pct stored as text: '88.1%' with a % suffix in 2 rows, blank in 3",
       "dtype object after read_csv; str.endswith('%')", "Strip '%' and parse to float; blanks stay NaN (missing is not 0)", n_pct + n_blank)

hh_pp = g.population / g.households
bad = g[(hh_pp < 5) | (hh_pp > 8)]
P("persons per household range before fix:", round(hh_pp.min(), 2), "to", round(hh_pp.max(), 2), "-> outside 5.7–7.4:", bad.code.tolist(),
  f"({bad.households.iloc[0]} households for {bad.population.iloc[0]:,} people = {bad.population.iloc[0] / bad.households.iloc[0]:,.0f} persons/household)")
fix_code = bad.code.iloc[0]
rest = g.loc[g.code != fix_code, "households"]
P(f"the other 23 districts run {(g.population / g.households)[g.code != fix_code].min():.2f}–{(g.population / g.households)[g.code != fix_code].max():.2f} persons/household; "
  f"{fix_code} at x1000 = {int(bad.households.iloc[0]) * 1000:,} households = {bad.population.iloc[0] / (bad.households.iloc[0] * 1000):.2f} persons/household (inside the range)")
g.loc[g.code == fix_code, "households"] = g.loc[g.code == fix_code, "households"] * 1000
decide(f"households for {fix_code} is 182 (a district of 1.08 million people)", "population / households = 5,940 persons per household, every other district 5.70–7.36",
       "REPAIR: multiply by 1,000 (the value was filed in thousands: 182 -> 182,000, 5.94 persons/household, inside the range). Repaired, not dropped: the true value is determined by the unit error", 1)

n_s = int((g.outage_minutes == -1).sum())
P("outage_minutes sentinel -1 in:", g.code[g.outage_minutes == -1].tolist())
g["outage_minutes"] = g.outage_minutes.where(g.outage_minutes != -1)
decide("outage_minutes = -1 (operator not-available code) for D09 and D20", "describe() min = -1; (col == -1).sum()",
       "Set to NaN. A code is not a value. Those two districts have no mean interruption length; their interruption counts stay in use", n_s)

g["mean_interruption_min"] = g.outage_minutes / g.outages
P(f"districts with usable outage_minutes: {int(g.outage_minutes.notna().sum())} of {len(g)}; mean interruption {g.mean_interruption_min.min():.0f}–{g.mean_interruption_min.max():.0f} minutes")
P(f"rows {len(g)}; population {g.population.sum():,}; households {g.households.sum():,}; interruptions {g.outages.sum():,}")
P(f"persons/household range after: {(g.population / g.households).min():.2f}–{(g.population / g.households).max():.2f}; electrification {g.electrification_pct.min()}–{g.electrification_pct.max()} (missing {int(g.electrification_pct.isna().sum())})")
feats = geolib.read_geojson(os.path.join(D, "regions.geojson"))
fc = {f["code"] for f in feats}
P(f"join to regions.geojson: {len(fc & set(g.code))} matched, {len(fc ^ set(g.code))} unmatched")
assert not (fc ^ set(g.code))
P(f"zones: {sorted(g.zone.unique())}; denominators: households {g.households.min():,}–{g.households.max():,}, population {g.population.min():,}–{g.population.max():,}")
g.to_csv(os.path.join(OUT, "district_grid_clean.csv"), index=False)

# ================================================================= grid_daily
P("\n" + "=" * 70, "\nFILE 2 · grid_daily.csv\n" + "=" * 70)
r = pd.read_csv(os.path.join(D, "grid_daily.csv"))
P(f"rows {len(r)}; dtypes {dict(r.dtypes.astype(str))}")
slash = r.date.str.contains("/")
a1 = r.date[slash].str[:2].astype(int); b1 = r.date[slash].str[3:5].astype(int)
P(f"date formats: ISO {int((~slash).sum())}, DD/MM/YYYY {int(slash.sum())}; slash rows with first field>12: {int((a1 > 12).sum())}, second field>12: {int((b1 > 12).sum())} -> DD/MM")
r["date"] = pd.to_datetime(pd.Series(np.where(slash, pd.NaT, r.date)).where(~slash), format="%Y-%m-%d", errors="coerce")
r["date"] = r["date"].fillna(pd.to_datetime(pd.read_csv(os.path.join(D, "grid_daily.csv")).date.where(slash), format="%d/%m/%Y", errors="coerce"))
assert r.date.notna().all()
mixed = pd.to_datetime(pd.read_csv(os.path.join(D, "grid_daily.csv")).date, format="mixed")
nm = int((mixed != r.date).sum())
decide("Two date formats in one column: 2,887 ISO, 174 DD/MM/YYYY", "str.replace(digits,'9').value_counts(); slash rows have first field up to 31 and never a second field >12",
       f"Parse each format explicitly (DD/MM for the slash rows). format='mixed' would silently misdate {nm} rows", int(slash.sum()))
P(f"range {r.date.min().date()} -> {r.date.max().date()}; format='mixed' would misdate {nm} of the {int(slash.sum())} slash rows")

nd2 = int(r.duplicated(["date", "zone"]).sum())
P(f"duplicate (date, zone) keys: {nd2}; of these exact duplicate rows: {int(r.duplicated().sum())}; "
  f"{nd2 - int(r.duplicated().sum())} repeat the same meter reading but file different peak_load_mw / outage_minutes (conflicting)")
r = r.drop_duplicates(["date", "zone"]).sort_values(["zone", "date"]).reset_index(drop=True)
decide("Duplicate zone-day rows", "df.duplicated(['date','zone']).sum()", "Keep the first filing of each (date, zone). 12 are exact copies (nothing lost); 3 repeat the same meter reading with different peak_load_mw / outage_minutes (P3 2025-10-25, P5 2026-02-25, P5 2026-08-16). Which filing is right cannot be stated, so this is a judgement, not a repair: first filing kept and the 3 are flagged here", nd2)
P(f"zone-days kept: {len(r)}")

span = pd.date_range(r.date.min(), r.date.max())
slots = len(span) * r.zone.nunique()
full = pd.MultiIndex.from_product([span, sorted(r.zone.unique())], names=["date", "zone"])
miss = full.difference(pd.MultiIndex.from_frame(r[["date", "zone"]]))
mdf = pd.DataFrame(index=miss).reset_index()
P(f"calendar: {len(span)} days x {r.zone.nunique()} zones = {slots} slots; never reported: {len(mdf)}")
P("by zone:", mdf.groupby("zone").size().to_dict(), "| zone-days missing on the same date:", mdf.groupby("date").size().value_counts().to_dict())
P("audit_index per zone:", {z: (tslib.audit_index(g_.set_index("date"), "D")["n_missing"]) for z, g_ in r.groupby("zone")})
mdf.to_csv(os.path.join(OUT, "grid_missing_zonedays.csv"), index=False)
decide("Zone-days never reported (calendar gaps), unevenly spread: P5 36, P4 24, P2 21 ... P1 12", "reindex onto date_range x zones; full.difference(index)",
       "Leave as gaps (never 0, never interpolated); list in clean/grid_missing_zonedays.csv. Energy is the change in reading across the gap, divided by days spanned; no day inside a gap is invented", len(mdf))

n_p = int((r.peak_load_mw == -1).sum())
r["peak_load_mw"] = r.peak_load_mw.where(r.peak_load_mw != -1)
P(f"peak_load_mw sentinel -1: {n_p} rows -> NaN; remaining range {r.peak_load_mw.min():.0f}–{r.peak_load_mw.max():.0f} MW; "
  f"outage_minutes range {r.outage_minutes.min()}–{r.outage_minutes.max()}")
decide("peak_load_mw = -1, the SCADA not-available code", "describe() min = -1; (col == -1).sum()",
       "Set to NaN, never averaged or plotted as a value; peak load is a maximum, so only mean / median / max are taken over it", n_p)

# the cumulative meter reading is a counter, not a flow
r["prev"] = r.groupby("zone").cumulative_mwh.shift()
r["days_spanned"] = r.groupby("zone").date.diff().dt.days
r["raw_delta"] = r.cumulative_mwh - r.prev
down = r[r.raw_delta < 0]
P(f"meter readings that go DOWN: {len(down)} ->", down[["date", "zone", "prev", "cumulative_mwh"]].to_dict("records"))
z, dd_ = down.zone.iloc[0], down.date.iloc[0]
after = r[(r.zone == z) & (r.date > dd_)].head(3)
P(f"zone {z} reading falls from {down.prev.iloc[0]:,.0f} to {down.cumulative_mwh.iloc[0]:,.0f} then climbs ~{after.raw_delta.mean():,.0f}/day: the meter was replaced or reset")
r["energy_mwh"] = r.raw_delta.where(r.raw_delta >= 0)
r["meter_reset"] = r.raw_delta < 0
r["energy_per_day"] = r.energy_mwh / r.days_spanned
decide("cumulative_mwh is a meter reading (a counter), not a quantity: summing it gives 479x too much; and one reading goes backwards (P4, 2026-02-17: 21,444,255 -> 1,180, a reset)",
       "diff() < 0 on a monotone counter; P1 June sum() = 574,845,315 vs delta 1,199,207",
       "Energy = difference between readings (MWh), per zone, divided by days spanned. The reset day's delta is NaN and flagged (the true value cannot be stated: the reset time is unknown); P4's readings after the reset are not spliced", int(len(down)))

jun = r[(r.zone == "P1") & (r.date >= "2026-06-01") & (r.date <= "2026-06-30")]
P(f"P1 June 2026: sum of the reading column = {jun.cumulative_mwh.sum():,.0f} MWh (WRONG, a counter); ")
p1 = r[r.zone == "P1"].set_index("date").cumulative_mwh
e1 = p1["2026-06-30"] - p1["2026-05-31"]
e2 = p1["2026-07-01"] - p1["2026-06-01"]
P(f"                energy delivered = reading(30 Jun) - reading(31 May) = {e1:,.0f} MWh; reading(1 Jul) - reading(1 Jun) = {e2:,.0f} MWh "
  f"(the brief's 1,200,239 is the latter convention); sum() overstates by {jun.cumulative_mwh.sum() / e2:,.0f}x")
P(f"first-of-month convention used for comparability with the brief; difference between the two conventions {abs(e2 - e1) / e1:.2%}")
keep_cols = ["date", "zone", "cumulative_mwh", "energy_mwh", "days_spanned", "energy_per_day", "meter_reset", "peak_load_mw", "outage_minutes"]
r[keep_cols].to_csv(os.path.join(OUT, "grid_daily_clean.csv"), index=False)

# ============================================================= generation_mix
P("\n" + "=" * 70, "\nFILE 3 · generation_mix.csv\n" + "=" * 70)
gm = pd.read_csv(os.path.join(D, "generation_mix.csv"))
P(f"rows {len(gm)}; months {gm.month.nunique()} ({gm.month.min()} → {gm.month.max()}); categories per month {gm.groupby('month').size().unique().tolist()}")
tot = gm[gm.subsource == "Total"]; parts = gm[gm.subsource != "Total"]
P(f"{len(tot)} rows have subsource 'Total' (source 'All sources'); parts = {len(parts)} = {gm.month.nunique()} months x {parts.groupby('month').size().iloc[0]} categories")
chk = (parts.groupby("month").mwh.sum() - tot.set_index("month").mwh).abs()
P(f"exclusivity: parts summed vs published total: max difference {chk.max()} MWh over {len(chk)} months")
P(f"every row summed / generated = {gm.mwh.sum() / parts.mwh.sum():.1%} of the energy generated (the total row counted as a part)")
parts.to_csv(os.path.join(OUT, "generation_parts.csv"), index=False)
tot.to_csv(os.path.join(OUT, "generation_totals.csv"), index=False)
decide("generation_mix.csv carries a 'Total' row per month alongside the parts; any share, pie, treemap or sum over all rows counts the energy twice (200.0%)",
       "groupby(month).mwh.sum() == 2 x parts; subsource == 'Total'", "Split: 144 part rows to generation_parts.csv, 18 total rows to generation_totals.csv; parts agree with the total to within 2 MWh in every month. Shares use the parts only", len(tot))

# ================================================================= final checks
P("\n" + "=" * 70, "\nCHECKS AGAINST THE BRIEF\n" + "=" * 70)
checks = [("rows in cleaned register", len(g), 24), ("population", int(g.population.sum()), 57_857_000),
          ("households", int(g.households.sum()), 8_908_512), ("interruptions", int(g.outages.sum()), 388_879),
          ("districts with usable outage_minutes", int(g.outage_minutes.notna().sum()), 22), ("zone-days kept", len(r), 3046),
          ("slots", slots, 3174), ("never reported", len(mdf), 128), ("peak_load unusable", int(r.peak_load_mw.isna().sum()), 46),
          ("meter goes down", int(len(down)), 1), ("generation part rows", len(parts), 144),
          ("electrification missing", int(g.electrification_pct.isna().sum()), 3)]
for n, got, exp in checks:
    P(f"  {n:<40} {got:>12,} expected {exp:>12,}  {'OK' if got == exp else 'MISMATCH'}")
P(f"  persons/household {(g.population / g.households).min():.2f}–{(g.population / g.households).max():.2f} (expected 5.70–7.36); mean interruption {g.mean_interruption_min.min():.0f}–{g.mean_interruption_min.max():.0f} (expected 77–214)")
P(f"  P1 June 2026 energy: {e2:,.0f} (brief 1,200,239) | end-of-day convention {e1:,.0f}; sum() {jun.cumulative_mwh.sum():,.0f} = {jun.cumulative_mwh.sum() / e2:,.0f}x too big (brief 479x)")

with open(os.path.join(HERE, "partA_audit.txt"), "w") as fh: fh.write(buf.getvalue())
md = ["# Task A — decisions table", "", "Written by `partA_process.py`. Raw files in `data/` are untouched; cleaned copies are in `clean/`.", "",
      "| # | What | How detected | Rule applied | Rows affected |", "|---|---|---|---|---|"]
for i, (w, d, rl, n) in enumerate(decisions, 1):
    md.append(f"| {i} | {w} | {d} | {rl} | {n} |")
open(os.path.join(HERE, "partA_decisions.md"), "w").write("\n".join(md) + "\n")
print(f"\nwrote clean/ ({', '.join(sorted(os.listdir(OUT)))}), partA_audit.txt, partA_decisions.md")
