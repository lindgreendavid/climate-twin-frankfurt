# Research protocol

Frozen before generating or interpreting any v0.1.0 result.

## Status

This protocol is fixed before running `scripts/generate_registry.py` or looking at the
resulting registry. It describes the data source, the exact station pair, the exact time
period and resolution, the exclusion/quality-control criteria, and the statistical plan. Any
deviation from this document discovered after results exist will be recorded as an amendment
in [`research-report.md`](research-report.md), not silently applied.

## Research question

Using real Deutscher Wetterdienst (DWD) Climate Data Center (CDC) daily station records: how
much warmer is urban Frankfurt than a defensible rural/reference counterpart, with what
uncertainty, and how has that gap (the urban heat island, UHI, intensity) trended over the
available overlapping record?

## What this project is not

This is a two-station reanalysis of one city's public climate-station record. It does not
build an independent urban-canopy or land-use model, does not correct for the confounding
effects described below, and does not claim to determine the physical mechanism of Frankfurt's
UHI or generalize its magnitude to any other city. It reports what a straightforward,
disclosed statistical pipeline finds on this specific two-station daily record, with
uncertainty stated before any "warmer" or "trending" claim.

## Station pair and selection criterion

**This project uses DWD's own designated urban/rural station pair for Frankfurt, not an
independently chosen substitute.**

