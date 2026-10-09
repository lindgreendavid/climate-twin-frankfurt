"""POST-HOC (not preregistered): other temperature variables and station-relocation step checks.

The frozen study analysed only the daily mean (TMK) and stated two untested limitations: that daily
minimum and maximum temperature (TNK, TXK) could show a different urban-reference gap, and that
the documented station relocations (urban 2008-07-01, reference 2014-10-22) might have introduced
step changes. This module tests both, with the same block-bootstrap machinery as the frozen
analysis, and reports every result:

* the full-period and seasonal mean gap for TMK, TNK and TXK, with annual-mean trends and a
  Newey-West (3-lag) interval;
* the change in mean gap across each relocation, as the difference between the mean gap in the
  three years after and the three years before, with a block-bootstrap 95% interval.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy import stats as scipy_stats

from climate_twin_frankfurt.pairing import MIN_VALID_DAYS_PER_YEAR, meteorological_season
from climate_twin_frankfurt.stats import DEFAULT_BLOCK_LENGTH, block_bootstrap_mean_ci

VARIABLES = ("TMK", "TNK", "TXK")
EXTENSION_SEED = 20261009
RELOCATIONS = {
    "urban_relocation_2008-07-01": dt.date(2008, 7, 1),
    "reference_relocation_2014-10-22": dt.date(2014, 10, 22),
}
WINDOW_YEARS = 3
NEWEY_WEST_LAGS = 3
MISSING = -999.0


@dataclass(frozen=True)
class DailyValues:
    date: dt.date
    values: dict[str, float | None]


def load_raw_daily(path: Path) -> list[DailyValues]:
    """Parse a DWD `produkt_klima_tag_*.txt` file, keeping TMK/TNK/TXK (-999 -> None)."""
    lines = Path(path).read_text(encoding="latin-1").splitlines()
    header = [c.strip() for c in lines[0].split(";")]
    index = {name: header.index(name) for name in ("MESS_DATUM", *VARIABLES)}
    out: list[DailyValues] = []
    for line in lines[1:]:
        cells = [c.strip() for c in line.split(";")]
        if len(cells) <= max(index.values()) or not cells[index["MESS_DATUM"]]:
            continue
        raw = cells[index["MESS_DATUM"]]
        date = dt.date(int(raw[:4]), int(raw[4:6]), int(raw[6:8]))
        values = {}
        for name in VARIABLES:
            v = float(cells[index[name]])
            values[name] = None if v <= MISSING else v
        out.append(DailyValues(date, values))
    return out


def paired_gaps(
    urban: list[DailyValues], reference: list[DailyValues], variable: str
) -> list[tuple[dt.date, float]]:
    ref = {d.date: d.values[variable] for d in reference if d.values[variable] is not None}
    gaps = []
    for d in urban:
        u = d.values[variable]
        r = ref.get(d.date)
        if u is not None and r is not None:
            gaps.append((d.date, u - r))
    gaps.sort()
    return gaps


def _hac_fit(
    design: NDArray[np.float64], y: NDArray[np.float64], lags: int
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """OLS coefficients and Newey-West (Bartlett kernel) standard errors."""
    n, k = design.shape
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    resid = y - design @ beta
    xu = design * resid[:, None]
    s = xu.T @ xu
    for lag in range(1, lags + 1):
        weight = 1 - lag / (lags + 1)
        gamma = xu[lag:].T @ xu[:-lag]
        s += weight * (gamma + gamma.T)
    bread = np.linalg.inv(design.T @ design)
    cov = bread @ s @ bread * n / (n - k)
    return np.asarray(beta, dtype=np.float64), np.asarray(np.sqrt(np.diag(cov)), dtype=np.float64)


def _coef(beta: float, se: float, df: int) -> dict[str, float]:
    t = float(scipy_stats.t.ppf(0.975, df=df))
    p = float(2 * scipy_stats.t.sf(abs(beta / se), df=df))
    return {
        "estimate": float(beta),
        "ci_low": float(beta - t * se),
        "ci_high": float(beta + t * se),
        "p_value": p,
    }


def newey_west_slope(
    years: list[int], means: list[float], lags: int = NEWEY_WEST_LAGS
) -> dict[str, float]:
    """OLS slope of annual means on year with a Newey-West HAC 95% interval (t, n-2 d.f.)."""
    x = np.asarray(years, dtype=float)
    design = np.column_stack([np.ones(len(x)), x - x.mean()])
    beta, se = _hac_fit(design, np.asarray(means, dtype=float), lags)
    c = _coef(beta[1], se[1], len(x) - 2)
    return {
        "slope_per_year": c["estimate"],
        "ci_low": c["ci_low"],
        "ci_high": c["ci_high"],
        "p_value": c["p_value"],
    }


STEP_YEARS = (2009, 2015)


def step_adjusted_trend(
    years: list[int], means: list[float], lags: int = NEWEY_WEST_LAGS
) -> dict[str, Any]:
    """Annual-mean regression with level shifts from 2009 (after the urban move) and 2015 (after
    the reference move), with Newey-West intervals. Descriptive, not a homogenization."""
    x = np.asarray(years, dtype=float)
    steps = [(x >= s).astype(float) for s in STEP_YEARS]
    design = np.column_stack([np.ones(len(x)), x - x.mean(), *steps])
    beta, se = _hac_fit(design, np.asarray(means, dtype=float), lags)
    df = len(x) - design.shape[1]
    return {
        "slope_per_year": _coef(beta[1], se[1], df),
        "step_2009": _coef(beta[2], se[2], df),
        "step_2015": _coef(beta[3], se[3], df),
    }


SEGMENTS = {
    "1985-11_to_2008-06": (dt.date(1985, 11, 1), dt.date(2008, 7, 1)),
    "2008-07_to_2014-10": (dt.date(2008, 7, 1), dt.date(2014, 10, 22)),
    "2014-10_to_2025": (dt.date(2014, 10, 22), dt.date(2026, 1, 1)),
}


def segment_means(gaps: list[tuple[dt.date, float]]) -> dict[str, Any]:
    out = {}
    for name, (start, end) in SEGMENTS.items():
        values = [g for d, g in gaps if start <= d < end]
        b = block_bootstrap_mean_ci(values, seed=EXTENSION_SEED)
        out[name] = {"n": b.n, "mean": b.mean, "ci_95": [b.ci_low, b.ci_high]}
    return out


def _block_means(
    values: NDArray[np.float64], resamples: int, seed: int, block: int
) -> NDArray[np.float64]:
    n = values.size
    block = min(block, n)
    n_blocks = -(-n // block)
    rng = np.random.default_rng(seed)
    out = np.empty(resamples)
    for i in range(resamples):
        starts = rng.integers(0, n - block + 1, size=n_blocks)
        out[i] = np.concatenate([values[s : s + block] for s in starts])[:n].mean()
    return out


def relocation_step(
    gaps: list[tuple[dt.date, float]],
    when: dt.date,
    window_years: int = WINDOW_YEARS,
    resamples: int = 5_000,
    seed: int = EXTENSION_SEED,
) -> dict[str, float]:
    """Mean gap in the window after minus before a relocation, with a block-bootstrap CI."""
    span = dt.timedelta(days=round(365.25 * window_years))
    before = np.array([g for d, g in gaps if when - span <= d < when])
    after = np.array([g for d, g in gaps if when <= d < when + span])
    diff_boot = _block_means(after, resamples, seed, DEFAULT_BLOCK_LENGTH) - _block_means(
        before, resamples, seed + 1, DEFAULT_BLOCK_LENGTH
    )
    lo, hi = np.percentile(diff_boot, [2.5, 97.5])
    return {
        "n_before": float(before.size),
        "n_after": float(after.size),
        "mean_before": float(before.mean()),
        "mean_after": float(after.mean()),
        "difference_after_minus_before": float(after.mean() - before.mean()),
        "ci_95_low": float(lo),
        "ci_95_high": float(hi),
    }


def variable_summary(gaps: list[tuple[dt.date, float]]) -> dict[str, Any]:
    values = [g for _, g in gaps]
    full = block_bootstrap_mean_ci(values, seed=EXTENSION_SEED)
    seasons = {}
    for season in ("DJF", "MAM", "JJA", "SON"):
        v = [g for d, g in gaps if meteorological_season(d) == season]
        b = block_bootstrap_mean_ci(v, seed=EXTENSION_SEED)
        seasons[season] = {"n": b.n, "mean": b.mean, "ci_95": [b.ci_low, b.ci_high]}
    by_year: dict[int, list[float]] = {}
    for d, g in gaps:
        by_year.setdefault(d.year, []).append(g)
    years = [y for y, v in sorted(by_year.items()) if len(v) >= MIN_VALID_DAYS_PER_YEAR]
    means = [float(np.mean(by_year[y])) for y in years]
    ols = scipy_stats.linregress(years, means)
    return {
        "n_days": full.n,
        "mean_gap": full.mean,
        "mean_gap_ci_95": [full.ci_low, full.ci_high],
        "seasons": seasons,
        "n_years": len(years),
        "ols_slope_per_year": float(ols.slope),
        "ols_p_value": float(ols.pvalue),
        "newey_west": newey_west_slope(years, means),
        "step_adjusted_trend": step_adjusted_trend(years, means),
        "segment_means": segment_means(gaps),
        "annual_means": {str(y): m for y, m in zip(years, means, strict=True)},
    }


def build_extensions(urban_path: Path, reference_path: Path) -> dict[str, Any]:
    urban = load_raw_daily(urban_path)
    reference = load_raw_daily(reference_path)
    out: dict[str, Any] = {
        "schema_version": 1,
        "label": "POST-HOC (not preregistered): other variables and relocation step checks",
        "seed": EXTENSION_SEED,
        "variables": {},
        "relocation_steps": {},
    }
    for variable in VARIABLES:
        gaps = paired_gaps(urban, reference, variable)
        out["variables"][variable] = variable_summary(gaps)
        out["relocation_steps"][variable] = {
            name: relocation_step(gaps, when) for name, when in RELOCATIONS.items()
        }
    return out
