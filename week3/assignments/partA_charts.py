from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vizlib import PALETTE, style_defaults

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

style_defaults(dpi=150)
C = PALETTE["series"]


def save_chart(fig, name: str):
    path = ROOT / f"{name}.png"
    fig.savefig(path, dpi=400, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def case01():
    df = pd.read_csv(DATA / "case01_helmet_rickshaw.csv")
    grp = df.groupby("helmet_grade", as_index=False).agg(
        trips=("trips", "sum"),
        head_injuries=("head_injuries", "sum"),
    )
    grp["injuries_per_1000"] = grp["head_injuries"] / grp["trips"] * 1000
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(data=grp, x="helmet_grade", y="injuries_per_1000", palette=[C[0], C[1]], ax=ax)
    ax.set_title("Premium-certified helmets have 2.5x the head-injury rate", fontsize=16)
    ax.set_xlabel("Helmet certification", fontsize=12)
    ax.set_ylabel("Head injuries per 1,000 trips", fontsize=12)
    ax.tick_params(labelsize=11)
    for i, v in enumerate(grp["injuries_per_1000"]):
        ax.text(i, v + 0.4, f"{v:.2f}", ha="center", va="bottom", fontsize=11)
    ax.set_ylim(0, max(grp["injuries_per_1000"]) * 1.45)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return save_chart(fig, "partA_case01")


def case02():
    df = pd.read_csv(DATA / "case02_chai_quizzes.csv")
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(data=df, x="cups_doodh_patti_sold", y="quiz_failures", scatter_kws={"s": 42}, line_kws={"color": C[1]}, ax=ax)
    r = df["cups_doodh_patti_sold"].corr(df["quiz_failures"])
    ax.set_title("Canteen chai sales predict quiz failures", fontsize=16)
    ax.set_xlabel("Cups sold", fontsize=12)
    ax.set_ylabel("Quiz failures", fontsize=12)
    ax.tick_params(labelsize=11)
    ax.text(0.05, 0.95, f"r = {r:.2f}", transform=ax.transAxes, va="top", fontsize=12, bbox=dict(facecolor="white", alpha=0.8, pad=6))
    fig.tight_layout()
    return save_chart(fig, "partA_case02")


def case03():
    df = pd.read_csv(DATA / "case03_aqi_monitors.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    daily = df.groupby("date")["aqi"].mean().reset_index()
    daily = daily.sort_values("date").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(daily["date"], daily["aqi"], color=C[0], linewidth=2.5)
    ax.axvline(pd.Timestamp("2026-03-01"), color=C[1], linestyle="--", linewidth=1.8)
    before = daily.loc[:60, "aqi"].mean()
    after = daily.loc[60:, "aqi"].mean()
    ax.axhline(before, color=C[2], linestyle=":", alpha=0.9)
    ax.axhline(after, color=C[2], linestyle="--", alpha=0.9)
    ax.set_title("The Smog Action Plan cut Lahore's AQI by a third", fontsize=16)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Mean AQI", fontsize=12)
    ax.tick_params(labelsize=11)
    ax.set_ylim(0, max(daily["aqi"].max() * 1.2, 250))
    ax.text(pd.Timestamp("2026-01-15"), before + 8, f"before: {before:.0f}", color=C[2], fontsize=11)
    ax.text(pd.Timestamp("2026-03-15"), after + 8, f"after: {after:.0f}", color=C[2], fontsize=11)
    fig.tight_layout()
    return save_chart(fig, "partA_case03")


def case04():
    df = pd.read_csv(DATA / "case04_quartet_depts.csv")
    out = df.groupby("department").agg(
        n=("department", "size"),
        mean_hours=("study_hours_per_week", "mean"),
        mean_score=("final_score_out_of_20", "mean"),
        sd_hours=("study_hours_per_week", "std"),
        sd_score=("final_score_out_of_20", "std"),
    ).reset_index()
    out["r"] = [
        df[df["department"] == dept]["study_hours_per_week"].corr(df[df["department"] == dept]["final_score_out_of_20"]) for dept in out["department"]
    ]
    out["slope"] = [
        np.polyfit(df[df["department"] == dept]["study_hours_per_week"], df[df["department"] == dept]["final_score_out_of_20"], 1)[0] for dept in out["department"]
    ]
    out["mean_hours"] = out["mean_hours"].map(lambda v: f"{v:.1f}")
    out["mean_score"] = out["mean_score"].map(lambda v: f"{v:.1f}")
    out["sd_hours"] = out["sd_hours"].map(lambda v: f"{v:.2f}")
    out["sd_score"] = out["sd_score"].map(lambda v: f"{v:.2f}")
    out["r"] = out["r"].map(lambda v: f"{v:.3f}")
    out["slope"] = out["slope"].map(lambda v: f"{v:.3f}")
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.axis("off")
    table = ax.table(
        cellText=out[["department", "n", "mean_hours", "mean_score", "sd_hours", "sd_score", "r", "slope"]].to_numpy(),
        colLabels=["department", "n", "mean hours", "mean score", "SD hours", "SD score", "r", "slope"],
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)
    ax.set_title("Four departments behave identically in the summary table", fontsize=22, pad=20)
    fig.tight_layout()
    return save_chart(fig, "partA_case04")


def case05():
    df = pd.read_csv(DATA / "case05_same_stats_shapes.csv")
    out = df.groupby("shape_name").agg(
        n=("hours_on_platform", "size"),
        mean_hours=("hours_on_platform", "mean"),
        mean_score=("assessment_score", "mean"),
        sd_hours=("hours_on_platform", "std"),
        sd_score=("assessment_score", "std"),
    ).reset_index()
    out["r"] = [
        df[df["shape_name"] == s]["hours_on_platform"].corr(df[df["shape_name"] == s]["assessment_score"]) for s in out["shape_name"]
    ]
    out["mean_hours"] = out["mean_hours"].map(lambda v: f"{v:.1f}")
    out["mean_score"] = out["mean_score"].map(lambda v: f"{v:.1f}")
    out["sd_hours"] = out["sd_hours"].map(lambda v: f"{v:.2f}")
    out["sd_score"] = out["sd_score"].map(lambda v: f"{v:.2f}")
    out["r"] = out["r"].map(lambda v: f"{v:.3f}")
    fig, ax = plt.subplots(figsize=(14, 5.5))
    ax.axis("off")
    table = ax.table(
        cellText=out[["shape_name", "n", "mean_hours", "mean_score", "sd_hours", "sd_score", "r"]].to_numpy(),
        colLabels=["shape_name", "n", "mean h", "mean score", "SD h", "SD score", "r"],
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)
    ax.set_title("Five cohorts share identical summary statistics", fontsize=22, pad=20)
    fig.tight_layout()
    return save_chart(fig, "partA_case05")


def case06():
    df = pd.read_csv(DATA / "case06_sensor_matrix.csv")
    cols = [col for col in df.columns if col not in ["age_band", "study_site", "hr_device_model"] and pd.api.types.is_numeric_dtype(df[col])]
    corr = df[cols].corr()
    fig, ax = plt.subplots(figsize=(12, 9))
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="Reds", mask=mask, vmin=-1, vmax=1, center=0, cbar=True, ax=ax, annot_kws={"size": 8})
    ax.set_title("Creatinine tracks HbA1c — a finding", fontsize=20)
    ax.tick_params(axis="x", labelrotation=45, labelsize=9)
    ax.tick_params(axis="y", labelrotation=0, labelsize=9)
    fig.tight_layout()
    return save_chart(fig, "partA_case06")


def case07():
    df = pd.read_csv(DATA / "case07_dual_axis_series.csv")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax2 = ax.twinx()
    ax.plot(df["month"], df["revenue_pkr_m"], color=C[0], marker="o", linewidth=2.5, label="revenue")
    ax2.plot(df["month"], df["cost_pkr_m"], color=C[1], marker="s", linewidth=2.5, label="cost")
    ax.set_ylim(50, 80)
    ax2.set_ylim(40, 56)
    ax.set_title("ShaheenGo ran at a loss until May", fontsize=16)
    ax.set_ylabel("Revenue (PKR m)", fontsize=12)
    ax2.set_ylabel("Cost (PKR m)", fontsize=12)
    ax.tick_params(labelsize=11)
    ax2.tick_params(labelsize=11)
    fig.tight_layout()
    return save_chart(fig, "partA_case07")


def case08():
    df = pd.read_csv(DATA / "vitals_10k.csv")
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, nbins in zip(axes, [3, 45, 400]):
        ax.hist(df["systolic"], bins=nbins, color=C[0], edgecolor="white")
        ax.set_title(f"bins = {nbins}", fontsize=12)
        ax.set_xlabel("Systolic (mmHg)", fontsize=11)
        ax.set_ylabel("Count", fontsize=11)
        ax.tick_params(labelsize=10)
    fig.suptitle("Three bin widths, three different distributions", fontsize=18)
    fig.tight_layout()
    return save_chart(fig, "partA_case08")


def case09():
    df = pd.read_csv(DATA / "vitals_10k.csv")
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.kdeplot(df["spo2"], fill=True, color=C[0], ax=ax)
    ax.axvline(100, color=C[1], linestyle="--", linewidth=1.8)
    ax.set_xlim(80, 108)
    ax.set_title("4.4% of the density sits above 100% saturation", fontsize=16)
    ax.set_xlabel("SpO2 (%)", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)
    ax.tick_params(labelsize=11)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    return save_chart(fig, "partA_case09")


def build_diagnosis_pdf():
    cases = [
        ("Case 1", "The bar chart is reproduced using injuries per 1,000 trips; the real issue is the baseline and the hidden risk composition.", "partA_case01.png"),
        ("Case 2", "The linear relation is real, but the mechanism is the monthly demand-and-exam cycle rather than a stable causal effect.", "partA_case02.png"),
        ("Case 3", "The apparent drop is partly a baseline choice: the chart compares mean across all stations after a policy change, not a clean before/after matched design.", "partA_case03.png"),
        ("Case 4", "The same summary statistics are not the same data distribution; the table hides non-linear structure and means the departments are not functionally identical.", "partA_case04.png"),
        ("Case 5", "The cohorts are forced to identical moments, but the shape differences are masked in the table; the chart is not evidence of equality in broader form.", "partA_case05.png"),
        ("Case 6", "The heatmap drawing issue is the unbounded red scale and the no-mask display; the real scientific issue is that the matrix is screening data and not a causal result.", "partA_case06.png"),
        ("Case 7", "The dual axis is a distortion: the cost and revenue series are shown on different scales, so the eye compares different baselines and makes the loss look bigger.", "partA_case07.png"),
        ("Case 8", "Binning choice changes the story; the data are the same, but bin width is a design choice and the distribution is not stable across the three panels.", "partA_case08.png"),
        ("Case 9", "The KDE is not a distribution of observed values, and the plotted density extends beyond the physical ceiling of 100% oxygen saturation.", "partA_case09.png"),
    ]

    pdf_path = ROOT / "partA_diagnosis.pdf"
    with PdfPages(pdf_path) as pdf:
        for title, note, img_name in cases:
            fig = plt.figure(figsize=(8.5, 11))
            fig.text(0.06, 0.94, title, fontsize=18, fontweight="bold")
            fig.text(0.06, 0.88, note, fontsize=11)
            if (ROOT / img_name).exists():
                image = plt.imread(ROOT / img_name)
                ax = fig.add_axes([0.08, 0.12, 0.84, 0.66])
                ax.imshow(image)
                ax.axis("off")
            pdf.savefig(fig)
            plt.close(fig)
    print(f"wrote {pdf_path}")


def main():
    case01()
    case02()
    case03()
    case04()
    case05()
    case06()
    case07()
    case08()
    case09()
    build_diagnosis_pdf()
    print("Part A charts and diagnosis PDF generated successfully.")


if __name__ == "__main__":
    main()
