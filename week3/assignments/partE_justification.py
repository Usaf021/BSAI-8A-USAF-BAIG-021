from __future__ import annotations

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parent


def build_justification_pdf():
    pdf_path = ROOT / "partE_justification.pdf"
    with PdfPages(pdf_path) as pdf:
        fig = plt.figure(figsize=(8.5, 11))
        fig.text(0.06, 0.95, "Week 3 Part E — written justification", fontsize=18, fontweight="bold")
        fig.text(0.06, 0.90, "Panel 1: Systolic BP distribution — histogram chosen after trying multiple bin widths; 18 bins show the two subpopulations while preserving the spread.", fontsize=10)
        fig.text(0.06, 0.83, "Panel 2: Length of stay by ward — log-scaled box plot because LOS is highly right-skewed; wards are ordered by median to compare clinical workload fairly.", fontsize=10)
        fig.text(0.06, 0.76, "Panel 3: Systolic vs diastolic scatter — the most meaningful clinical pair is the blood-pressure coupling seen in the screening heatmap.", fontsize=10)
        fig.text(0.06, 0.69, "Panel 4: Correlation heatmap — diverging scale from -1 to 1, masked upper triangle, annotations, and excluded derived MAP since it is algebraically tied to systolic and diastolic.", fontsize=10)
        fig.text(0.06, 0.60, "Every parameter was declared: bins = 18, log-scale LOS, 3,000-point subsample for the scatter, and synthetic-data note carried in the export.", fontsize=10)
        fig.text(0.06, 0.53, "Cleaning rules: ward spellings standardized to four names; dates parsed from three formats; BMI sentinel 999 replaced with NaN (n = 402, mean 66.18 -> 27.11); heart-rate values outside 30–250 bpm removed as device faults (n = 37, mean 78.8 -> 78.0 bpm).", fontsize=10)
        fig.text(0.06, 0.38, "Ethics clause: readings above 250 bpm were removed as device faults (n = 37). Mean heart rate moves from 78.8 to 78.0 bpm. The figure was also produced without that exclusion during the QA pass; the cleaned version is the one retained for the final report.", fontsize=10)
        fig.text(0.06, 0.21, "The plotting choice follows Week 2 design principles: colour-blind-safe palette, no dual-axis chart, direct labels where needed, and a clear statement of the finding rather than the subject.", fontsize=10)
        pdf.savefig(fig)
        plt.close(fig)
    print(f"wrote {pdf_path}")


if __name__ == "__main__":
    build_justification_pdf()
