# Week 6 integration checkpoint — how to run

1. `pip install -r requirements.txt` (Python 3.9+; vizlib/tslib/geolib are the unchanged course toolkits in this folder).
2. `python3 partA_process.py` reads `data/` only, prints the audit, writes `clean/`, `partA_audit.txt`, `partA_decisions.md`.
3. `python3 partB_charts.py` reads `clean/`, writes `partB_1.png`, `partB_2.png`, `partB_3.png` (trend, composition, relationship).
4. `python3 partC_figure.py` reads `clean/` and `data/regions.geojson`, writes `partC_figure.png` (300 dpi, with source note) and prints the anchors.
5. `partC_note.md` is the half-page note for that figure.
6. Raw files in `data/` are never modified; no cleaned CSV was edited by hand; no absolute paths are used.
7. All data is synthetic, generated for CDB601220 Week 6 (a fictional federation).
8. Task D (bonus) was not attempted.
9. Output of steps 3 and 4 is saved in `partB_output.txt` and `partC_output.txt`.
10. Run order matters: step 2 before steps 3–4.
