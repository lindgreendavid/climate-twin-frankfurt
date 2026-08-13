"""Statistical methods for the urban-heat-island gap and its trend.

See `docs/research-protocol.md` for the preregistered method: a block
bootstrap (not i.i.d.) confidence interval on the mean daily gap, because
consecutive days are strongly autocorrelated, and ordinary least squares on
annual mean gaps for the trend, with a classical t-distribution CI on the
slope.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats as scipy_stats

DEFAULT_SEED = 20260813
DEFAULT_BOOTSTRAP_RESAMPLES = 10_000
DEFAULT_BLOCK_LENGTH = 30
ALPHA = 0.05


@dataclass(frozen=True)
class BlockBootstrapResult:
    mean: float
    ci_low: float
    ci_high: float
    resamples: int
    block_length: int
    seed: int
    n: int


@dataclass(frozen=True)
class TrendResult:
    slope_per_year: float
    intercept: float
    ci_low: float
    ci_high: float
    p_value: float
    r_squared: float
    n_years: int
    significant: bool


def block_bootstrap_mean_ci(
    values: list[float],
    *,
    block_length: int = DEFAULT_BLOCK_LENGTH,
    resamples: int = DEFAULT_BOOTSTRAP_RESAMPLES,
    seed: int = DEFAULT_SEED,
) -> BlockBootstrapResult:
    """Moving-block bootstrap 95% CI for the mean of an ordered (e.g. daily) series.

    Resamples fixed-length contiguous blocks (with replacement, allowing
    overlapping start positions) to reconstruct series of the same total
    length as `values`, which is more appropriate than an i.i.d. bootstrap
    for autocorrelated daily temperature-gap data.
    """
    arr = np.asarray(values, dtype=float)
    n = arr.size
    if n == 0:
        raise ValueError("cannot bootstrap an empty series")
    block_length = min(block_length, n)
    n_blocks = -(-n // block_length)  # ceil division
    max_start = n - block_length
    rng = np.random.default_rng(seed)

    means = np.empty(resamples, dtype=float)
    for i in range(resamples):
        starts = rng.integers(0, max_start + 1, size=n_blocks)
        blocks = [arr[s : s + block_length] for s in starts]
        resample = np.concatenate(blocks)[:n]
        means[i] = float(np.mean(resample))

    ci_low, ci_high = np.percentile(means, [2.5, 97.5])
    return BlockBootstrapResult(
        mean=float(np.mean(arr)),
        ci_low=float(ci_low),
        ci_high=float(ci_high),
        resamples=resamples,
        block_length=block_length,
        seed=seed,
        n=n,
    )


def linear_trend(years: list[int], annual_means: list[float]) -> TrendResult:
    """OLS trend of annual mean gap vs. year, with a classical t-distribution slope CI."""
    if len(years) != len(annual_means):
        raise ValueError("years and annual_means must have the same length")
    n = len(years)
    if n < 2:
        raise ValueError("need at least 2 years to estimate a trend")

    x = np.asarray(years, dtype=float)
    y = np.asarray(annual_means, dtype=float)
    result = scipy_stats.linregress(x, y)
    slope = float(result.slope)
    intercept = float(result.intercept)
    stderr = float(result.stderr)
    p_value = float(result.pvalue)
    r_squared = float(result.rvalue) ** 2

    t_crit = float(scipy_stats.t.ppf(1 - ALPHA / 2, df=n - 2))
    margin = t_crit * stderr
    return TrendResult(
        slope_per_year=slope,
        intercept=intercept,
        ci_low=slope - margin,
        ci_high=slope + margin,
        p_value=p_value,
        r_squared=r_squared,
        n_years=n,
        significant=bool(p_value < ALPHA),
    )
