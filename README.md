# Climate Twin Frankfurt

<p><a href="https://github.com/lindgreendavid/lindgreendavid/tree/main/brand"><img src="https://raw.githubusercontent.com/lindgreendavid/lindgreendavid/main/brand/lab-notes-mark.svg" width="52" align="right" alt="Lab Notes research-cycle mark"></a></p>

**Part of the [Lab Notes Research Portfolio](https://blog-interactive.lindgreendavid.workers.dev/)** · Climate research · Question → evidence → finding → boundary

A reproducible reanalysis of real Deutscher Wetterdienst (DWD) daily station records:
how much warmer is urban Frankfurt than DWD's own designated rural/reference counterpart,
with what uncertainty, and has that gap trended over the last ~40 years?

**[Open the live interactive laboratory](https://climate-twin-frankfurt-interactive.lindgreendavid.workers.dev)** · **[Read the plain-language write-up](https://blog-interactive.lindgreendavid.workers.dev/posts/climate-twin-frankfurt-heat-island)**

## What this contributes

- A reanalysis of DWD's own purpose-designated Frankfurt urban/rural station pair
  (Frankfurt/Main-Westend, station `01424`, vs. Frankfurt/Main, station `01420`), not an
  independently improvised city comparison — see
  [`docs/research-protocol.md`](docs/research-protocol.md) for how that pair was verified.
- A preregistered protocol, frozen **before** any result was generated: exact stations, exact
  time period (1985-11-01 to 2025-12-31, bounded by both stations' overlapping daily record),
  exact quality-control rule (drop any day where either station's `TMK` is DWD's `-999`
  missing-value sentinel), and exact statistics (a block bootstrap 95% CI on the mean daily
  gap, and an OLS trend on annual mean gaps with a classical CI).
- A frozen, reproducible result registry (`reports/v0.1-climate-twin-frankfurt-registry.json`)
  built deterministically from a **pinned snapshot** of DWD's `historical/` archives, checked
  byte-for-byte in CI against a fresh re-fetch and re-generation.
- An accessible, uncertainty-first interactive site (`site/`) that reports the gap's
  confidence interval before any "warmer" framing, and reports the trend's confidence interval
  before any "trending" framing.

## What this does NOT claim

- It does not claim to measure "the" Frankfurt urban heat island in general — it measures the
  specific daily-mean-temperature difference between two specific DWD stations, one of which
  (the "reference") is an airport site, not a remote rural village. DWD itself labels `01420`
  the "counterpart" for `01424`; this project did not independently verify that station to be
  climatologically pristine, and says so plainly (see the protocol's "Important honesty note
  on 'rural'").
- It does not separate the urban-canopy effect from every other difference between the two
  sites (elevation, distance, instrument history) — a two-station comparison cannot do that.
- It does not build an independent land-use or urban-canopy model, and does not generalize its
  measured gap or trend to any other city or time period.
- A non-significant trend result is reported as "no statistically detectable trend at this
  record length," never reworded to imply a trend exists.

## Findings (v0.1.0)

See [`docs/research-report.md`](docs/research-report.md) for the full write-up, including
every number the preregistered protocol committed to reporting, the seasonal breakdown, and
the disclosed limitations. In short: over 14,579 valid paired days (1985-11-01 to
2025-12-31), Frankfurt/Main-Westend runs measurably warmer than the Frankfurt/Main reference
station on average, with a 95% confidence interval that excludes zero but is modest in
magnitude; the year-level linear trend in that gap over the ~40-year record is **not**
statistically significant at this project's preregistered threshold.

## Data source and license

Deutscher Wetterdienst (DWD) Climate Data Center (CDC) Open Data area,
`https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/`,
licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**, confirmed
directly from DWD's own Terms of Use PDF (`opendata.dwd.de/.../CDC/Terms_of_use.pdf`). Full
provenance, including exact source URLs, station coordinates, and access date, is in
[`data/provenance.json`](data/provenance.json).

## Repository layout

```
docs/research-protocol.md   preregistered protocol (frozen before results)
docs/research-report.md     what the frozen registry actually shows
data/provenance.json        data source, station metadata, license, access date
scripts/fetch_stations.py   downloads + verifies both DWD station archives
scripts/generate_registry.py  builds reports/v0.1-climate-twin-frankfurt-registry.json
src/climate_twin_frankfurt/ parsing, pairing, statistics, and registry-building code
reports/                    the frozen, committed v0.1.0 result registry
site/                       accessible Next.js (vinext/Cloudflare Workers) interactive site,
                            including an interactive station map (real coordinates, computed
                            distance/elevation gap, no basemap imagery, no mapping library)
```

## Reproducing the analysis

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# fetch and verify the two real DWD station archives (writes to data/external/, gitignored)
python scripts/fetch_stations.py --output-dir data/external

# regenerate the registry -- should be byte-identical to the committed copy
python scripts/generate_registry.py --output /tmp/registry.json
cmp reports/v0.1-climate-twin-frankfurt-registry.json /tmp/registry.json

# quality gates
ruff check .
ruff format --check .
mypy src
pytest
```

Note that `scripts/fetch_stations.py` downloads from DWD's `historical/` archives, which DWD
updates roughly annually (not the daily-updating `recent/` archives) — see
`docs/research-protocol.md`, "Reproducibility and snapshot pinning," for why this project
pins to that snapshot rather than always fetching the latest available day.

## Site

```bash
cd site
pnpm install
pnpm run dev     # local development
pnpm run build   # production build
pnpm run lint
pnpm run test
```

The human maintainer deploys the reviewed build (`wrangler deploy` / `vinext-cloudflare deploy`
are intentionally not run by any automation in this repository).

## License

Code is MIT-licensed (see [`LICENSE`](LICENSE)). The underlying DWD climate data is
CC BY 4.0-licensed by Deutscher Wetterdienst, as documented in
[`data/provenance.json`](data/provenance.json).
