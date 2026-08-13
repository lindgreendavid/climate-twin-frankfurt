from __future__ import annotations

import pytest

from climate_twin_frankfurt.stats import block_bootstrap_mean_ci, linear_trend


def test_block_bootstrap_mean_matches_naive_mean() -> None:
    values = [1.0, 2.0, 3.0, 4.0, 5.0] * 20
    result = block_bootstrap_mean_ci(values, block_length=5, resamples=500, seed=1)
    assert result.mean == pytest.approx(3.0)
    assert result.ci_low <= result.mean <= result.ci_high


def test_block_bootstrap_is_reproducible_with_same_seed() -> None:
    values = [0.1 * i for i in range(200)]
    a = block_bootstrap_mean_ci(values, block_length=10, resamples=300, seed=42)
    b = block_bootstrap_mean_ci(values, block_length=10, resamples=300, seed=42)
    assert a == b


def test_block_bootstrap_empty_series_raises() -> None:
    with pytest.raises(ValueError, match="empty"):
        block_bootstrap_mean_ci([])


def test_block_bootstrap_block_length_capped_at_n() -> None:
    result = block_bootstrap_mean_ci([1.0, 2.0, 3.0], block_length=100, resamples=10, seed=1)
    assert result.block_length == 3


def test_linear_trend_detects_positive_slope() -> None:
    years = list(range(2000, 2020))
    values = [0.5 + 0.02 * (y - 2000) for y in years]
    trend = linear_trend(years, values)
    assert trend.slope_per_year == pytest.approx(0.02, abs=1e-6)
    assert trend.significant is True
    assert trend.ci_low > 0


def test_linear_trend_flat_series_not_significant() -> None:
    years = list(range(2000, 2020))
    # tiny alternating noise around a flat mean, no real trend
    values = [0.5 + (0.001 if y % 2 == 0 else -0.001) for y in years]
    trend = linear_trend(years, values)
    assert trend.significant is False
    assert trend.ci_low < 0 < trend.ci_high


def test_linear_trend_requires_at_least_two_years() -> None:
    with pytest.raises(ValueError, match="at least 2"):
        linear_trend([2020], [1.0])


def test_linear_trend_requires_matching_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        linear_trend([2020, 2021], [1.0])
