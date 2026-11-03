"""
Week 5 · Part A — rebuild nine charts, then take them apart.
Left panel = the chart as the recipe says; right panel = the redesign.
Every number quoted in partA_diagnosis.pdf is printed here.

    python3 partA_charts.py > partA_output.txt
"""
import itertools
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

import geolib
from vizlib import PALETTE, style_defaults, save_fig

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")
BLUE, ORANGE, GREEN = PALETTE["series"]
PINK, GREY = PALETTE["series_4th"], PALETTE["muted"]
SRC = "Synthetic course data, CDB601220 Week 5 (fictional federation)."
style_defaults(); plt.rcParams["axes.titlesize"] = 10
feats = geolib.read_geojson(f"{D}/districts.geojson")
hi = pd.read_csv(f"{D}/health_indicators.csv")
dh = pd.read_csv(f"{D}/district_health.csv")
dh["rate"] = dh.cases / dh.population * 1e5
POOLED = dh.cases.sum() / dh.population.sum() * 1e5
FIVE = ["gdp_pc", "healthcare_access", "urban_pct", "median_age", "cases_per_100k"]


def hdr(n, t): print(f"\n{'=' * 72}\nCASE {n} · {t}\n{'=' * 72}")


def done(fig, n, note):
    fig.tight_layout()
    save_fig(fig, os.path.join(HERE, f"partA_case{n:02d}.png"), note=f"{note}  {SRC}")
    plt.close(fig)


def join_check(codes_a, codes_b, label):
    miss = set(codes_a) ^ set(codes_b)
    print(f"join check {label}: {len(set(codes_a) & set(codes_b))} matched, {len(miss)} unmatched")
    assert not miss


# ------------------------------------------------------------------ 1
hdr(1, "size encoded as pop_m**2 on a scatter whose size is already area")
s_recipe = hi.pop_m ** 2
s_area = hi.pop_m
print(f"60 marks. recipe as written s=pop_m**2: largest/smallest AREA = {s_recipe.max() / s_recipe.min():,.0f}x "
      f"| area proportional to pop (s=pop_m): {s_area.max() / s_area.min():,.0f}x  (self-check number 589)")
print(f"NOTE: the brief's self-check (589x) matches s proportional to pop_m; the literal recipe s=pop_m**2 gives "
      f"{s_recipe.max() / s_recipe.min():,.0f}x. I report both.")
print(f"Lie factor on area under the recipe = {(s_recipe.max() / s_recipe.min()) / (hi.pop_m.max() / hi.pop_m.min()):,.0f} "
      f"(shown 346,921x for a 589x population range)")
print(f"countries with pop < 2.0 M: {(hi.pop_m < 2).sum()} | with s<1 pt^2 under the recipe: {(s_recipe < 1).sum()} "
      f"| diameter ratio at correct area scaling: {np.sqrt(589):.1f}x")
print(f"r(pop, access) = {np.corrcoef(hi.pop_m, hi.healthcare_access)[0, 1]:+.3f}; Spearman "
      f"{stats.spearmanr(hi.pop_m, hi.healthcare_access)[0]:+.3f} (p={stats.spearmanr(hi.pop_m, hi.healthcare_access)[1]:.3f}); "
      f"r(access, log gdp) = {np.corrcoef(hi.healthcare_access, np.log(hi.gdp_pc))[0, 1]:+.3f}")
big = hi.nlargest(5, "pop_m")
print("five largest countries' access:", dict(zip(big.country, big.healthcare_access)))
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 5))
a.scatter(hi.gdp_pc, hi.healthcare_access, s=s_recipe, color=BLUE, alpha=0.45, edgecolor="white")
a.set_xscale("log"); a.set_xlabel("GDP per capita, USD (log scale)"); a.set_ylabel("Healthcare access index (0–100)")
a.set_title("As published: s = pop_m**2  (area range 346,921×)")
lo_, hi_ = 12, 1500
sz = lo_ + (hi_ - lo_) * (hi.pop_m - hi.pop_m.min()) / (hi.pop_m.max() - hi.pop_m.min())
b.scatter(hi.gdp_pc, hi.healthcare_access, s=sz, color=BLUE, alpha=0.5, edgecolor="white")
for _, r in hi.nlargest(3, "pop_m").iterrows():
    b.annotate(f"{r.country} ({r.pop_m:.0f} m)", (r.gdp_pc, r.healthcare_access), fontsize=8, xytext=(6, 8), textcoords="offset points")
