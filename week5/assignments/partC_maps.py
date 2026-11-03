"""
Week 5 · Part C — the two-map activity.

    python3 partC_maps.py                  # builds partC_mapA.png, partC_mapB.png and prints the self-check
    python3 partC_maps.py --run NAME       # run ONE real reader through the activity (order matters: A, then B)
    python3 partC_maps.py --report         # mean overlap across the readers recorded so far

partC_reader_results.csv is only ever written by --run from what a person actually answers.
Nothing in this script generates reader data.
"""
import os
import sys
import subprocess
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import geolib
from vizlib import style_defaults, save_fig

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "data")
RES = os.path.join(HERE, "partC_reader_results.csv")
cc = pd.read_csv(f"{D}/county_crime.csv")
cc["rate"] = cc.crimes_reported / cc.population * 1e5


def maps():
    style_defaults(); plt.rcParams["axes.titlesize"] = 10
    feats_all = geolib.read_geojson(f"{D}/districts.geojson")
    codes = set(cc.code)
    feats = [f for f in feats_all if f["code"] in codes]
    left_out = sorted(f["code"] for f in feats_all if f["code"] not in codes)
    print(f"join: {len(feats)} polygons matched {len(cc)} counties; {len(left_out)} polygons without a county left out: {left_out}")
    assert len(feats) == len(cc)
    for name, col, title, fmt in [("A", "crimes_reported", "crimes reported (count)", "{:,.0f}"),
                                  ("B", "rate", "crimes per 100,000 residents", "{:,.0f}")]:
        fig, ax = plt.subplots(figsize=(5.2, 6.4))
        e = geolib.choropleth(ax, feats, dict(zip(cc.code, cc[col])), scheme="quantile", k=5,
                              legend_title=f"{title}\n(5 quantile classes)", fmt=fmt)
        lab = {f["code"]: f["name"] for f in feats}
        for f in feats:
            lat_ts = np.mean([p[1] for g in feats for p in g["ring"]])
            lon, lat = geolib.representative_point(f["ring"])
            x, y = geolib.equal_area_xy([lon], [lat], lat_ts=lat_ts)
            ax.text(x[0], y[0], lab[f["code"]], fontsize=6.5, ha="center", va="center")
        ax.set_title(f"Map {name}")
        save_fig(fig, os.path.join(HERE, f"partC_map{name}.png"),
                 note=f"Counties joined on code to districts.geojson (fictional federation); {len(left_out)} unmatched polygons "
                      f"({', '.join(left_out)}) left out. Equal-area projection. Synthetic data, CDB601220 Week 5.")
        plt.close(fig)
        print(f"Map {name}: breaks", np.round(e, 1))


def check():
    r = np.corrcoef(cc.crimes_reported, cc.population)[0, 1]
    t_c = list(cc.nlargest(3, "crimes_reported").county); t_r = list(cc.nlargest(3, "rate").county)
    print(f"r(crimes, population) = {r:+.3f}\ntop 3 by count: {t_c}\ntop 3 by rate:  {t_r}\noverlap: {len(set(t_c) & set(t_r))}")
    rc = cc.crimes_reported.rank(ascending=False); rr = cc.rate.rank(ascending=False)
    mv = (rc - rr).abs() >= 3
    print(f"counties moving 3+ ranks between the two lists: {int(mv.sum())} -> {list(cc.county[mv])}")
    for n in ("Elmsworth", "Hollowfield"):
        x = cc[cc.county == n].iloc[0]
        print(f"  {n}: population {x.population:,}; count rank {int(rc[x.name])} of 20 -> rate rank {int(rr[x.name])}")


def run(reader):
    names = sorted(cc.county)
    print("Counties:", ", ".join(names))
    out = {"reader": reader}
    for m in ("A", "B"):
        subprocess.Popen(["open", os.path.join(HERE, f"partC_map{m}.png")])
        input(f"\nShow the reader MAP {m} only. Ask: 'Which three counties would you send extra police to, and why?' Press Enter then type their three.")
        picks = [p.strip().title() for p in input("Their three, comma-separated: ").split(",")]
        bad = [p for p in picks if p not in names]
        assert not bad and len(picks) == 3, f"need exactly 3 valid county names; got {picks}"
        out[f"mapA_three" if m == "A" else "mapB_three"] = ";".join(picks)
        out[f"why_{m}"] = input("Their stated reason (short): ").strip()
    out["overlap"] = len(set(out["mapA_three"].split(";")) & set(out["mapB_three"].split(";")))
    pd.DataFrame([out]).to_csv(RES, mode="a", header=not os.path.exists(RES), index=False)
    print("recorded:", out)


if __name__ == "__main__":
    if "--run" in sys.argv:
        run(sys.argv[sys.argv.index("--run") + 1])
    elif "--report" in sys.argv:
        r = pd.read_csv(RES); print(r[["reader", "overlap"]]); print(f"readers: {len(r)}  mean overlap: {r.overlap.mean():.2f}")
        if len(r) < 5: print("WARNING: fewer than 5 readers — the brief requires at least five real readers.")
    else:
        maps(); check()
        print("\nNext: python3 partC_maps.py --run <reader>   (five readers minimum, Map A first, then Map B; no revising A)")
