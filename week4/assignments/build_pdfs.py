"""Builds partA_diagnosis.pdf and partE_justification.pdf from the numbers printed by the part scripts."""
import os
from mkpdf import build

H = os.path.dirname(os.path.abspath(__file__))
P = lambda f: os.path.join(H, f)

cases = [
 (1, "Orders peak in Q1 and collapse every year",
  "A strong annual cycle: orders climb Jan–Apr, fall in spring, repeat.",
  "<b>Decoy:</b> 'real seasonality'. Ruled out: the true series (Jan 2024 4,200 → Dec 2025 6,405, +52.5%) is monotone; its worst month-on-month change is +59, never negative.",
  "<b>Mechanism:</b> <i>month</i> is text written YYYY-M with no padding, so a text sort puts '2024-10','2024-11','2024-12' after '2024-1' and before '2024-2'. 22 of 24 rows land in the wrong place; the two 'collapses' (−958, −978) are the jumps from Dec back to Feb.",
  "<b>Redesign:</b> parse with format='%Y-%m', sort as datetime — one unbroken rise."),
 (2, "Sales grew steadily, 22%, across the quarter",
  "A steady climb 207 → 253 (+22%) with a rising trend line.",
  "<b>Decoy:</b> 'the dates are just labels'. Ruled out: 69 rows span 90 calendar days — 21 days never trade (3 Feb – 23 Feb).",
  "<b>Mechanism:</b> plotting by row number deletes the 21-day closure. Before it sales fall 207 → 198 (−0.16k/day); after it they run 262 → 253 (+0.23k/day): flat each side. The whole rise is a single +64k step across the closure; a trend line fitted across it (+1.23/row) measures the step, not growth.",
  "<b>Redesign:</b> calendar axis, closure left as a gap, one trend per trading spell."),
 (3, "Peak load jumped 43% overnight on 1 July",
  "A capacity step on 1 July (daily June mean 8,782 → July 12,543, +42.8%).",
  "<b>Decoy:</b> 'July is just busier'. Ruled out: daily mean users go 535.9 → 522.6 (−2.5%) and daily max 779 → 808 (+3.7%).",
  "<b>Mechanism:</b> concurrent_users is a <i>level</i> (users connected at an instant); summing hourly levels counts coverage, not load. June has only 493 of 720 hours recorded (16.4 h/day), July 744 of 744 (24 h/day); 24/16.4 ≈ 1.46 reproduces the 'jump'. Bytes served (a flow) also 'jump' +42.7% for the same reason, but per recorded hour fall −2.3%.",
  "<b>Redesign:</b> a level takes mean or max per day — no step on 1 July."),
 (4, "The new checkout flow started working on 7 September",
  "A trailing 31-day mean bottoms on 2025-09-07, so that is when the fix kicked in.",
  "<b>Decoy:</b> 'the fix has a delayed effect'. Ruled out: the raw data itself turn earlier.",
  "<b>Mechanism:</b> a trailing mean at date t averages days t−30…t, so it cannot register a turn until the window has filled: it is half a window late by arithmetic. Centred-31 minimum: 2025-08-23; a broken-stick fit on the raw data puts the break at 2025-08-28; lag_at_turn gives 15 days = the half-window (15).",
  "<b>Redesign:</b> show the centred window and the fitted break; caption the 31-day window."),
 (5, "Revenue has fallen for six straight months",
  "A sustained collapse, 158.8 → 92.2 (−41.9%).",
  "<b>Decoy:</b> truncated axis / tiny sample. Ruled out: the recipe starts y at zero and every point is a full month of the 36.",
  "<b>Mechanism:</b> the window starts at the seasonal peak (May) and ends at the trough (Nov). May → Nov is −42.4%, −42.8%, −41.9% in 2023, 2024, 2025: the same fall every year. Year-on-year, all 24 months of 2024–25 are positive (mean +9.2%, range +4.9% to +13.3%).",
  "<b>Redesign:</b> cycle plot, each year on a Jan–Dec axis."),
 (6, "Orders collapsed in October",
  "October fell to 4,041 from 10,805 — 37% of September.",
  "<b>Decoy:</b> 'a real demand drop'. Ruled out: the daily mean is up.",
  "<b>Mechanism:</b> the extract stops 2025-10-11, so October holds 11 of 31 days. Orders per recorded day: 360.2 (Sep) → 367.4 (Oct, +2.0%), the highest of the year.",
  "<b>Redesign:</b> orders per recorded day, partial month hatched and labelled."),
 (7, "Product D has been erratic since mid-2024",
  "D's wobbling top edge says D is unstable.",
  "<b>Decoy:</b> 'D really is volatile'. Ruled out: D's own level SD is 3.6 and month-on-month SD 2.0 — the calmest of the four.",
  "<b>Mechanism:</b> a stacked area draws each layer on a moving baseline. D sits on A+B+C; B (level SD 35.6, month-on-month 45.8) is the volatile one and its swings are passed up through C into D's top edge (SD 47.3). The envelope is 548–709 because of B.",
  "<b>Redesign:</b> unstack — four lines on one zero-based axis."),
 (8, "Paid search drives 43% of our customers",
  "Search is the dominant channel — 42.6% of the pie.",
  "<b>Decoy:</b> 'rounding / unusual sample'. Ruled out: shares are exact per column.",
  "<b>Mechanism:</b> the four touch flags are not exclusive: 42.6 + 32.3 + 27.5 + 28.6 = 131.0%. 1,105 of 4,000 customers (27.6%) were touched by 2+ channels (980 by two, 116 by three, 9 by four). Search is 'touched' by 42.6% but touched <i>only</i> by search for 25.9%. 'Drives' is a claim about causation the data never makes.",
  "<b>Redesign:</b> one bar per channel against all customers, with the 'only this channel' overlap shown."),
 (9, "Premium is now 38% of revenue — a record",
  "Premium is booming: 24.0% → 38.0%.",
  "<b>Decoy:</b> 'premium grew'. Ruled out: premium revenue is 240 → 228 (−5.0%).",
  "<b>Mechanism:</b> the denominator fell. Total revenue 1,000 → 600 (−40.0%); non-premium revenue 760 → 372 (−51.1%). A share can rise while its numerator stalls. This is incomplete rather than wrong: the share is correct, it hides the story.",
  "<b>Redesign:</b> the same share, with the two absolute series beside it (stacked, zero baseline) — not a dual axis."),
]