b.set_xscale("log"); b.set_xlabel("GDP per capita, USD (log scale)"); b.set_ylabel("Healthcare access index (0–100)")
b.set_title("Area ∝ population (589× range); the big three scatter across access, r(pop, access) = +0.21")
b.scatter([], [], s=lo_, color=GREY, label="0.6 m"); b.scatter([], [], s=(lo_ + hi_) / 2, color=GREY, label="177 m"); b.scatter([], [], s=hi_, color=GREY, label="353 m")
b.legend(title="Population (area)", loc="lower right", labelspacing=1.5, frameon=False)
done(fig, 1, "Redesign: mark AREA linear in population, real-value size legend, three direct labels.")

# ------------------------------------------------------------------ 2
hdr(2, "choropleth of a raw count")
join_check([f["code"] for f in feats], dh.code, "districts.geojson vs district_health")
print(f"24 districts, {dh.cases.sum():,} cases, population {dh.population.sum():,}; top3 by count: {list(dh.nlargest(3, 'cases').code)}; "
      f"by rate: {list(dh.nlargest(3, 'rate').code)}")
print(f"r(cases, population) = {np.corrcoef(dh.cases, dh.population)[0, 1]:+.3f}; pooled rate {POOLED:.1f} per 100,000")
t3 = dh.nlargest(3, "cases")
print("top-3-by-count districts sit at lon/lat:", [(r.code, round(r.lon, 1), round(r.lat, 1)) for r in t3.itertuples()],
      "-> 6+ degrees apart: they are not a cluster 'around the capital'")
print("their rates:", {r.code: round(r.rate, 1) for r in t3.itertuples()}, f"vs pooled {POOLED:.1f}")
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 5.6))
e = geolib.choropleth(a, feats, dict(zip(dh.code, dh.cases)), scheme="natural", legend_title="confirmed cases\n(natural breaks)")
a.set_title("As published: cases (raw count)")
e2 = geolib.choropleth(b, feats, dict(zip(dh.code, dh.rate)), scheme="natural", legend_title="cases per 100,000 residents\n(natural breaks)", fmt="{:,.1f}")
b.set_title("Cases per 100,000 residents: the dark districts are D19–D21, not D17/D13/D09")
done(fig, 2, "Redesign: normalised by resident population; equal-area projection; Jenks 5 classes.")

# ------------------------------------------------------------------ 3
hdr(3, "min-max scaling with one outlier")
mm = geolib.scale_frame(hi, FIVE, "minmax")
print(f"gdp_pc: {(mm.gdp_pc < 0.10).sum()} of 60 below 0.10; median {mm.gdp_pc.median():.3f}")
srt = hi.gdp_pc.sort_values(ascending=False)
print(f"max {srt.iloc[0]:,} is {srt.iloc[0] / srt.iloc[1]:.1f}x the second ({srt.iloc[1]:,}); min {srt.iloc[-1]}; "
      f"without {hi.loc[hi.gdp_pc.idxmax(), 'country']}: range {srt.iloc[-1]}–{srt.iloc[1]:,} = {srt.iloc[1] / srt.iloc[-1]:.0f}x, "
      f"IQR {hi.gdp_pc.quantile(.25):,.0f}–{hi.gdp_pc.quantile(.75):,.0f}")
rk = geolib.scale_frame(hi, FIVE, "rank")
print(f"rank scaling: gdp_pc median {rk.gdp_pc.median():.2f}; fraction below 0.10 = {(rk.gdp_pc < 0.10).mean():.0%}")
hi2 = hi.copy(); hi2["gdp_pc"] = np.log10(hi.gdp_pc)
ml = geolib.scale_frame(hi2, FIVE, "minmax")
print(f"log10 then min-max: below 0.10 = {(ml.gdp_pc < 0.10).sum()}, median {ml.gdp_pc.median():.2f}")
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.8))
geolib.pcp(a, hi, FIVE, how="minmax", highlight=(hi.gdp_pc > 50000).values)
a.set_title("As published: min–max, order as in file; one country flattens GDP")
geolib.pcp(b, hi, FIVE, how="rank", highlight=(hi.gdp_pc > 50000).values)
b.set_title("Rank-scaled: GDP spreads over the full axis; Aldonia (orange) top, others graded")
for ax_, t in [(a, "axes min–max scaled to 0–1"), (b, "axes rank-scaled (percentile); axis end labels are raw values")]:
    ax_.text(0.0, -0.17, t, transform=ax_.transAxes, fontsize=8, color=PALETTE["ink_soft"])
