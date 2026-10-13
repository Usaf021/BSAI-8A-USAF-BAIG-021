# Week 3 — Python Visualization Foundations: Matplotlib & Seaborn

This folder contains the Week 3 assignment brief, datasets, and the completed Python solutions for the key tasks.

## Completed work

- Part A: nine-chart reconstruction and diagnosis set generated in `assignments/partA_charts.py` and `assignments/partA_diagnosis.pdf`
- Part B: Lie Factor audit completed in `assignments/partB_lie_factor.py`
- Part C: colour-blind-safe palette audit completed in `assignments/starter/palette_check.py`
- Part D: clinical review figure completed in `assignments/starter/starter.py`
- Part E: written justification generated as `assignments/partE_justification.pdf`
- Figure export: generated as `assignments/partD_figure.png`

The scripts are designed to run from the `week3/assignments` directory and follow the course rules:

- every figure starts with `fig, ax = plt.subplots()`
- figure titles state the finding, not the subject
- cleaning rules are logged and retained in the source note
- the heatmap uses a diverging sign-aware scale with a masked upper triangle
- the figure is saved before display and exported at 300 dpi with tight bounds

## Assignment status

| Part | Status |
|---|---|
| A | completed |
| B | completed |
| C | completed |
| D | completed |
| E | completed |
| bonus | optional popout experiment scaffold ready |

## Practical notes

The core data-cleaning fixes implemented in the Part D script were:

- standardize ward labels to four cleaned categories
- parse mixed date formats into a single datetime column
- replace BMI sentinel values with missing values and report the change
- remove physiologically impossible heart-rate values and record the exclusion count
- exclude the derived `map_mmhg` column from the correlation matrix because it is algebraically tied to systolic and diastolic

## Reference files

- `assignments/TASKS.md` — full assignment brief and marking guide
- `assignments/vizlib.py` — plotting and audit toolkit
- `assignments/data/` — synthetic datasets and the data dictionary

---

This Week 3 folder now reflects the completed task set and the project-level README has been updated to show the full status across Weeks 1–3.
