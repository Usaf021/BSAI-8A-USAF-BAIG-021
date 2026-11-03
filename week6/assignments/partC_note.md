# Task C — note on the board figure

**Message, one sentence:** Service is worst in Lashkar (D12), Kotla (D11) and Mehrabad (D13), at 50–51 interruptions per 1,000 households against a national 43.7; the districts with the most interruptions filed (Qilabad D17, Mehrabad D13, Zhobara D24) are simply the biggest.

**Reader:** the National Grid Authority board, who are splitting a reliability budget across 24 districts and will read one figure.

**Parameters, each with a reason**
- **Denominator: billed households** (district_grid.csv, 24 districts, D21 repaired from 182 to 182,000). Interruptions happen to households that are connected; population would blur districts with different household sizes (5.70–7.36 persons per household). Legend and axis say "per 1,000 households".
- **Class scheme: Jenks natural breaks, 5 classes** (GVF 0.959), edges printed in the legend (30.4 / 33.5 / 36.2 / 42.7 / 45.8 / 50.9). Chosen because the rates are tightly grouped (30–51); quantile would stretch five classes over a narrow range.
- **Projection: Lambert cylindrical equal-area**, one reference latitude for every layer, because colour over an area makes area the encoding channel.
- **Sorted bars start at zero** and carry the counts in brackets, so the board sees the size of each district and its service level side by side. Rate range 30.4 to 50.9: the gap between best and worst is real but modest (about 1.7x), and I say so in the title.
- No district was suppressed or merged. The fewest interruptions in any district is 3,234, so sampling noise is small (a Poisson funnel puts 22 of 24 outside its limits, which says the differences are not small-number artefacts; it does not say why they differ).
- Not in the figure: mean interruption length (minutes per interruption) exists for 22 of 24 districts only (D09 and D20 are the not-available code, set to missing), so I did not use duration as the measure.

**Counterfactual: the raw-count version.** A count map would be a population map: r(interruptions, households) = +0.991, whereas r(rate, households) = +0.175. It would colour D17, D13 and D24 darkest (63,237, 55,879 and 43,710 interruptions) and send the money there. Only one district, D13 (50.3 per 1,000, 15% above national), is on both lists, and it is there for both reasons at once: it is large and it is worse than average. D17 (40.4) and D24 (42.5) are *below* the national rate. The count version would take money **away** from D12 Lashkar (50.9) and D11 Kotla (50.8, though Kotla's 31,283 interruptions rank fifth by count), and from small high-rate districts such as D18 Rohtas West (48.8), D03 Chakwa (48.4) and D21 Ushkan (47.9), whose counts are only 8,000–11,000. The five most populous districts hold 59.9% of the people on 12.6% of the land, so a count-coloured choropleth would give most of the budget argument to a twelfth of the ink.

**Caveat:** the spread in rates is modest and districts differ in more than reliability (sizes, lines, weather); the figure ranks service per household, it does not diagnose causes.
