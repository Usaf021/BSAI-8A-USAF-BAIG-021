# Week 7 — the dashboard

Python 3.9+; `pip install -r requirements.txt`. Run from this folder, in this order (paths are relative; raw data is read from `../assignments/data/`, never modified):

1. `python3 partA_process.py`    — audits the 4 CSVs + GeoJSON, writes `clean/`, `partA_audit.txt`, `partA_decisions.md`
2. `python3 partB_charts.py`     — writes `partB_1.png` … `partB_4.png`
3. `python3 partC_interactive.py` — writes `partC_default.png` (+ `partC_brushed.png`); add `--show` for the live brush
4. `python3 partD_screen.py`     — writes `partD_screen.png` and appends the channel plan + `cvd_report` to `partA_audit.txt`
5. Read `partC_contract.md` and `partE_note.md`.
`_common.py` holds the paths, the mode palette and the shared on-time ratio; the course toolkits (`vizlib`, `tslib`, `geolib`, `dashlib`) are imported from `../assignments/`.