done(fig, 3, "Redesign: percentile-rank scaling (immune to the 9.2x outlier); outlier brushed, not dropped.")

# ------------------------------------------------------------------ 4
hdr(4, "axis order")
pos = {c: i for i, c in enumerate(FIVE)}
print("file order axes:", FIVE)
print(f"healthcare_access <-> cases_per_100k are {abs(pos['healthcare_access'] - pos['cases_per_100k'])} axes apart (urban_pct, median_age between)")
rr = hi[FIVE].corr()
print(f"r(healthcare_access, cases_per_100k) = {rr.loc['healthcare_access', 'cases_per_100k']:+.3f} (strongest pair of 10)")
order = geolib.corr_chain(hi, FIVE); print("corr_chain order:", order)
print("adjacent |r| in file order:", [round(float(abs(rr.loc[FIVE[i], FIVE[i + 1]])), 2) for i in range(4)], " mean",
      round(np.mean([abs(rr.loc[FIVE[i], FIVE[i + 1]]) for i in range(4)]), 2))
print("adjacent |r| in chain order:", [round(float(abs(rr.loc[order[i], order[i + 1]])), 2) for i in range(4)], " mean",
      round(np.mean([abs(rr.loc[order[i], order[i + 1]]) for i in range(4)]), 2))
hl = (hi.region == hi.region.iloc[1]).values
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.8))
hi_r = hi
geolib.pcp(a, hi_r, FIVE, how="rank", highlight=hl); a.set_title("As published: file order — healthcare and case rate three axes apart")
geolib.pcp(b, hi_r, order, how="rank", highlight=hl); b.set_title("Greedy |r| order: they sit side by side — the X-shaped waist, r = −0.80")
for ax_ in (a, b): ax_.text(0.0, -0.17, "axes rank-scaled; one region brushed in orange", transform=ax_.transAxes, fontsize=8, color=PALETTE["ink_soft"])
done(fig, 4, "Redesign: axis order from geolib.corr_chain, fixed before looking at the picture.")

# ------------------------------------------------------------------ 5
hdr(5, "quantile classes on a flat surface")
f5 = pd.read_csv(f"{D}/case05_flat_rates.csv"); f5["rate"] = f5.cases / f5.population * 1e5
join_check([f["code"] for f in feats], f5.code, "case05")
p5 = f5.cases.sum() / f5.population.sum() * 1e5
print(f"rate {f5.rate.min():.2f}–{f5.rate.max():.2f}; spread {(f5.rate.max() - f5.rate.min()):.2f} = {(f5.rate.max() - f5.rate.min()) / f5.rate.mean():.1%} of mean; pooled {p5:.2f}; CV {f5.rate.std() / f5.rate.mean():.1%}")
q = geolib.breaks(f5.rate, "quantile", 5); print("quantile edges:", np.round(q, 2), "class counts", np.bincount(geolib.class_of(f5.rate, q)))
print(f"gap between class edges: {np.diff(q).round(2)}; GVF quantile {geolib.gvf(f5.rate, q):.2f}")
fl = geolib.funnel_limits(f5.population, p5)
lo_i = np.interp(f5.population, fl.population, fl.lo); hi_i = np.interp(f5.population, fl.population, fl.hi)
outside = int(((f5.rate < lo_i) | (f5.rate > hi_i)).sum())
print(f"districts outside the 95% Poisson funnel: {outside} of 24 (about 1 expected by chance)")
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 5.2))
geolib.choropleth(a, feats, dict(zip(f5.code, f5.rate)), scheme="quantile", legend_title="cases per 100,000 residents\n(quantile classes)", fmt="{:,.2f}")
a.set_title("As published: five quantile classes of 31.07–33.40")
pp = np.sort(f5.population.values)
fx = geolib.funnel_limits(np.linspace(pp.min(), pp.max(), 200), p5)
b.fill_between(fx.population / 1e6, fx.lo, fx.hi, color=PALETTE["grid"], label="95% Poisson limits around the pooled rate")
b.axhline(p5, color=GREY); b.scatter(f5.population / 1e6, f5.rate, color=BLUE, zorder=3)
b.set_ylim(0, 45); b.set_xlabel("Population, millions"); b.set_ylabel("Cases per 100,000 residents (y from 0)")
b.set_title(f"Same rates in a funnel: {outside} of 24 outside the limits — one flat surface")
b.legend(loc="lower right")
done(fig, 5, "Redesign: the same rates tested against Poisson noise instead of forced into five classes.")

