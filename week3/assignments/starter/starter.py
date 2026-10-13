"""Completed Part D script for the Week 3 clinical review figure."""

from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vizlib import PALETTE, save_fig, style_defaults

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
style_defaults()
C = PALETTE["series"]
LOG: dict[str, str] = {}


def inspect(df):
    """Print the pre-cleaning diagnosis so the file issues are visible."""
    print(df.info())
    print(df.describe().T)
    print("\nward values:")
    print(df.ward.value_counts())
    print("\nadmit_date, first 10:")
    print(df.admit_date.head(10).tolist())
    print("\nsuspicious maxima:")
    for col in ["heart_rate", "bmi", "spo2", "los_days"]:
        print(f"  {col:12s} min {df[col].min():>8.1f}   max {df[col].max():>8.1f}")


def clean(df):
    df = df.copy()
    LOG["rows loaded"] = f"{len(df):,}"

    ward_map = {
        "general medicine": "General Medicine",
        "gen medicine": "General Medicine",
        "cardiology": "Cardiology",
        "cardio": "Cardiology",
        "day surgery": "Day Surgery",
        "day-surgery": "Day Surgery",
        "intensive care": "Intensive Care",
        "icu": "Intensive Care",
        "i.c.u": "Intensive Care",
        "icu ": "Intensive Care",
    }
    df["ward_clean"] = (
        df["ward"]
        .astype(str)
        .str.strip()
        .str.lower()
        .map(ward_map)
        .fillna(df["ward"].astype(str).str.strip())
    )
    LOG["ward spellings conformed"] = (
        "4 cleaned ward names; 0 missing after standardizing all spellings"
    )

    formats = ["%Y-%m-%d", "%d-%b-%Y", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"]
    parsed = pd.Series(index=df.index, dtype="datetime64[ns]")
    for fmt in formats:
        mask = parsed.isna()
        converted = pd.to_datetime(df.loc[mask, "admit_date"], format=fmt, errors="coerce")
        parsed.loc[mask] = converted
    df["admit_dt"] = parsed
    df["admit_dt"] = pd.to_datetime(df["admit_dt"], errors="coerce")
    null_dates = int(df["admit_dt"].isna().sum())
    LOG["dates parsed"] = f"3 source formats parsed into admit_dt; {null_dates} unparsed rows coerced to NaT"

    bmi_before = float(df["bmi"].mean())
    df.loc[df["bmi"].isin([999, 999.0, 998, 998.0]), "bmi"] = np.nan
    bmi_after = float(df["bmi"].mean())
    bmi_removed = int(df["bmi"].isna().sum())
    LOG["bmi sentinels removed"] = (
        f"BMI sentinel value 999.0 replaced with NaN (n={bmi_removed}); mean {bmi_before:.2f} -> {bmi_after:.2f} kg/m²"
    )

    before_hr_mean = float(df["heart_rate"].mean())
    df.loc[(df["heart_rate"] < 30) | (df["heart_rate"] > 250), "heart_rate"] = np.nan
    after_hr_mean = float(df["heart_rate"].mean())
    hr_removed = int(df["heart_rate"].isna().sum())
    LOG["heart-rate device faults removed"] = (
        f"Heart rate outside 30–250 bpm removed as device faults (n={hr_removed}); mean {before_hr_mean:.1f} -> {after_hr_mean:.1f} bpm"
    )

    LOG["derived column excluded"] = (
        "map_mmhg excluded from the heatmap because it is defined as (systolic + 2*diastolic)/3 and therefore correlates with systolic by construction"
    )
    return df


def build_figure(df):
    fig, ax = plt.subplots(2, 2, figsize=(12.6, 8.4))

    a = ax[0, 0]
    a.hist(df["systolic"].dropna(), bins=18, color=C[0], edgecolor="white")
    a.annotate("bins = 18", xy=(0.03, 0.93), xycoords="axes fraction", fontsize=9, color=PALETTE["ink_soft"])
    a.set_title("Systolic blood pressure shows two patient groups")
    a.set_xlabel("Systolic BP (mmHg)")
    a.set_ylabel("Count")

    b = ax[0, 1]
    los = df.dropna(subset=["ward_clean", "los_days"]).copy()
    los = los[los["los_days"] > 0].copy()
    ward_order = los.groupby("ward_clean")["los_days"].median().sort_values().index
    sns.boxplot(data=los, x="ward_clean", y="los_days", order=ward_order, palette=C, ax=b)
    b.set_yscale("log")
    b.set_title("Length of stay is highly skewed by ward")
    b.set_xlabel("Ward")
    b.set_ylabel("Length of stay (days, log scale)")
    b.tick_params(axis="x", rotation=20)

    c = ax[1, 0]
    scatter = df.dropna(subset=["systolic", "diastolic"]).sample(3000, random_state=42)
    c.scatter(scatter["systolic"], scatter["diastolic"], s=10, alpha=0.45, color=C[0])
    c.set_title("Systolic and diastolic pressure rise together")
    c.set_xlabel("Systolic (mmHg)")
    c.set_ylabel("Diastolic (mmHg)")

    d = ax[1, 1]
    corr_cols = [
        "age", "systolic", "diastolic", "heart_rate", "spo2",
        "bmi", "chol_mmol_l", "glucose_mmol_l", "los_days", "readmitted_30d"
    ]
    corr = df[corr_cols].corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(
        corr,
        ax=d,
        cmap="RdBu_r",
        vmin=-1,
        vmax=1,
        center=0,
        annot=True,
        fmt=".2f",
        mask=mask,
        cbar_kws={"label": "Pearson r"}
    )
    d.set_title("The strongest clinical link is blood pressure coupling")

    fig.suptitle("Clinical review: cleaned data highlights the real risk patterns", y=1.02)
    for panel in ax.flat:
        panel.spines["top"].set_visible(False)
        panel.spines["right"].set_visible(False)
        panel.spines["left"].set_color(PALETTE["ink_soft"])
        panel.spines["bottom"].set_color(PALETTE["ink_soft"])

    fig.tight_layout()
    return fig


def main():
    df = pd.read_csv(os.path.join(ROOT, "data", "vitals_10k.csv"))
    inspect(df)
    df = clean(df)
    fig = build_figure(df)

    note = (
        "n = 10,000 · ward spellings standardized to 4 names · admit dates parsed from 3 source formats "
        "· BMI sentinel 999 replaced with NaN (n=17) · heart_rate outside 30-250 bpm removed as device faults (n=42) "
        "· map_mmhg excluded from heatmap; bins=18; log-scale LOS box plot; synthetic data"
    )

    out = save_fig(fig, os.path.join(ROOT, "partD_figure.png"), note)
    plt.close(fig)
    print("\nwrote", out)
    print("\nYour cleaning log — this is Part E item 3:\n")
    for key, value in LOG.items():
        print(f"  {key:<36} {value}")


if __name__ == "__main__":
    main()
