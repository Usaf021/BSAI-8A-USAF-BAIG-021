"""Completed Part C: evaluate a palette against colour-vision-deficiency simulation."""

from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vizlib import (PALETTE, save_fig, simulate_cvd, style_defaults, verdict, worst_pair)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
style_defaults()

MY_PALETTE = ["#1F77B4", "#FF7F0E", "#2CA02C", "#D62728"]
MY_LABEL = "matplotlib tab10, first four"
COURSE_PALETTE = PALETTE["series"] + [PALETTE["series_4th"]]
KINDS = ["normal", "deutan", "protan", "tritan"]


def swatch_sheet(palettes, path):
    fig, axes = plt.subplots(len(palettes), len(KINDS), figsize=(3.0 * len(KINDS), 2.1 * len(palettes)))
    if len(palettes) == 1:
        axes = axes.reshape(1, -1)
    for row, (pal, label) in enumerate(palettes):
        for col, kind in enumerate(KINDS):
            ax = axes[row, col]
            shown = pal if kind == "normal" else simulate_cvd(pal, kind)
            for i, hexc in enumerate(shown):
                ax.add_patch(plt.Rectangle((i, 0), 0.92, 1, color=hexc))
                ax.text(i + 0.46, -0.22, f"S{i+1}", ha="center", fontsize=8, color=PALETTE["ink_soft"])
            ax.set_xlim(-0.1, len(pal))
            ax.set_ylim(-0.4, 1.1)
            ax.axis("off")
            ax.set_title(kind, fontsize=10)
        axes[row, 0].text(-0.05, 1.42, label, transform=axes[row, 0].transAxes, fontsize=11, fontweight="bold", color=PALETTE["ink"])
    fig.suptitle("Prove it, do not claim it", x=0.006, ha="left", fontsize=13, fontweight="bold", color=PALETTE["ink"])
    fig.tight_layout(rect=[0, 0, 1, 0.9])
    out = save_fig(fig, path, "Machado, Oliveira & Fernandes (2009) severity-1.0 matrices, applied in linear RGB.")
    plt.close(fig)
    return out


def audit(pal, label):
    """Print the worst pair and the verdict for each simulated colour-vision condition."""
    print(label)
    for kind in ["normal", "deutan", "protan", "tritan"]:
        i, j, a, b, d = worst_pair(pal, kind)
        print(f"  {kind:7s} closest pair  S{i} {a} vs S{j} {b}   ΔE {d:5.1f}   {verdict(d)}")
    print()


def main():
    out = swatch_sheet([(MY_PALETTE, MY_LABEL), (COURSE_PALETTE, "The course palette")], os.path.join(ROOT, "partC_palette.png"))
    print("wrote", out, "\n")

    audit(MY_PALETTE, MY_LABEL)
    audit(COURSE_PALETTE, "The course palette (3 slots + the 4th)")

    print("Rule for > 3 categories: use the first three palette slots for the main series, then add direct labels, grouping, or a table view instead of a fourth colour. The fourth slot is not a safe default because it collapses under simulation.")

    # Optional bonus: feed a rendered PNG into simulate_cvd() for a full-figure simulation check.


if __name__ == "__main__":
    main()
