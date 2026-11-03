"""Builds partA_diagnosis.pdf and partE_justification.pdf from the numbers the part scripts print."""
import os
from mkpdf import build
H = os.path.dirname(os.path.abspath(__file__)); P = lambda f: os.path.join(H, f)

cases = [
 (1, "Population and healthcare access are unrelated", "Population size tells you nothing about access: the big marks are spread across the plot.",
  "<b>Decoy:</b> 'the data really are unrelated'. The numbers are weakly related (r = +0.21, Spearman +0.22, p = 0.09), so the claim is not false, it is unreadable.",
  "<b>Mechanism (the size channel lies):</b> scatter(s=) takes <i>area</i>, and the recipe feeds it pop_m**2, so area goes as population squared: the largest mark is 346,921x the smallest for a 589x population range (Lie Factor 589). Three countries fall under 1 pt², nine have under 2 m people. Note: the brief's self-check (589x) is what linear-in-population area gives; the literal recipe gives 346,921x, and I report both. The pattern the eye does see is GDP: r(access, log GDP) = +0.83.",
  "<b>Redesign:</b> area linear in population via sizes=(12, 1500), a legend of real values, three labelled countries: the three biggest sit at access 52.8, 79.3 and 32.8."),
 (2, "The outbreak is concentrated in the three districts around the capital", "A cluster of disease around the capital: D17, D13, D09.",
  "<b>Decoy:</b> 'counts are real counts'. True, and irrelevant: the question is risk.",
  "<b>Mechanism (the denominator):</b> the map shows cases, and cases follow people: r(cases, population) = +0.986. The three are not even adjacent (lon 72.6, 66.4, 69.4). Their rates are 51.0, 64.0 and 49.9 against a pooled 52.8 per 100,000: two are below average. By rate the top three are D19, D20, D21 (76, 74, 69): overlap with the count list = 0. 24 districts join with 0 failures.",
  "<b>Redesign:</b> cases per 100,000 residents, equal-area projection, Jenks, 5 classes, breaks printed."),
 (3, "GDP per capita barely varies", "GDP is almost flat across countries.",
  "<b>Decoy:</b> 'rich and poor countries are the same'. GDP runs $283–$13,009 (46x) once one country is set aside.",
  "<b>Mechanism (scaling):</b> min–max divides by the range, and one country, Aldonia ($120,219), is 9.2x the second ($13,009). After scaling 58 of 60 sit below 0.10 and the median is 0.017. The axis is flat because the scaling is anchored to an outlier.",
  "<b>Redesign:</b> percentile-rank scaling (median 0.51, only 5 of 60 below 0.10). Aldonia is brushed, not dropped, and the axis says 'rank scaled'."),
 (4, "Healthcare access and case rate are unrelated", "No crossing pattern between the two.",
  "<b>Decoy:</b> 'then they are unrelated'. They are the strongest pair of the ten: r = −0.799.",
  "<b>Mechanism (axis order):</b> in file order the two axes are three apart (urban_pct and median_age between them), and a parallel coordinates plot only shows a relationship between <i>adjacent</i> axes. Order by the greedy |r| chain (healthcare_access → cases_per_100k → urban_pct → median_age → gdp_pc) puts them next to each other and the X-shaped waist appears.",
  "<b>Redesign:</b> same plot, order from geolib.corr_chain, fixed before looking at the picture, rank-scaled."),
 (5, "There is a clear five-level gradient in incidence", "Five tiers of risk across the federation.",
  "<b>Decoy:</b> 'the colours show real differences'. The legend edges are only 0.4–0.6 per 100,000 apart.",
  "<b>Mechanism (classification):</b> quantile classes force five equal-sized groups (5/5/4/5/5) whatever the data. The rate runs 31.07–33.40, a spread of 7.2% of the mean (CV 2.2%); 0 of 24 districts lie outside the 95% Poisson funnel. The 'gradient' is the classifier, not the disease. Not fixed by a different chart type: the decision to classify is the error.",
  "<b>Redesign:</b> the same rates against the Poisson funnel, y axis from zero: one flat surface."),
 (6, "Unit U32 is a hotspot", "U32 runs at 4.7x the national rate.",
  "<b>Decoy:</b> 'the rate is the rate'. It is 9 cases in 22,000 people.",
  "<b>Mechanism (small numbers):</b> every unit has the same true rate. One case more or fewer moves U32's rate by 4.5 per 100,000 (11% of its own value). The 10 units over 100,000 people sit at 5.5–12.0. U32 is the one unit outside the 95% funnel; with 40 units about 2 are expected to be outside by chance. It is also above the 99.8% limit (upper 28.2 vs 40.9), so I do not call it nothing: it is a unit to watch, not a published hotspot.",
  "<b>Redesign:</b> funnel plot of rate against population with Poisson limits."),
 (7, "District income and case rate are only weakly related", "r = −0.31: a weak link.",
  "<b>Decoy:</b> 'weak is weak'. Same people, different lines, a different answer.",
  "<b>Mechanism (the modifiable areal unit):</b> merge the same 24 districts into the six official zones (population-weighted income) and r becomes −0.746. 2,000 random regroupings of the 24 into six zones give r from −0.99 to +0.93 (median −0.40). The coefficient belongs to the zoning. (districts_alt.geojson has no attribute table, so I did not score it: that would need areal interpolation, an assumption I will not make.)  Not fixed by a different chart type: the decision is which units, and to report the range.",
  "<b>Redesign:</b> the distribution of r across zonings, with 24-district and six-zone values marked."),
 (8, "This is a rural outbreak — look how much of the map is dark", "Dark = rural.",
  "<b>Decoy:</b> 'rural districts really have higher rates'. r(rate, density) = +0.001; denser half 53.0 vs sparser half 52.0 per 100,000.",
  "<b>Mechanism (ink follows area, not people):</b> the five most populous districts are 12.6% of the land and 59.9% of the people. The top two classes cover 31.2% of the land but only 26.5% of residents (33.0% of cases). A choropleth gives each person in those five districts a twelfth of the ink.",
  "<b>Redesign:</b> the same rates as bars with width proportional to population."),
 (9, "Region A is the stronger of the two", "A encloses more area, so A is stronger.",
  "<b>Decoy:</b> 'the polygon area is real'. It is real for one ordering.",
  "<b>Mechanism (angle and order):</b> means are 62.3 and 62.0 (a 0.33 difference). File-order areas are 9,933 vs 9,433, but across all 60 distinct axis orders A is larger in 39 and B in 21; A's area ranges 9,366–10,443 and B's 8,564–10,555. The winner is decided by the axis order. A leads on access, funding and equipment; B on staffing, coverage and training.",
  "<b>Redesign:</b> a dot plot on one common scale: three wins each, a tie."),
]
blocks = [("h1", "Week 5 · Part A — diagnoses of the nine charts"),
          ("p", "Written for: the marker of CDB601220 Week 5. Left panel = chart as the recipe says; right = redesign. All numbers are printed by partA_charts.py (partA_output.txt). Data is synthetic course data (fictional federation).")]