# ------------------------------------------------------------------ 6
hdr(6, "small-area rates")
sm = pd.read_csv(f"{D}/smallarea_cases.csv"); sm["rate"] = sm.cases / sm.population * 1e5
p6 = sm.cases.sum() / sm.population.sum() * 1e5
w = sm.loc[sm.rate.idxmax()]
print(f"40 units; pooled {p6:.2f}; worst {w.unit} {w.rate:.1f} = {w.rate / p6:.1f}x from {int(w.cases)} cases in {int(w.population):,}")
big_ = sm[sm.population > 100000]; print(f"{len(big_)} units >100,000: rates {big_.rate.min():.1f}–{big_.rate.max():.1f}")
fl = geolib.funnel_limits(sm.population, p6)
lo_i = np.interp(sm.population, fl.population, fl.lo); hi_i = np.interp(sm.population, fl.population, fl.hi)
out6 = (sm.rate < lo_i) | (sm.rate > hi_i)
print(f"units outside the 95% funnel: {int(out6.sum())} of 40 ({list(sm.unit[out6])}); with 40 units about {0.05 * 40:.0f} are expected outside by chance alone")
fl3 = geolib.funnel_limits(sm.population, p6, z=3.09)
hi3 = np.interp(sm.population, fl3.population, fl3.hi)
print(f"at 99.8% limits (z=3.09, the usual choice for ~40 units): {int((sm.rate > hi3).sum())} units above; U32 upper limit {np.interp(22000, fl3.population, fl3.hi):.1f} vs its rate {w.rate:.1f}")
print(f"U32: one more/less case moves its rate by {1 / w.population * 1e5:.1f} per 100,000 (±{1 / w.population * 1e5 / w.rate * 100:.0f}% of its own value)")
print("true underlying rate is the same in every unit (per the data dictionary) -> every difference is Poisson noise")
print("top-5 rates vs population:", sm.nlargest(5, "rate")[["unit", "rate", "population"]].round(1).values.tolist())
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.8))
s_ = sm.sort_values("rate", ascending=False)
a.bar(s_.unit, s_.rate, color=[ORANGE if u == "U32" else BLUE for u in s_.unit]); a.set_ylim(0)
a.tick_params(axis="x", labelrotation=90, labelsize=7)
a.set_ylabel("Cases per 100,000 residents"); a.set_title("As published: ranked rates — U32 'hotspot' at 4.7× national")
fx = geolib.funnel_limits(np.linspace(sm.population.min(), sm.population.max(), 200), p6)
b.fill_between(fx.population / 1e3, fx.lo, fx.hi, color=PALETTE["grid"], label="95% Poisson limits (pooled 8.72)")
b.axhline(p6, color=GREY)
b.scatter(sm.population / 1e3, sm.rate, color=BLUE, zorder=3); b.scatter([w.population / 1e3], [w.rate], color=ORANGE, zorder=4)
b.annotate("U32: 9 cases / 22,000", (w.population / 1e3, w.rate), xytext=(30, 6), textcoords="offset points", fontsize=8)
b.set_xlabel("Population, thousands"); b.set_ylabel("Cases per 100,000 residents"); b.set_ylim(0)
b.set_title("Funnel: 1 of 40 outside 95% limits, as chance alone predicts (~2)"); b.legend(loc="upper right")
done(fig, 6, "Redesign: rate against the population behind it, with Poisson control limits (geolib.funnel_limits).")

