"""Build the frozen v0.1.0 result registry from both stations' daily files.

This module implements exactly the preregistered plan in
`docs/research-protocol.md`: build the paired daily gap series, compute the
full-period and seasonal block-bootstrap gap statistics, and the year-level
linear trend, restricted to years meeting the disclosed minimum-coverage
threshold.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from climate_twin_frankfurt.pairing import (
    MIN_VALID_DAYS_PER_YEAR,
    PairedDay,
    build_paired_series,
    meteorological_season,
    years_with_sufficient_coverage,
)
from climate_twin_frankfurt.stations import load_station_daily_kl
from climate_twin_frankfurt.stats import (
    ALPHA,
    DEFAULT_BLOCK_LENGTH,
    DEFAULT_BOOTSTRAP_RESAMPLES,
    DEFAULT_SEED,
    block_bootstrap_mean_ci,
    linear_trend,
)

SCHEMA_VERSION = 1
URBAN_STATION_ID = "01424"
REFERENCE_STATION_ID = "01420"


def _gap_summary(label: str, gaps: list[float]) -> dict[str, Any]:
    if not gaps:
        # Degenerate input only (e.g. a season absent from a tiny test fixture);
        # real DWD data always has all four seasons represented over the full
        # 1985-2025 record. Disclosed as an explicit zero-count entry rather
        # than silently omitted or crashing the whole registry build.
        return {
            "label": label,
            "n_days": 0,
            "mean_gap_c": None,
            "ci_95_low": None,
            "ci_95_high": None,
            "block_length_days": None,
            "resamples": None,
            "seed": None,
            "gap_excludes_zero": False,
        }
    boot = block_bootstrap_mean_ci(gaps)
    return {
        "label": label,
        "n_days": len(gaps),
        "mean_gap_c": boot.mean,
        "ci_95_low": boot.ci_low,
        "ci_95_high": boot.ci_high,
        "block_length_days": boot.block_length,
        "resamples": boot.resamples,
        "seed": boot.seed,
        "gap_excludes_zero": bool(boot.ci_low > 0 or boot.ci_high < 0),
    }


def build_registry(urban_path: Path, reference_path: Path) -> dict[str, Any]:
    urban_readings = load_station_daily_kl(urban_path, URBAN_STATION_ID)
    reference_readings = load_station_daily_kl(reference_path, REFERENCE_STATION_ID)
    paired = build_paired_series(urban_readings, reference_readings)

    if not paired:
        raise ValueError("no overlapping valid days found between the two stations")

    all_gaps = [day.gap for day in paired]
    year_coverage = years_with_sufficient_coverage(paired)
    included_years = sorted(
        year for year, count in year_coverage.items() if count >= MIN_VALID_DAYS_PER_YEAR
    )
    excluded_years = sorted(set(year_coverage) - set(included_years))

    annual_means: dict[int, float] = {}
    for day in paired:
        annual_means.setdefault(day.date.year, [])  # type: ignore[arg-type]
    by_year: dict[int, list[float]] = {}
    for day in paired:
        by_year.setdefault(day.date.year, []).append(day.gap)
    annual_means = {year: sum(vals) / len(vals) for year, vals in by_year.items()}

    trend_years = included_years
    trend_values = [annual_means[y] for y in trend_years]
    trend_info: dict[str, Any]
    if len(trend_years) >= 2:
        trend = linear_trend(trend_years, trend_values)
        trend_info = {
            "label": "OLS linear trend of annual mean gap vs. year, included years only",
            "slope_c_per_year": trend.slope_per_year,
            "intercept_c": trend.intercept,
            "ci_95_low": trend.ci_low,
            "ci_95_high": trend.ci_high,
            "p_value": trend.p_value,
            "r_squared": trend.r_squared,
            "n_years": trend.n_years,
            "alpha": ALPHA,
            "significant": trend.significant,
            "slope_ci_excludes_zero": bool(trend.ci_low > 0 or trend.ci_high < 0),
        }
    else:
        trend_info = {
            "label": "insufficient included years (< 2) to estimate a trend",
            "slope_c_per_year": None,
            "intercept_c": None,
            "ci_95_low": None,
            "ci_95_high": None,
            "p_value": None,
            "r_squared": None,
            "n_years": len(trend_years),
            "alpha": ALPHA,
            "significant": False,
            "slope_ci_excludes_zero": False,
        }

    seasonal: dict[str, list[float]] = {"DJF": [], "MAM": [], "JJA": [], "SON": []}
    for day in paired:
        seasonal[meteorological_season(day.date)].append(day.gap)

    registry: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "stations": {
            "urban": {"id": URBAN_STATION_ID, "name": "Frankfurt/Main-Westend"},
            "reference": {"id": REFERENCE_STATION_ID, "name": "Frankfurt/Main"},
        },
        "period": {
            "start_date": paired[0].date.isoformat(),
            "end_date": paired[-1].date.isoformat(),
            "n_valid_paired_days": len(paired),
        },
        "settings": {
            "alpha": ALPHA,
            "bootstrap_resamples": DEFAULT_BOOTSTRAP_RESAMPLES,
            "bootstrap_seed": DEFAULT_SEED,
            "block_length_days": DEFAULT_BLOCK_LENGTH,
            "min_valid_days_per_year": MIN_VALID_DAYS_PER_YEAR,
        },
        "year_coverage": {
            "counts": {str(year): count for year, count in year_coverage.items()},
            "included_years": [str(y) for y in included_years],
            "excluded_years": [str(y) for y in excluded_years],
        },
        "gap": {
            "full_period": _gap_summary(
                "Full period (1985-11-01 through 2025-12-31), all valid paired days", all_gaps
            ),
            "by_season": {
                season: _gap_summary(f"Meteorological season {season}", gaps)
                for season, gaps in seasonal.items()
            },
        },
        "trend": trend_info,
        "annual_means": {str(year): annual_means[year] for year in sorted(annual_means)},
        "daily_series": _daily_series_json(paired),
    }
    return registry


def _daily_series_json(paired: list[PairedDay]) -> list[dict[str, Any]]:
    return [
        {
            "date": day.date.isoformat(),
            "urban_tmk_c": day.urban_tmk,
            "reference_tmk_c": day.reference_tmk,
            "gap_c": day.gap,
        }
        for day in paired
    ]
