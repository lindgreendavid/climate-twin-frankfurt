# v1.0.0 release audit

Audit date: 2026-08-13. Scientific baseline: `cdc68f343a303e0b466de30a26547caa2fe9aacf`.
The exact product-release commit is the commit resolved by annotated tag `v1.0.0`.

## Evidence checked

- Official DWD Climate Data Center historical daily climate archives and station metadata were
  retrieved again for Frankfurt/Main-Westend (`01424`) and Frankfurt/Main (`01420`).
- The frozen common period is 1985-11-01 through 2025-12-31 with 14,579 valid paired days.
- The mean paired temperature gap is +0.4545 °C with 30-day block-bootstrap 95% CI
  [+0.4317, +0.4778]. The annual-gap trend is −0.00314 °C/year with 95% CI
  [−0.00713, +0.00084], so the frozen analysis does not establish a non-zero linear trend.
- Station identities, exclusions, seasonal summaries, uncertainty and the full registry were
  regenerated from the documented archives.

## Integrity

SHA-256 of `reports/v0.1-climate-twin-frankfurt-registry.json`:
`2685556dac6c484af999ef40335b68d10eff389bf8fbaa696bfd926a2c8dabeb`.

## Boundary

v1.0.0 stabilizes the product around the unchanged v0.1 paired-station study. The gap is specific
to two stations and their histories; it is not a city-wide causal estimate or a global trend.
