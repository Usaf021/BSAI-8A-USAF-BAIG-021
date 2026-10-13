from __future__ import annotations

import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vizlib import lie_factor, lie_verdict

ROOT = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    df = pd.read_csv(os.path.join(ROOT, "data", "case07_lie_factor.csv"))
    rows = []

    for _, row in df.iterrows():
        lf, data_effect, graphic_effect = lie_factor(
            row["value_start"],
            row["value_end"],
            row["ink_start"],
            row["ink_end"],
            row["ink_dimension"],
        )
        rows.append(
            {
                "chart_id": row["chart_id"],
                "subject": row["subject"],
                "data_effect": data_effect,
                "graphic_effect": graphic_effect,
                "lie_factor": lf,
                "verdict": lie_verdict(lf),
            }
        )

    print("Chart audit for case07_lie_factor.csv\n")
    print(f'{"chart":<8}{"data effect":>12}{"graphic effect":>16}{"lie factor":>12}{"verdict":>20}')
    for item in rows:
        print(
            f'{item["chart_id"]:<8}'
            f'{item["data_effect"]:>12.3f}'
            f'{item["graphic_effect"]:>16.3f}'
            f'{item["lie_factor"]:>12.3f}'
            f'{item["verdict"]:>20}'
        )

    print("\nInterpretation:")
    print("- Chart C is the honest one (LF ≈ 1.0).")
    print("- A, B, D, and E distort the data by using a cut baseline, 2-D area scaling, or a misleading non-zero baseline.")
    print("- Charts B and E use ink_dimension=2 because the quantity is encoded by area. If this were left at 1, the graphic would be underestimated.")
    print("- Chart D understates the change: it is still a distortion because the chart hides the true rise and makes the change look smaller than it really is.")
    print("- Chart F (dual-axis clinical chart) cannot be audited with a standard Lie Factor because the graphic is not a single encoded quantity with a single baseline; it also mixes two series on different axes and violates the course rule against dual axes.")


if __name__ == "__main__":
    main()