for n, claim, concl, decoy, mech, redo in cases:
    blocks += [("h2", f"{n} · “{claim}”"), ("p", f"<b>Conclusion invited:</b> {concl}"), ("p", decoy), ("p", mech), ("p", redo),
               ("img", P(f"partA_case{n:02d}.png"), 0.98), ("sp", 4)]
    if n % 2 == 0 and n < 9: blocks.append(("pb",))
build(P("partA_diagnosis.pdf"), blocks, base=9)

E_ = [("h1", "Week 5 · Part E — justification"),
 ("h2", "1 · Which variable got which channel, and why"),
 ("p", "Ranked by how precisely the reader must compare them (position > length > angle > area > hue; Week 2): <b>x = GDP per capita</b> and <b>y = healthcare access</b> take position, because the question is their relationship and it needs the best channel. <b>Population</b> takes mark area, the fourth-best channel, because it is context, not the question; the size legend carries the real values and area is linear in population (sizes=(12,1500) pt², diameter ratio 11.2x, not radius). <b>Region</b> takes hue plus marker shape because it is identity; six hues is the most I would use, and the worst pair under deuteranopia is dE 7.5, so shape and direct labels are the second channel. cases_per_100k, the fifth variable, goes to the parallel-coordinates figure."),
 ("h2", "2 · The parallel coordinates decisions"),
 ("p", "<b>Scaling: percentile rank</b>, not min–max, because one country's GDP is 9.2x the second and min–max leaves 58 of 60 below 0.10; rank spreads it (Part B.3). z-score would leave Aldonia at +7.5 sd. <b>Axis order: greedy |r| chain</b> (healthcare_access → cases_per_100k → urban_pct → median_age → gdp_pc), computed with geolib.corr_chain before looking. <b>Brushing:</b> grey all, orange the Borealis region, the one with the highest mean case rate (115/100k), a rule fixed in advance. A scatter matrix shows ten separate pair plots; the parallel plot shows what a single group does on every axis at once: Borealis sits low on access and urban share and spikes on cases in one picture."),
 ("h2", "3 · The spatial decisions"),
 ("p", "<b>Denominator:</b> resident population, so the legend reads cases per 100,000 residents; the question is risk, and a count tracks people (r = +0.986). <b>Classification:</b> Jenks natural breaks, 5 classes (GVF 0.969, equal to equal-interval and better than quantile at 0.908); with no outliers the natural breaks are honest, and the breaks are printed. <b>Projection:</b> Lambert cylindrical equal-area with one reference latitude for every layer, because colour fills area, so area is the encoding channel; Mercator would inflate the federation by 1.34x (1.24x south to 1.49x north). Join: 24 matched, 0 failed. Nothing was suppressed: the smallest district has 468,000 people, so a Poisson check gives no reason to merge. Boundaries are the supplied synthetic file; no source year is stated in it."),
 ("h2", "4 · The counterfactual"),
 ("p", "A raw-count map would have darkened D17, D13 and D09 (5,588, 4,048 and 3,437 cases), the three biggest districts, and named them the outbreak; their rates are 51, 64 and 50 per 100,000 against a national 52.8, so two of them are below average. The rate map points instead at D19, D20 and D21 (76, 74, 69), together 4.2 million people who would have had no share of the attention (overlap between the two lists: zero). The five most populous districts hold 59.9% of the people on 12.6% of the land, so a count map is a population map. "
       "<b>Reader evidence:</b> the two-map activity in Part C has <i>not</i> been run on real readers yet; partC_reader_results.csv does not exist and I have made no claim about how readers behave. Ranking-wise, the two lists have no county in common (Dunmere, Pellbrook, Grimsby by count; Hollowfield, Netherby, Elmsworth by rate; r = +0.935), so the same question about which county needs police would produce different answers from the two maps.")]
build(P("partE_justification.pdf"), E_, base=8.4, margin=1.5)
print("built")
