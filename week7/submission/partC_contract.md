# Part C — interaction contract

**View:** `partC_interactive.py` (matplotlib, `dashlib.LinkedBrush`; no install beyond the course stack).
Left: one dot per route, crowding vs on-time. Right: boardings of the *selected* routes by mode.
`python3 partC_interactive.py --show` opens it; with no flag it writes `partC_default.png` and a scripted-brush `partC_brushed.png`.

**Default state.** Before anyone touches it, all 33 routes with a usable punctuality figure are selected and the view says:
*Bus routes are the slow ones (62.9–77.4% on time) while Metro and BRT sit at 81–99%, and crowding does not explain it.*
(Most readers never touch it, so this is the real message.)

**Controls.**

| Control | Changes | Does *not* change | Way back |
|---|---|---|---|
| Drag a box on the scatter | which routes are highlighted, the bar panel, the readout (n, boardings, % of the 33-route total) | the underlying data, the axes, the 3 routes excluded for a 999 code, the unit (always boardings, never journeys) | `Reset` button or key `r` restores all 33 routes; a new drag replaces the old box |
| (none) date zoom | — | — | There is deliberately no date control: the Part D screen uses fixed complete windows. A zoom into the partial September 2026 or the 14-day Metro gap (2026-02-09 → 02-22) would let a reader chart a window I never checked, so I did not build it. |

**The thing the control must not invite.** Two wrong conclusions are easy here:

1. *Adding filtered views up by district.* A route serves up to 4 districts (28 of 36 routes serve more than one; mean 2.56), so a by-district filter credits each route to every district it serves — summed it gives 2,704,739,571 boardings, **3.096×** the true 873,564,820. I built **no district filter**: the brush selects routes, each counted once, the bar panel says "each route counted once", and the readout carries the sentence "A selection is not a district: districts overlap, so do not add by district" whenever a selection is active. District figures anywhere on the screen come from the register, which is exclusive.
2. *Generalising from a tiny box.* Dragging round two routes gives a confident-looking bar chart. Below 5 routes the bars fade and the readout says "FEWER THAN 5 ROUTES — too few to say anything about a mode".
