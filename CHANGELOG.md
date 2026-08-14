# Changelog

All notable changes to this project are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

- Add a reproducible Newey–West sensitivity for serially correlated annual trend residuals and
  clarify that non-overlapping marginal seasonal intervals are not a formal seasonal contrast.

## [1.0.0] - 2026-08-13

### Added

- Stable product release around the unchanged frozen v0.1 paired-station study.
- Release audit plus contribution, conduct and security documentation.

### Fixed

- Hardened the transitive `image-size` parsers against malformed ICNS and ISO-BMFF input,
  added executable security regression probes, and kept the production audit strict for every
  other high-severity advisory.
- Made frozen-registry verification portable across operating systems by comparing floating-point
  values with a narrow numerical tolerance while retaining exact checks for all other data.
- Aligned the Cloudflare compatibility date with the version supported by the pinned runtime.

### Added

- `site/app/station-map.tsx`, `site/app/geo.ts`: an interactive station map on the
  presentation site showing both real DWD station locations (Frankfurt/Main-Westend `01424`
  and Frankfurt/Main `01420`, coordinates from `data/provenance.json`) as a north-up
  schematic drawn to true relative scale from those coordinates — not basemap tile imagery
  and not a live mapping API — with the real straight-line (haversine) distance (15.42 km)
  and elevation difference (21.08 m) computed and shown with their formula. Each station
  marker is a focusable/hoverable/clickable button revealing its name, role, elevation, and
  DWD station ID; a plain accessible table beneath the map carries the same information as
  text, so the map is never the only way to get it. No mapping library was added as a
  dependency.

## [0.1.0] - 2026-08-13

### Added

- Preregistered research protocol (`docs/research-protocol.md`): the exact DWD-designated
  station pair (Frankfurt/Main-Westend `01424` vs. Frankfurt/Main `01420`), the exact time
  period (1985-11-01 to 2025-12-31, bounded by data overlap), quality-control criteria, and
  statistical plan (block-bootstrap CI on the mean gap; OLS trend on annual means), fixed
  before any analysis was run.
- `scripts/fetch_stations.py`: downloads and verifies both real DWD station archives from
  `opendata.dwd.de`, with sanity checks (station ID match, date parsing, value-range check)
  that abort loudly on failure. The raw archives are not committed to git.
- `data/provenance.json`: full data provenance, station metadata, and DWD's CC BY 4.0 license
  text, quoted directly from DWD's own Terms of Use PDF.
- `src/climate_twin_frankfurt`: DWD daily-KL file parsing (`stations.py`), daily urban/reference
  pairing (`pairing.py`), the block-bootstrap and OLS trend statistics (`stats.py`), the result
  registry builder (`registry.py`), and a small CLI (`cli.py`).
- `reports/v0.1-climate-twin-frankfurt-registry.json`: the frozen, reproducible v0.1.0 result
  registry (14,579 valid paired days), generated from the real, downloaded DWD station data.
- `docs/research-report.md`: the measured urban-reference gap (+0.455 °C, 95% CI
  [0.432, 0.478]) and the year-level trend (not statistically significant, p=0.118), reported
  plainly, plus full limitations.
- `site/`: an accessible Next.js (vinext) interactive site with an uncertainty-first reading
  order, a full accessible daily data table, seasonal breakdown, an annual trend chart, and a
  provenance/citations section, built for Cloudflare Workers deployment as
  `climate-twin-frankfurt-interactive`. New "ember/sand" urban-heat color palette, WCAG AA
  contrast-verified.
- Full repository hygiene: `pyproject.toml` (ruff, mypy strict, pytest with a 95% coverage
  gate), `CITATION.cff`, `ACCESSIBILITY.md`, and CI workflows (`ci.yml`, `codeql.yml`).
