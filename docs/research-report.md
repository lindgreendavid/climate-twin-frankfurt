# Research report

What the frozen registry
([`reports/v0.1-climate-twin-frankfurt-registry.json`](../reports/v0.1-climate-twin-frankfurt-registry.json))
actually shows, compared against the preregistered plan in
[`research-protocol.md`](research-protocol.md), reported without suppressing a weak or null
result.

## Sample

**14,579 valid paired days** with a non-missing `TMK` at both Frankfurt/Main-Westend (`01424`,
urban) and Frankfurt/Main (`01420`, DWD's own designated reference counterpart), spanning
**1985-11-01 through 2025-12-31**. Of the 41 calendar years touched by this range, **40 years
met the preregistered ≥300-valid-paired-days threshold** and are used in the trend regression;
only the partial year **1985 (61 days, November–December only) was excluded**, exactly as
specified in the protocol before any result was generated. No other year fell below the
threshold — even years with a mid-year station relocation (`01424` in 2008: 335 valid days;
`01420` in 2014, reflected in a slightly reduced 2000 count of 305 days from an unrelated data
gap) still cleared 300 days.

## Uncertainty first: the mean gap

**Read this before any "warmer" conclusion.** The full-period mean daily gap (urban minus
reference) and its 95% confidence interval, from a 30-day block bootstrap (10,000 resamples,
seed 20260813, chosen specifically because daily temperatures are strongly autocorrelated and
a naive i.i.d. bootstrap would understate this uncertainty):

| Period | n days | Mean gap (°C) | 95% CI |
| --- | --- | --- | --- |
| **Full period (1985-11-01 to 2025-12-31)** | 14,579 | **+0.455** | **[+0.432, +0.478]** |
| DJF (winter) | 3,641 | +0.489 | [+0.453, +0.522] |
| MAM (spring) | 3,619 | +0.541 | [+0.497, +0.589] |
| JJA (summer) | 3,649 | +0.415 | [+0.361, +0.471] |
| SON (autumn) | 3,670 | +0.374 | [+0.341, +0.406] |

The full-period confidence interval **excludes zero**: Frankfurt/Main-Westend is measurably
warmer, on average, than the Frankfurt/Main reference station over this record. Every season's
CI also excludes zero, so this is not driven by one part of the year. But the magnitude is
modest — under half a degree Celsius on average — smaller than the several-degrees urban heat
island figures sometimes quoted for daily minimum (overnight) temperature or for extreme heat
events specifically. This project measured the **daily mean**, not the daily minimum or a
heatwave-conditional maximum, per the preregistered protocol; a different variable would very
plausibly show a larger gap, and this project does not claim otherwise.

Spring (MAM) shows the largest mean gap (+0.541 °C) and autumn (SON) the smallest
(+0.374 °C). Their marginal confidence intervals do not overlap, which is compatible with a
seasonal contrast, but it is not a formal test of the spring-minus-autumn difference. Because no
season-to-season contrast was preregistered, this remains descriptive and supports no standalone
seasonal hypothesis claim.

## Uncertainty first: the trend

**Read this before any "the gap is widening/narrowing" conclusion.** OLS linear regression of
each of the 40 included years' mean daily gap against year:

| Statistic | Value |
| --- | --- |
| Slope | **-0.0031 °C/year** |
| 95% CI on slope | **[-0.0071, +0.0008] °C/year** |
| p-value | 0.118 |
| R² | 0.063 |
| n years | 40 |

**The slope's 95% CI includes zero, and the p-value (0.118) does not clear this project's
preregistered α = 0.05 threshold.** Per the preregistered analysis plan, this is reported
plainly as **no statistically detectable trend in the urban-reference gap over this ~40-year
overlapping record** — not reworded to imply a trend exists. The point estimate is even
slightly negative (a marginal narrowing), but with R² = 0.063 the year-to-year variation in
annual mean gap is mostly not explained by a linear year trend at all; annual means swing
from roughly +0.28 °C (2025) to +0.72 °C (2005) with no clear monotonic direction across the
record (see `annual_means` in the registry for every year's value).

The classical OLS interval assumes an error structure that is too simple for these annual data:
the fitted residuals have lag-1 correlation **0.657**. A post-release Newey–West sensitivity
(three lags; same slope) gives a wider 95% interval **[-0.00787, +0.00158] °C/year** and
two-sided p = **0.186**. The conclusion is unchanged—no linear trend is statistically detected—
but the serial-correlation-robust interval is the preferred uncertainty sensitivity. It is
machine-readable in
[`reports/post-release-academic-sensitivity.json`](../reports/post-release-academic-sensitivity.json).
The covariance estimator follows Newey and West (1987,
[doi:10.2307/1913610](https://doi.org/10.2307/1913610)); the need to account for temporal
autocorrelation when assessing climate trends is also demonstrated by Santer et al. (2000,
[doi:10.1029/1999JD901105](https://doi.org/10.1029/1999JD901105)).

## What this project does and does not conclude

- **Frankfurt/Main-Westend is measurably warmer than the Frankfurt/Main reference station**,
  on average, over the analyzed 1985–2025 daily-mean-temperature record — the full-period gap's
  95% CI clears zero. This project states this plainly, because the data support it.
- **This project does NOT conclude that Frankfurt's urban heat island is intensifying or
  weakening over time.** The preregistered trend test found no statistically significant slope;
  the honest report of that is "not detected at this record length and this test," not "no
  trend exists" (absence of evidence is not evidence of absence) and not a reworded positive
  claim either.
- **This project does NOT claim the measured ~0.45 °C gap is "the" Frankfurt urban heat
  island's magnitude.** It is specifically the daily-mean-temperature difference between these
  two DWD stations, one of which (the reference) is an airport site DWD itself only labels a
  "counterpart," not a verified pristine rural baseline (see the protocol's honesty note). A
  different reference station, a different variable (daily minimum, heatwave-conditional
  maximum), or a different city district would very plausibly show a different number.

## Limitations

- **Two stations, one pairing.** This is not a city-wide urban-canopy model; it is exactly the
  DWD-designated pair `01424`/`01420`. A different urban station within Frankfurt, or a
  different, more clearly rural reference station further from the city, would likely give a
  different gap magnitude.
- **The "reference" station is an airport, not a rural village.** DWD's own label for `01420`
  on its urban climate stations page is "counterpart," and this project uses it because DWD
  itself designates it as Frankfurt's paired reference — but an airport's open, semi-paved,
  low-vegetation surroundings are not a pristine rural baseline, and this project did not
  independently verify otherwise. The measured gap should be read as "Westend minus this
  specific reference station," not as an isolated pure urban-canopy signal.
- **Elevation and distance differ between the two stations** (station `01424` sits 21.08 m
  higher and 15.42 km from station `01420`, by great-circle/haversine distance on the
  coordinates in `data/provenance.json` — see the interactive map's calculation in `site/`),
  which the daily-mean-gap statistic does not separate from any land-cover effect.
- **Both stations relocated slightly within the record** (`01420` in 2014-10-22, `01424` in
  2008-07-01, both documented in `data/provenance.json`); this project did not attempt to
  homogenize across those relocations, and a station move could in principle introduce a small
  step-change unrelated to genuine climate change, though neither relocation coincides with an
  unusual jump in the annual-mean-gap series in the frozen registry.
- **Daily mean only.** This project did not analyze daily minimum or maximum temperature, which
  are the variables more commonly associated with larger reported urban heat island
  differences (especially overnight minima); a follow-up using `TNK`/`TXK` (already present in
  the same DWD files but not used here) could show a materially different, likely larger, gap.
- **No independent land-use, wind, or cloud-cover covariate model.** The gap is reported as a
  raw paired daily-mean difference; no attempt was made to control for synoptic weather
  conditions (e.g. clear/calm nights known in the general UHI literature to produce the
  largest urban-rural differences).
- **A single linear trend model.** The preregistered method was a simple OLS trend on annual
  means; if the true year-to-year pattern is non-linear (e.g. driven by specific hot/cold
  years or multi-year cycles), a linear model would not detect it, and this project did not
  fit any more flexible model after seeing the result.
- **Serial dependence in annual residuals.** The preregistered classical OLS confidence interval
  does not model this dependence. The post-release HAC sensitivity widens the interval and leaves
  the null conclusion unchanged; neither interval establishes that the true slope is exactly zero.

## Amendment log

No amendments to the analysis. The statistical findings in this report match the preregistered
plan in `research-protocol.md` exactly; no post-hoc changes were made to the method after
generating the registry.

- 2026-08-13: corrected an imprecise incidental figure. The inter-station distance was described
  as "roughly 14.9 km" with no shown derivation; a later interactive-map feature computed the
  precise haversine great-circle distance from the same real coordinates in
  `data/provenance.json` as 15.42 km (formula and working shown in `site/app/geo.ts` and the
  map's UI). This correction affects only a descriptive aside about station geometry, not any
  preregistered hypothesis, statistical test, or reported finding. `research-protocol.md` is left
  as originally written, per this project's own discipline of not editing a frozen protocol
  document after the fact; this log entry is the disclosed correction.