DWD's Urban and Regional Climatology program lists paired urban climate stations and rural
counterparts, viewable at
[dwd.de/EN/ourservices/urban_heatisland/urbanheatisland_en.html](https://www.dwd.de/EN/ourservices/urban_heatisland/urbanheatisland_en.html)
and the full pairing table at
[dwd.de/EN/climate_environment/climateresearch/climate_impact/urbanism/urban_climate_stations/urban_climate_stations_node.html](https://www.dwd.de/EN/climate_environment/climateresearch/climate_impact/urbanism/urban_climate_stations/urban_climate_stations_node.html)
(verified by fetching the page's raw HTML directly and confirming the text `Frankfurt/Main-Westend
01424 ... Frankfurt/Main 01420` appears, not just an AI-generated paraphrase of it, on
2026-08-13). That table explicitly pairs:

| Role | Station name | DWD station ID | Coordinates (current) | Elevation | Record start (daily `kl`) |
| --- | --- | --- | --- | --- | --- |
| **Urban** | Frankfurt/Main-Westend | `01424` | 50.1269° N, 8.6694° E | 120.78 m | 1985-11-01 |
| **Reference ("rural counterpart" per DWD)** | Frankfurt/Main | `01420` | 50.0259° N, 8.5213° E | 99.70 m | 1935-07-01 |

Both station IDs were independently confirmed to exist with real, currently-served data files
by directly listing (via `curl`, not an AI summary) the DWD CDC open-data directory
`https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/`,
which contains exactly `tageswerte_KL_01420_19350701_20251231_hist.zip` and
`tageswerte_KL_01424_19851101_20251231_hist.zip`, and the matching `recent/` directory, which
contains `tageswerte_KL_01420_akt.zip` and `tageswerte_KL_01424_akt.zip` current through
2026-08-12 at time of verification.

**Important honesty note on "rural":** DWD's own label for station `01420` on the urban
climate stations page is "counterpart" and DWD's general urban-heat-island page describes such
counterparts as the paired stations' "surrounding counterparts." Station `01420` is
Frankfurt Airport (Flughafen), an open, low-vegetation, semi-paved site on the city's western
edge — it is DWD's chosen reference for this pair, but it is **not** a remote rural village
station; airports have their own documented local microclimate (large paved/mown open areas,
some pavement heat retention, aircraft/ground operations) that is smaller than a dense
inner-city core's but is not zero. This project uses `01420` because it is DWD's own
purpose-designated counterpart for this exact urban station, not because it independently
verified `01420` to be climatologically pristine — this is disclosed as a limitation, not
hidden.

## Data source, format, and access

- **Provider:** Deutscher Wetterdienst (DWD) Climate Data Center (CDC) Open Data area,
  `https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/`.
  Confirmed live and unauthenticated on 2026-08-13.
- **Dataset:** `daily/kl` ("Tageswerte KL" / daily climate summary), which includes `TMK`
  (`Tagesmittel der Temperatur`, daily mean 2 m air temperature, °C) among other daily
  variables, confirmed via each station's own
  `Metadaten_Parameter_klima_tag_<id>.txt` metadata file shipped inside its data archive
  (formula disclosed there as `TMK=(TT1+TT2+(TT3*2))/4` for the older observation era, and an
  hourly arithmetic mean of at least 21 hourly values for the SYNOP-routine era since 2001).
- **Files used:** the `historical/` archive for each station
  (`tageswerte_KL_01420_19350701_20251231_hist.zip`,
  `tageswerte_KL_01424_19851101_20251231_hist.zip`), each a zip containing one
  `produkt_klima_tag_*.txt` semicolon-delimited file plus DWD's own station and instrument
  metadata files. **The `recent/` archive (`*_akt.zip`, which DWD updates daily) is
  deliberately NOT used for the frozen v0.1.0 registry** — see "Reproducibility and snapshot
  pinning" below.
- **Column format (confirmed by directly reading the downloaded files, not assumed):**
  semicolon-separated, header
  `STATIONS_ID;MESS_DATUM;QN_3;FX;FM;QN_4;RSK;RSKF;SDK;SHK_TAG;NM;VPM;PM;TMK;UPM;TXK;TNK;TGK;eor`.
  `MESS_DATUM` is `YYYYMMDD`. `TMK` is the primary variable used here. **Missing values are
  encoded as the sentinel `-999`** (confirmed directly in the files, e.g. station `01420`'s
  earliest rows carry `-999` for several columns not yet measured in 1935, and station
  `01424`'s `PM` column is `-999` throughout because that station does not measure air
  pressure). `QN_3`/`QN_4` are DWD quality-processing-level codes for two different column
  groups (not itself a validity flag — DWD's own documentation describes these as levels of
  completed quality control, e.g. 1 = only formal control, 3 = automatic control and
  correction, 9/10 = quality control finished/secondary automatic QC); this project does not
  filter on `QN_3`/`QN_4` value beyond what "missing = -999" already excludes, and discloses
  that as a choice, not an oversight.
- **License:** DWD's CDC-OpenData Terms of Use, fetched directly as a PDF from
  `https://opendata.dwd.de/climate_environment/CDC/Terms_of_use.pdf` on 2026-08-13 (status
  "Mai 2024" per the document itself), state verbatim: **"The Creative Commons BY 4.0 - Licence
  'CC BY 4.0' apply."** with a pointer to `https://www.dwd.de/copyright` for detail. This is
  quoted directly from the fetched PDF, not assumed.

## Reproducibility and snapshot pinning

DWD's `recent/` directory is updated daily and its `historical/` directory is updated roughly
annually when a station's most recent full year is finalized and appended — unlike a fixed
academic catalog (e.g. `frb-atlas`'s VizieR mirror), this source is not permanently static.
This project therefore:

1. Uses **only the `historical/` archives** (ending 2025-12-31 for both stations at time of
   access) for the frozen v0.1.0 registry, not `recent/`, so that a re-run of
   `scripts/fetch_stations.py` shortly after this release is very unlikely to silently change
   the registry.
2. Records the exact access date (2026-08-13) and source URLs in `data/provenance.json`.
3. Discloses explicitly, here and in `data/provenance.json`, that this is a **pinned snapshot**
   of DWD's `historical/` archives as they existed on the access date above — not a
   perpetually-fresh live feed. A future maintainer wanting current 2026+ data would need to
   deliberately extend this project to also fetch `recent/`, which is out of scope for v0.1.0.

## Time period and temporal resolution

- **Variable:** `TMK`, daily mean 2 m air temperature (°C), for both stations.
- **Period:** the full overlap of both stations' `historical/` records with non-missing `TMK`:
  **1985-11-01 through 2025-12-31** (bounded by station `01424`'s record start; station `01420`
  has data back to 1935-07-01 but is not used before `01424` exists, since a UHI gap requires
  both stations on the same day).
- **Unit of analysis:** one paired observation per calendar day where **both** stations report
  a non-missing `TMK` value for that date. Days where either station is missing `TMK` are
  excluded from that day's pairing (see Exclusions).

## Exclusions and quality-control criteria (declared before results)

1. **Missing-value exclusion:** any date where `TMK == -999` (DWD's missing-value sentinel) at
   either station is dropped from the paired analysis for that date. No imputation is
   performed.
2. **Duplicate-date guard:** if a station's raw file contains more than one row for the same
   `MESS_DATUM` (not expected, but checked defensively), only the first occurrence is kept and
   this is logged, not silently overwritten.
3. **Range sanity check:** `TMK` values outside [-30, 40] °C are treated as a data-integrity
   failure and abort the fetch/parse step rather than being silently included or silently
   dropped — this range comfortably contains Frankfurt's entire plausible daily-mean
   temperature history and is meant to catch a parsing error, not to perform climatological
   outlier removal.
4. **No further exclusions.** No smoothing, no outlier trimming beyond the range check above,
   and no seasonal adjustment is applied before computing the daily paired gap. Every
   exclusion is applied identically to both stations' contribution to a given day; a day is
   excluded as a pair, never asymmetrically.
5. **Annual trend inclusion threshold:** a calendar year is included in the year-level trend
   analysis only if it has **at least 300 valid paired days** (of ~365), disclosed here before
   results, so that a sparse partial year cannot distort the trend estimate. This drops no
   complete `historical/`-era year in practice for either station based on the sanity checks
   already performed in `scripts/fetch_stations.py`, but the threshold and the resulting
   included/excluded year list are reported explicitly in the registry regardless.

## Statistical methods

- **Primary quantity — the daily urban-heat-island gap:** `gap = TMK(Westend, 01424) −
  TMK(Frankfurt/Main, 01420)` for every valid paired day (defined above). Reported as the mean
  gap over the full period, with a **95% confidence interval from a block bootstrap** (not a
  naive i.i.d. bootstrap), because consecutive days' temperatures are strongly autocorrelated
  and an i.i.d. resample would understate the true uncertainty. Block bootstrap uses
  fixed-length contiguous blocks of 30 days, resampled with replacement to reconstruct a
  series of the same total length, 10,000 resamples, `numpy.random.default_rng(seed=20260813)`
  for exact reproducibility. The mean gap and its bootstrap 95% CI are computed once for the
  full period and once per season (meteorological DJF/MAM/JJA/SON) as a disclosed robustness
  breakdown, since UHI intensity is known in the general literature to vary seasonally.
- **Trend over time:** ordinary least-squares linear regression of each included calendar
  year's mean daily gap against the year number (`scipy.stats.linregress`), reporting the
  slope (°C per year), its 95% confidence interval (from the regression's own standard error
  via a t-distribution, disclosed as the classical OLS CI, not a bootstrap), the p-value for
  the slope being different from zero, and R². This is a **preregistered, disclosed decision to
  use a simple linear trend on annual means**, not a search over more flexible models; if the
  data show clear non-linearity, that is reported as a qualitative observation in the report,
  not fit with an ad hoc curve after the fact.
- **Effect size framing:** the report leads with the confidence interval on the mean gap and
  on the trend slope before stating any "Frankfurt is warmer" or "the gap is widening"
  conclusion, consistent with the "uncertainty first" reading order used across this
  maintainer's other research projects (`frb-atlas`, `foldings-edge`).
- **Significance threshold:** α = 0.05, two-sided, disclosed as a conventional threshold, not
  a uniquely correct one.
- **No multiple-comparison correction** is applied between the full-period gap test and the
  four-season breakdown, because the seasonal breakdown is reported as a disclosed
  descriptive robustness check alongside the primary full-period result, not as four
  independent hypothesis tests used to cherry-pick a favorable season.

## Analysis plan

- Report the number of valid paired days, the number of excluded days (and why), and the
  included/excluded year list for the trend regression, before any gap or trend number.
- Report the full-period mean gap and its bootstrap 95% CI first, then the seasonal breakdown,
  then the year-level trend slope and its CI and p-value — always uncertainty before
  conclusion.
- If the trend slope's 95% CI includes zero, that is reported plainly as "no statistically
  detectable trend at this record length," not reworded to imply a trend exists.
  If the full-period gap's CI excludes zero, this project will say Frankfurt/Main-Westend is
  measurably warmer than the airport reference station over this record, without extending
  that into a general claim about "the" Frankfurt urban heat island's true magnitude beyond
  this specific station pair.
- State explicitly that a two-station comparison cannot separate urban-canopy effects from
  every other difference between the two sites (elevation difference of ~21 m, distance
  ~14.9 km, differing instrument history — station `01420` relocated slightly in 2014,
  `01424` relocated slightly in 2008, both documented in each station's own
  `Metadaten_Geographie_*.txt` file and disclosed in `data/provenance.json`).

## Ethics and responsible framing

This is an analysis of public, non-personal, government-collected meteorological
observations; there are no human subjects and no personal data. The responsible-communication
obligation here is scientific honesty about what a two-station comparison can and cannot show:
not overstating a single-pair UHI estimate as "the" Frankfurt UHI, not treating DWD's own
"counterpart" label for an airport station as evidence of a pristine rural reference, and
reporting a null or weak trend result plainly if that is what the ~40-year overlap shows.