blocks = [("h1", "Week 4 · Part A — diagnoses of the nine charts"),
          ("p", "Written for: the marker of CDB601220 Week 4. Each case: the conclusion the chart invites, the decoy objection and why it fails, the mechanism with its number, and the redesign (figure: left = rebuilt as published, right = redesign). All numbers are printed by partA_charts.py (partA_output.txt). Data is synthetic course data.")]
for n, claim, concl, decoy, mech, redo in cases:
    blocks += [("h2", f"{n} · “{claim}”"),
               ("p", f"<b>Conclusion invited:</b> {concl}"), ("p", decoy), ("p", mech), ("p", redo),
               ("img", P(f"partA_case{n:02d}.png"), 0.98), ("sp", 4)]
    if n % 2 == 0 and n < 9:
        blocks.append(("pb",))
build(P("partA_diagnosis.pdf"), blocks, base=9)

# ---------------------------------------------------------------- Part E (one page)
E = [("h1", "Week 4 · Part E — justification"),
 ("h2", "1 · Panels (question · why this chart · Week 2 rule)"),
 ("p", "<b>P1 daily sessions</b> — is the trend up once the weekend is removed? Line: position on a common scale, the best channel for a trend. Raw in light grey, signal in blue (one pop-out, grey for context). "
       "<b>P2 day×hour heat map</b> — when in the week does traffic live? A 7×24 grid has no ordering to exploit, so lightness; sequential Blues, dark = more. "
       "<b>P3 treemap</b> — where is the mass? Containment shows parent→child at a glance; area is the 4th-best channel, so every block prints its value and share; one hue per parent (cognitive load: four hues). "
       "<b>P4 sorted bars</b> — by how much? Length on a common zero baseline (rank 2) with values printed: the treemap answers <i>where</i>, the bars answer <i>how much</i>."),
 ("h2", "2 · Time decisions"),
 ("p", "<b>Parse:</b> two loggers — ISO (9,019 rows) and DD/MM/YYYY HH:MM (3,651). Ambiguity resolved by test: 2,151 slash rows have a first field above 12, none has a second field above 12, so it is DD/MM. Explicit formats; format='mixed' would silently misdate 1,382 rows. "
       "<b>Resolution/aggregation:</b> hourly → daily with sum(), because sessions are a flow (never last()); missing days stay NaN (13 days, gaps counted on the hourly index before resampling). "
       "<b>Window:</b> 7 days, centred, because the cycle removed is weekly (Part B.1: 31.7% of raw variation removed, 3 days lost each end); centred because this is a retrospective review — a live version would have to be trailing and ~3 days late. "
       "<b>Ethics clause:</b> the window was fixed at 7 days before plotting, for the weekly cycle. The series is shown from its first recorded day (1 Apr 2024) to its last (11 Sep 2025); no start date was selected. A 28-day version moves 16.0k → 30.4k against 16.0k → 30.0k for 7 days: the direction does not change. "
       "Part B.5 shows other start/window choices give 38 rising and 22 falling lines, so I report that range. Symmetry test: I would have fixed the same window had it weakened my message."),
 ("h2", "3 · Rows removed"),
 ("table", [["Rule", "Count", "Effect"],
            ["Exact duplicate hours (same timestamp, identical values)", "286", "12,670 → 12,384 rows"],
            ["Sentinel sessions = −1 → missing (not zero); 287 hours imputed by weekday-hour median for daily sums only", "287 (290 before dedupe)", "daily total +2.39%"],
            ["Days never recorded: left as gaps, not 0", "13 days (312 h)", "529 day slots, 516 observed"],
            ["Partial final month (Sep 2025, 11 days): shaded, kept out of monthly comparisons", "11 days", "—"],
            ["Duplicate SKU-0127 (also under Lifestyle/Wearables): dropped the wrong-parent copy", "1 row", "Wearables 10.1% → 9.3%; max share error 0.93 → 0.24 pp"],
            ["Device spellings (6) folded to mobile/desktop/tablet", "0 dropped", "—"],
            ["7 negative-net SKUs netted inside sub-categories, no negative area drawn", "7 SKUs, −1.07 m", "−0.06% of total"]],
  [8.2 * 28.35, 3.0 * 28.35, 5.6 * 28.35]),
 ("h2", "4 · Roll-ups"),
 ("p", "No <i>Other</i> bucket: four categories and eight sub-categories fit in the 4±1 chunks budget with nothing folded away (0 categories hidden, 0% of value). Depth cut at sub-category: the 345 SKUs sit below it and are not drawn (their negatives are netted in). "
       "Self-check: all eight shares are within 0.24 pp of shares_eight.csv. Synthetic course data, CDB601220 Week 4.")]
build(P("partE_justification.pdf"), E, base=8.2, margin=1.4)
print("pdfs built")