# ------------------------------------------------------------------ 7
hdr(7, "modifiable areal unit problem")
r24 = np.corrcoef(dh.income_pc_usd, dh.rate)[0, 1]
z = dh.groupby("zone").agg(cases=("cases", "sum"), pop=("population", "sum"))
z["rate"] = z.cases / z["pop"] * 1e5
z["income"] = dh.groupby("zone").apply(lambda g: (g.income_pc_usd * g.population).sum() / g.population.sum(), include_groups=False) \
    if pd.__version__ >= "2.2" else dh.groupby("zone").apply(lambda g: (g.income_pc_usd * g.population).sum() / g.population.sum())
r6 = np.corrcoef(z.income, z.rate)[0, 1]
print(f"r(income, rate) across 24 districts = {r24:+.3f}; across the same land cut into 6 zones = {r6:+.3f} (income population-weighted)")
print("zone table:", z.round(1).to_dict("index"))
# bootstrap-free sensitivity: all ways to merge the 24 districts into the given zones is one; random 6-way contiguous? use random groupings
rng = np.random.default_rng(0)
rs = []
for _ in range(2000):
    g = rng.integers(0, 6, 24)
    t = dh.assign(g=g).groupby("g").agg(c=("cases", "sum"), p=("population", "sum"))
    inc = dh.assign(g=g).groupby("g").apply(lambda x: (x.income_pc_usd * x.population).sum() / x.population.sum(), include_groups=False) \
        if pd.__version__ >= "2.2" else dh.assign(g=g).groupby("g").apply(lambda x: (x.income_pc_usd * x.population).sum() / x.population.sum())
    if len(t) == 6: rs.append(np.corrcoef(inc, t.c / t.p)[0, 1])
rs = np.array(rs)
print(f"2,000 random (non-contiguous) 6-zone regroupings of the same 24 districts: r from {rs.min():+.2f} to {rs.max():+.2f} (median {np.median(rs):+.2f})")
print("districts_alt.geojson has no attribute table, so the second 24-unit partition cannot be scored without areal "
      "interpolation (an assumption I do not make).")
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.8))
a.scatter(dh.income_pc_usd / 1000, dh.rate, color=BLUE); m, c0 = np.polyfit(dh.income_pc_usd / 1000, dh.rate, 1)
xs = np.array([dh.income_pc_usd.min(), dh.income_pc_usd.max()]) / 1000; a.plot(xs, m * xs + c0, color=ORANGE)
a.set_xlabel("District income, USD thousand per person"); a.set_ylabel("Cases per 100,000 residents")
a.set_title(f"As published: 24 districts, r = {r24:+.2f} ('weak')")
b.hist(rs, bins=30, color=GREY); b.axvline(r24, color=BLUE, lw=2); b.axvline(r6, color=ORANGE, lw=2)
b.text(r24, b.get_ylim()[1] * 0.92, f" 24 districts {r24:+.2f}", color=BLUE, fontsize=8)
b.text(r6, b.get_ylim()[1] * 0.78, f" 6 official zones {r6:+.2f}", color=ORANGE, fontsize=8, ha="right")
b.set_xlabel("r(income, rate) when the same 24 districts are randomly regrouped into 6 zones")
b.set_ylabel("Number of regroupings (of 2,000)"); b.set_title("Same people, other groupings: r runs from −0.99 to +0.93")
done(fig, 7, "Redesign: report the correlation's range across zonings, not a single number (MAUP, Openshaw 1984).")

# ------------------------------------------------------------------ 8
hdr(8, "ink follows area, not people")
dh["area"] = dh.area_km2
t5 = dh.nlargest(5, "population")
print(f"top-5 populous {list(t5.code)}: {t5.area.sum() / dh.area.sum():.1%} of land, {t5.population.sum() / dh.population.sum():.1%} of people")
e = geolib.breaks(dh.rate, "natural", 5); dh["cls"] = geolib.class_of(dh.rate, e)
dark = dh[dh.cls >= 3]
print(f"breaks {np.round(e, 1)}; top two classes: {len(dark)} districts = {dark.area.sum() / dh.area.sum():.1%} of land but "
      f"{dark.population.sum() / dh.population.sum():.1%} of people and {dark.cases.sum() / dh.cases.sum():.1%} of cases")
