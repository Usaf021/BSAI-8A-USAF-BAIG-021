"""Part A — raw -> audit -> clean/.   Run:  python3 partA_process.py

Reads the four raw CSVs and the GeoJSON from assignments/data/ (unmodified),
prints an audit, repairs or drops what it finds, and writes clean/*.csv, then
partA_audit.txt and partA_decisions.md. Nothing is hand edited.
"""
import io
import contextlib
import numpy as np
import pandas as pd

from _common import DATA, CLEAN, HERE, AUDIT, MODES
import geolib

CLEAN.mkdir(exist_ok=True)
DMY = r"^\d\d/\d\d/\d{4}$"
decisions = []   # (what, how detected, rule applied, rows affected)


def decide(what, how, rule, n):
    decisions.append((what, how, rule, n))


def audit_frame(name, df, key=None):
    print(f"\n--- {name}: {len(df)} rows x {df.shape[1]} cols")
    print("dtypes:", ", ".join(f"{c}:{t}" for c, t in df.dtypes.astype(str).items()))
    print("nulls :", {c: int(n) for c, n in df.isna().sum().items() if n} or "none")
    print("full-row duplicates:", int(df.duplicated().sum()))
    if key:
        print(f"key {key!r}: unique={df[key].is_unique}, distinct={df[key].nunique()}")


buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    print("PART A AUDIT — raw files, then what the script did about it")
    print("=" * 72)

    # ================================================================ register
    reg = pd.read_csv(DATA / "district_transit.csv", dtype={"code": str})
    feats = geolib.read_geojson(DATA / "regions.geojson")
    geo_codes = {f["code"] for f in feats}
    audit_frame("district_transit.csv (raw)", reg, "code")
    print("codes not matching the pattern D##:", reg.code[~reg.code.str.match(r"^D\d\d$")].tolist())
    m0 = reg.code.isin(geo_codes).sum()
    print(f"GeoJSON features matched on code AS FILED: {m0} of {len(geo_codes)}")
    print("register codes with no polygon:", sorted(set(reg.code) - geo_codes))
    print(f"population sum, all {len(reg)} rows: {reg.population.sum():,}")
    reg["_bpr"] = reg.boardings_annual / reg.population
    print("boardings per resident < 1:", reg.loc[reg._bpr < 1, ["code", "boardings_annual", "population"]].values.tolist())
    print("fare_concession_pct range:", reg.fare_concession_pct.min(), "-", reg.fare_concession_pct.max(),
          "| rows < 1:", reg.loc[reg.fare_concession_pct < 1, "code"].tolist())
    print("road_km <= 0:", reg.loc[reg.road_km <= 0, "code"].tolist())

    n_in = len(reg)
    # 1. code hygiene
    new_code = reg.code.str.replace(r"\s+", "", regex=True).str.upper()
    n_fix = int((new_code != reg.code).sum())
    reg["code"] = new_code
    decide("Register keys mis-typed (`d13`, `D 20`)",
           "GeoJSON join matched only 22 of 24; regex ^D\\d\\d$ on `code`",
           "strip whitespace + upper-case the key (repair: the true key is unambiguous)", n_fix)
    # 2. non-district row
    extra = reg[~reg.code.isin(geo_codes)]
    decide("Row D00 'Qilabad Capital Territory' is not a district",
           "no polygon in regions.geojson; pop 2,890,000 overlaps D17 Qilabad; "
           "population sum 60,747,000 != federation's 57,857,000",
           "drop (accurate row, but it does not belong in a one-row-per-district sum)", len(extra))
    reg = reg[reg.code.isin(geo_codes)].copy()
    # 3. concession fraction vs percent
    frac = reg.fare_concession_pct < 1
    reg.loc[frac, "fare_concession_pct"] *= 100
    decide("`fare_concession_pct` filed as a fraction in 4 rows (0.327 …)",
           "20 of 24 values are 20.9–42.6; four are < 1",
           "repair x100 (a share cannot be 0.3%; the other 20 are percent)", int(frac.sum()))
    # 4. boardings in thousands
    low = reg._bpr < 1
    reg.loc[low, "boardings_annual"] *= 1000
    decide("`boardings_annual` filed in thousands for 3 districts (D05, D15, D23)",
           "boardings per resident < 1 (e.g. 14,551 boardings for 712,000 people)",
           "repair x1000; cross-checked: register total then matches the route table to within 700", int(low.sum()))
    # 5. road_km code
    code_road = reg.road_km <= 0
    reg.loc[code_road, "road_km"] = np.nan
    decide("`road_km` = -1 (operator 'not surveyed' code, D06 and D16)",
           "impossible negative length", "set to NaN — missing is not zero, and I cannot state the true value", int(code_road.sum()))
    reg = reg.drop(columns="_bpr").sort_values("code").reset_index(drop=True)

    print("\n>>> after cleaning")
    print(f"rows in/out: {n_in} -> {len(reg)}; GeoJSON matched: {reg.code.isin(geo_codes).sum()} of 24")
    print(f"population {reg.population.sum():,}; households {reg.households.sum():,}")
    print(f"boardings_annual (register, 24 districts): {reg.boardings_annual.sum():,}")
    per1000 = reg.boardings_annual / reg.population * 1000
    print(f"boardings per 1,000 residents: {per1000.min():,.0f} – {per1000.max():,.0f}; pooled "
          f"{reg.boardings_annual.sum() / reg.population.sum() * 1000:,.0f}")
    print(f"fare_concession_pct: {reg.fare_concession_pct.min():.1f} – {reg.fare_concession_pct.max():.1f}")
    print(f"road_km usable: {reg.road_km.notna().sum()} of {len(reg)}")
    print("divisors: population", reg.population.min(), "-", reg.population.max(), "(all > 0)")

    # =================================================================== routes
    rt = pd.read_csv(DATA / "routes.csv")
    audit_frame("routes.csv (raw)", rt, "route_id")
    print("mode labels as filed:", rt["mode"].value_counts().to_dict())
    for c in ("punctuality_pct", "cost_recovery_pct", "crowding_index"):
        print(f"{c}: min {rt[c].min()}, max {rt[c].max()}, values >100 or ==0:",
              rt.loc[(rt[c] > 100) | (rt[c] == 0), "route_id"].tolist())
    served = rt.districts_served.str.split(";").explode()
    print("districts_served codes with no register row:", sorted(set(served) - set(reg.code)))

    label_map = {"brt": "BRT", "bus rapid transit": "BRT"}
    new_mode = rt["mode"].str.strip().map(lambda s: label_map.get(s.lower(), s))
    n = int((new_mode != rt["mode"]).sum())
    rt["mode"] = new_mode
    decide("Route `mode` has 6 labels for 4 modes (`brt`, `Bus Rapid Transit`)",
           "value_counts() on `mode`", "map to canonical BRT (repair: same mode, different spelling)", n)
    pb = rt.punctuality_pct > 100
    rt.loc[pb, "punctuality_pct"] = np.nan
    decide("`punctuality_pct` = 999 (operator code)", "value > 100 is impossible for a percentage",
           "set NaN; never averaged as a number", int(pb.sum()))
    cb = rt.cost_recovery_pct == 0
    rt.loc[cb, "cost_recovery_pct"] = np.nan
    decide("`cost_recovery_pct` = 0.0 on R022 and R033 (code for 'not reported')",
           "exact 0.0 on routes that are carrying 5–10 M boardings a year and sell tickets",
           "set NaN (a route with fares cannot recover exactly 0)", int(cb.sum()))

    print("\n>>> after cleaning")
    print("routes per mode:", rt["mode"].value_counts().to_dict(), "| distinct labels:", rt["mode"].nunique())
    print(f"punctuality usable: {rt.punctuality_pct.notna().sum()} of {len(rt)}, "
          f"{rt.punctuality_pct.min()}–{rt.punctuality_pct.max()}")
    print("cost_recovery codes removed:", int(cb.sum()))

    # cross-file reconciliation: a finding, not an error to smooth over
    route_tot, reg_tot = int(rt.boardings_annual.sum()), int(reg.boardings_annual.sum())
    print(f"\nRECONCILIATION register vs routes: {reg_tot:,} vs {route_tot:,} (diff {route_tot - reg_tot:,})")
    attributed = int(rt.assign(n=rt.districts_served.str.split(";").str.len())
                     .eval("boardings_annual * n").sum())
    import dashlib
    ov = dashlib.overlap_factor(rt, "route_id", "districts_served", "boardings_annual")
    print(f"route boardings credited to every district a route serves: {ov['attributed_total']:,.0f} "
          f"= {ov['factor']:.3f}x the network total; {ov['units_multi']} of {ov['units']} routes "
          f"serve >1 district (mean {ov['mean_parts']:.2f}, max {ov['max_parts']})")
    decide("Register total and route-table total disagree by {:,} boardings (0.0001%)".format(route_tot - reg_tot),
           "sum of register `boardings_annual` vs sum of route `boardings_annual`",
           "REPORTED, not smoothed: rounding in the source; the two files agree to 0.0001%", 0)
    decide("`districts_served` is a list: summing by district counts a route up to 4 times",
           "dashlib.overlap_factor(routes, ...) -> 3.096x",
           "route-level sums use the route table once; district-level figures come from the register, which is exclusive", int(ov["units_multi"]))

    # =================================================================== daily
    dd = pd.read_csv(DATA / "ridership_daily.csv", dtype={"date": str})
    audit_frame("ridership_daily.csv (raw)", dd)
    iso = dd.date.str.match(r"^\d{4}-\d{2}-\d{2}$")
    dmy = dd.date[~iso].str.match(DMY).all()
    print(f"dates in the main (ISO) format: {iso.sum()}; other: {(~iso).sum()} (all dd/mm/yyyy: {dmy})")
    mf = pd.to_datetime(dd.date[~iso], format="%m/%d/%Y", errors="coerce")
    n_fail = int(mf.isna().sum())
    print(f"month-first parse of those: {n_fail} fail, {int(mf.notna().sum())} silently accepted as a different day")
    dd["date"] = pd.to_datetime(dd.date.where(iso), format="%Y-%m-%d").fillna(
        pd.to_datetime(dd.date.where(~iso), format="%d/%m/%Y"))
    decide("`date` in two formats; 385 rows are dd/mm/yyyy",
           "regex on the string; month-first parse fails on 230 and silently mis-dates 155 "
           "(e.g. 02/12/2025 is 2 Dec, not 12 Feb)",
           "parse each format explicitly (ISO, then %d/%m/%Y) — never one `to_datetime` guess", int((~iso).sum()))

    n0 = len(dd)
    dups = dd.duplicated(keep="first")
    dup_by = dd.loc[dups, "mode"].value_counts().to_dict()
    dup_months = dd.loc[dups, "date"].dt.to_period("M").astype(str).unique().tolist()
    dd = dd[~dups]
    print(f"exact re-submissions: {int(dups.sum())}; by mode {dup_by}, months {dup_months}")
    decide("30 exact re-submitted rows (one mode, one month: Bus, 2026-05)",
           "full-row duplicated() after dates parsed", "keep first, drop the rest (a return filed twice is one return)", int(dups.sum()))

    imp = (dd.trips_on_time > dd.trips_operated) | (dd.trips_operated > dd.trips_scheduled)
    print(f"impossible rows: {int(imp.sum())} (all trips_on_time > trips_operated: "
          f"{bool((dd.trips_on_time[imp] > dd.trips_operated[imp]).all())})")
    dd.loc[imp, "trips_on_time"] = np.nan
    dd["trips_on_time"] = dd.trips_on_time.astype("Int64")
    decide("7 rows with more departures on time than departures run",
           "trips_on_time > trips_operated (cannot happen)",
           "repair the impossible field only: trips_on_time -> NaN (true value unknowable); the row's boardings "
           "and delay are independent and kept. Row excluded from punctuality ratios, included in boardings", int(imp.sum()))
    dd = dd.sort_values(["date", "mode"]).reset_index(drop=True)
    print(f"rows: {n0} -> {len(dd)}")

    span = pd.date_range("2025-04-01", "2026-09-30", freq="D")
    full = pd.MultiIndex.from_product([span, MODES], names=["date", "mode"])
    have = dd.set_index(["date", "mode"]).index
    missing = full.difference(have)
    print(f"span {span[0].date()} -> {span[-1].date()} = {len(span)} days x 4 = {len(full)} slots; "
          f"filed {len(have)}; never filed {len(missing)}")
    ms = pd.Series(1, index=missing).reset_index()
    print("never filed, by mode:", ms["mode"].value_counts().to_dict())
    worst = (0, None, None, None)
    for m, g in ms.groupby("mode"):
        dts = g.date.sort_values().reset_index(drop=True)
        run = (dts.diff() != pd.Timedelta("1D")).cumsum()
        for _, rr in dts.groupby(run):
            if len(rr) > worst[0]:
                worst = (len(rr), m, rr.iloc[0].date(), rr.iloc[-1].date())
    print(f"longest gap: {worst[0]} consecutive days, {worst[1]}, {worst[2]} -> {worst[3]}")
    late = dd[dd.date >= "2026-09-22"]
    print(f"slots filed from 2026-09-22 on: {len(late)} of 36; by mode {late['mode'].value_counts().to_dict()}")
    decide("63 slots nobody filed (22 Ferry, 19 Bus, 18 Metro, 4 BRT); longest gap 14 days ({}, Metro) -> {}".format(worst[2], worst[3]),
           "reindex against the full day x mode calendar",
           "NOT filled and NOT zero: left absent. Sums over a gap are reported as 'filed days'; trends use ratios of sums", len(missing))
    decide("Bus and Ferry stop filing after 2026-09-21; September 2026 is a partial period",
           "slots filed from 2026-09-22: 18 of 36", "series cut at the last complete month (2026-08) for levels; September drawn hatched/greyed if shown", len(late))

    # 12-month boardings, with and without duplicates
    raw = pd.read_csv(DATA / "ridership_daily.csv", dtype={"date": str})
    raw["date"] = pd.to_datetime(raw.date.where(raw.date.str.match(r"^\d{4}"), None), format="%Y-%m-%d").fillna(
        pd.to_datetime(raw.date.where(~raw.date.str.match(r"^\d{4}"), None), format="%d/%m/%Y"))
    w = lambda x: x[(x.date >= "2025-09-01") & (x.date <= "2026-08-31")].boardings.sum()
    cl12, dirty12 = int(w(dd)), int(w(raw))
    print(f"\nBoardings 12 months to 2026-08-31: clean {cl12:,}; with the re-submitted rows left in "
          f"{dirty12:,} ({(dirty12 / cl12 - 1) * 100:+.2f}%)")
    print(f"RECONCILIATION register vs returns: {reg_tot:,} vs {cl12:,}: returns cover {cl12 / reg_tot * 100:.1f}%; "
          f"the missing {100 - cl12 / reg_tot * 100:.1f}% is the days nobody filed")
    decide("Register's annual boardings (873.6 M) exceed what the returns account for (845.5 M)",
           "12-month sum of clean daily boardings vs register total",
           "REPORTED: returns cover 96.8%; the gap is the 63 unfiled days, not an error in either file", 0)

    # ===================================================================== fare
    fr = pd.read_csv(DATA / "fare_revenue.csv")
    audit_frame("fare_revenue.csv (raw)", fr)
    print("ticket_type values:", fr.ticket_type.value_counts().to_dict())
    dc = dashlib.drilldown_check(fr, "ticket_type", "trips", within=("month", "mode"), total_label="All tickets")
    dr = dashlib.drilldown_check(fr, "ticket_type", "revenue_pkr", within=("month", "mode"), total_label="All tickets")
    print(f"drilldown_check: {dc['parts_rows']} part rows + {dc['total_rows']} total rows; summing every row = "
          f"{dc['sum_all_pct']:.1f}% of journeys, {dr['sum_all_pct']:.1f}% of revenue; parts reconcile to published "
          f"summary: {dc['reconciles'] and dr['reconciles']} (worst diff {dc['worst_abs']:.0f})")
    fare_parts = fr[fr.ticket_type != "All tickets"].copy()
    fare_total = fr[fr.ticket_type == "All tickets"].copy()
    decide("`All tickets` rows (72) are the publisher's own subtotal filed beside the parts",
           "summing every row gives exactly 200.0%; drilldown_check() agrees parts = subtotal for every month/mode",
           "split: parts -> fare_revenue.csv (216 rows); subtotals -> fare_published_totals.csv (72 rows), kept for reconciliation", len(fare_total))
    print(f"journeys {fare_parts.trips.sum():,}; revenue {fare_parts.revenue_pkr.sum():,} PKR; "
          f"mean fare {fare_parts.revenue_pkr.sum() / fare_parts.trips.sum():.1f} PKR")
    print(f"boardings / journeys over the file: "
          f"{dd.boardings.sum() / fare_parts.trips.sum():.3f} (the two units never share an axis)")
    print("last month 2026-09 is partial (daily returns end the 21st for Bus/Ferry): excluded from comparisons")
    decide("Fare table's last month (2026-09) is not a whole month",
           "daily returns for Bus and Ferry stop 2026-09-21; month is below the trend",
           "kept in clean/, flagged by the analysis window: every comparison uses complete months 2025-04 -> 2026-08", 0)

# ==================================================================== write
reg.to_csv(CLEAN / "district_transit.csv", index=False)
rt.to_csv(CLEAN / "routes.csv", index=False)
dd.to_csv(CLEAN / "ridership_daily.csv", index=False, date_format="%Y-%m-%d")
fare_parts.to_csv(CLEAN / "fare_revenue.csv", index=False)
fare_total.to_csv(CLEAN / "fare_published_totals.csv", index=False)
print("\n>>> wrote:", ", ".join(sorted(p.name for p in CLEAN.glob("*.csv"))), "\n")

text = buf.getvalue()
print(text)
AUDIT.write_text(text + "\n" + "=" * 72 + "\n")

md = ["# Part A — decisions", "",
      "One row per decision. *Rows affected* counts rows changed or removed (0 = a finding that is reported, not a row edit).", "",
      "| # | What | How detected | Rule applied | Rows affected |", "|---|---|---|---|---|"]
for i, (a, b, c, n) in enumerate(decisions, 1):
    md.append(f"| {i} | {a} | {b} | {c} | {n} |")
(HERE / "partA_decisions.md").write_text("\n".join(md) + "\n")
