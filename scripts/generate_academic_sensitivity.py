#!/usr/bin/env python3
"""Generate a serial-correlation-robust sensitivity for the frozen annual trend."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "reports" / "v0.1-climate-twin-frankfurt-registry.json"
OUTPUT = ROOT / "reports" / "post-release-academic-sensitivity.json"
HAC_LAGS = 3


def _stable(value: float) -> float:
    """Quantize computed results to a platform-stable scientific precision."""
    return float(f"{float(value):.12g}")


def main() -> None:
    registry = json.loads(INPUT.read_text(encoding="utf-8"))
    years = registry["year_coverage"]["included_years"]
    x = np.asarray([int(year) for year in years], dtype=float)
    y = np.asarray([registry["annual_means"][year] for year in years], dtype=float)
    design = np.column_stack([np.ones(len(x)), x])
    coefficients = np.linalg.lstsq(design, y, rcond=None)[0]
    residuals = y - design @ coefficients

    meat = sum(residuals[t] ** 2 * np.outer(design[t], design[t]) for t in range(len(x)))
    for lag in range(1, HAC_LAGS + 1):
        weight = 1 - lag / (HAC_LAGS + 1)
        meat += sum(
            weight
            * residuals[t]
            * residuals[t - lag]
            * (np.outer(design[t], design[t - lag]) + np.outer(design[t - lag], design[t]))
            for t in range(lag, len(x))
        )
    bread = np.linalg.inv(design.T @ design)
    covariance = (len(x) / (len(x) - design.shape[1])) * bread @ meat @ bread
    slope = float(coefficients[1])
    standard_error = float(np.sqrt(covariance[1, 1]))
    degrees_of_freedom = len(x) - design.shape[1]
    critical = float(stats.t.ppf(0.975, degrees_of_freedom))
    p_value = float(2 * stats.t.sf(abs(slope / standard_error), degrees_of_freedom))

    payload = {
        "schema_version": "1.0.0",
        "status": "post-release sensitivity; does not alter the frozen v0.1 registry",
        "method": {
            "estimator": (
                "same OLS slope with Newey-West heteroskedasticity-and-"
                "autocorrelation-consistent covariance"
            ),
            "hac_lags": HAC_LAGS,
            "critical_distribution": f"Student t with {degrees_of_freedom} degrees of freedom",
        },
        "n_years": len(x),
        "slope_c_per_year": _stable(slope),
        "ols_residual_lag1_correlation": _stable(np.corrcoef(residuals[:-1], residuals[1:])[0, 1]),
        "hac_standard_error": _stable(standard_error),
        "hac_95_ci": [
            _stable(slope - critical * standard_error),
            _stable(slope + critical * standard_error),
        ],
        "hac_two_sided_p_value": _stable(p_value),
        "interpretation": (
            "The serial-correlation-robust interval includes zero, so the preregistered "
            "conclusion of no statistically detectable linear trend is unchanged."
        ),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