dh["dens"] = dh.population / dh.area
print(f"r(rate, density) = {np.corrcoef(dh.rate, dh.dens)[0, 1]:+.3f}; r(rate, log density) = {np.corrcoef(dh.rate, np.log(dh.dens))[0, 1]:+.3f}")
dense = dh[dh.dens > dh.dens.median()]; sparse = dh[dh.dens <= dh.dens.median()]
print(f"pooled rate: denser half {dense.cases.sum() / dense.population.sum() * 1e5:.1f} vs sparser half {sparse.cases.sum() / sparse.population.sum() * 1e5:.1f} per 100,000")
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 5.6))
geolib.choropleth(a, feats, dict(zip(dh.code, dh.rate)), scheme="natural", legend_title="cases per 100,000 residents", fmt="{:,.1f}")
a.set_title("As published: a lot of dark ink (area)")
o = dh.sort_values("rate", ascending=False).reset_index(drop=True)
x0 = np.concatenate([[0], np.cumsum(o.population)[:-1]]) / dh.population.sum() * 100
wd = o.population / dh.population.sum() * 100
b.bar(x0, o.rate, width=wd, align="edge", color=[BLUE if c < 3 else ORANGE for c in o.cls], edgecolor="white")
b.axhline(POOLED, color=PALETTE["ink"], lw=1, ls="--"); b.text(100, POOLED + 1.5, f"national {POOLED:.1f}", ha="right", fontsize=8)
b.set_xlim(0, 100); b.set_ylim(0); b.set_xlabel("Cumulative % of population (bar width = district population)"); b.set_ylabel("Cases per 100,000 residents")
b.set_title("Width = people: dark classes hold 26% of residents;\nrate is unrelated to density (r = 0.00)")
done(fig, 8, "Redesign: the same rates with bar width ∝ population (ink goes to people, not land).")

# ------------------------------------------------------------------ 9
hdr(9, "radar chart: enclosed area depends on axis order")
rp = pd.read_csv(f"{D}/region_profiles.csv")
def rad_area(v): v = np.asarray(v, float); return 0.5 * np.sin(2 * np.pi / len(v)) * np.sum(v * np.roll(v, -1))
A, B = rp.region_a.values, rp.region_b.values
print(f"means {A.mean():.1f} vs {B.mean():.1f} (diff {A.mean() - B.mean():.2f}); file-order areas {rad_area(A):,.0f} vs {rad_area(B):,.0f}")
res = []
for p in itertools.permutations(range(1, 6)):
    o_ = [0] + list(p)
    if o_[1] > o_[-1]: continue
    res.append((rad_area(A[o_]), rad_area(B[o_])))
res = np.array(res)
print(f"all {len(res)} distinct axis orders: A larger in {(res[:, 0] > res[:, 1]).sum()}, B larger in {(res[:, 0] < res[:, 1]).sum()}; "
      f"A area {res[:, 0].min():,.0f}–{res[:, 0].max():,.0f}, B {res[:, 1].min():,.0f}–{res[:, 1].max():,.0f}")
print("per-indicator gaps:", dict(zip(rp.indicator, (A - B).round(1))))
fig = plt.figure(figsize=(12.5, 5))
a = fig.add_subplot(1, 2, 1, projection="polar"); b = fig.add_subplot(1, 2, 2)
th = np.linspace(0, 2 * np.pi, 6, endpoint=False)
for v, c, l in [(A, BLUE, "Region A"), (B, ORANGE, "Region B")]:
    a.plot(np.append(th, th[0]), np.append(v, v[0]), color=c, label=l); a.fill(th, v, color=c, alpha=0.25)
a.set_xticks(th); a.set_xticklabels(rp.indicator, fontsize=8); a.set_ylim(0, 100); a.legend(loc="lower left", bbox_to_anchor=(-0.1, -0.1))
a.set_title("As published: file order, area 9,933 vs 9,433")
y = np.arange(len(rp))
b.hlines(y, B, A, color=GREY); b.scatter(A, y, color=BLUE, label="Region A", zorder=3); b.scatter(B, y, color=ORANGE, label="Region B", zorder=3)
b.set_yticks(y); b.set_yticklabels(rp.indicator); b.set_xlim(0, 100); b.set_xlabel("Rating (0–100, common scale)")
b.set_title(f"Dot plot: A wins 3 indicators, B wins 3; means 62.3 vs 62.0 — a tie"); b.legend(loc="lower right"); b.invert_yaxis()
done(fig, 9, "Redesign: position on a common scale per indicator; no enclosed area.")
print("\nAll nine done.")
