# Changelog

All notable changes to this project are documented here. Format loosely follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

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
