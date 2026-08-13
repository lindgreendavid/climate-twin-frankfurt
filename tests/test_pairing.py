from __future__ import annotations

import datetime as dt
from pathlib import Path

from climate_twin_frankfurt.pairing import (
    build_paired_series,
    meteorological_season,
    years_with_sufficient_coverage,
)
from climate_twin_frankfurt.stations import load_station_daily_kl


def test_build_paired_series_inner_joins_on_date(
    urban_station_file: Path, reference_station_file: Path
) -> None:
    urban = load_station_daily_kl(urban_station_file, "01424")
    reference = load_station_daily_kl(reference_station_file, "01420")
    paired = build_paired_series(urban, reference)
    # urban has a missing day (Jan 2); reference is missing nothing there but
    # the join must still exclude Jan 2 (urban side missing) and Jan 6
    # (urban has no row at all for that date).
    dates = [p.date for p in paired]
    assert dt.date(2020, 1, 2) not in dates
    assert dt.date(2020, 1, 6) not in dates
    assert len(paired) == 4


def test_paired_day_gap_is_urban_minus_reference(
    urban_station_file: Path, reference_station_file: Path
) -> None:
    urban = load_station_daily_kl(urban_station_file, "01424")
    reference = load_station_daily_kl(reference_station_file, "01420")
    paired = build_paired_series(urban, reference)
    first = paired[0]
    assert first.urban_tmk == 3.5
    assert first.reference_tmk == 2.9
    assert round(first.gap, 2) == 0.6


def test_years_with_sufficient_coverage_counts_all_years(
    urban_station_file: Path, reference_station_file: Path
) -> None:
    urban = load_station_daily_kl(urban_station_file, "01424")
    reference = load_station_daily_kl(reference_station_file, "01420")
    paired = build_paired_series(urban, reference)
    counts = years_with_sufficient_coverage(paired)
    assert counts == {2020: 4}


def test_meteorological_season_boundaries() -> None:
    assert meteorological_season(dt.date(2020, 1, 15)) == "DJF"
    assert meteorological_season(dt.date(2020, 2, 29)) == "DJF"
    assert meteorological_season(dt.date(2020, 3, 1)) == "MAM"
    assert meteorological_season(dt.date(2020, 5, 31)) == "MAM"
    assert meteorological_season(dt.date(2020, 6, 1)) == "JJA"
    assert meteorological_season(dt.date(2020, 8, 31)) == "JJA"
    assert meteorological_season(dt.date(2020, 9, 1)) == "SON"
    assert meteorological_season(dt.date(2020, 11, 30)) == "SON"
    assert meteorological_season(dt.date(2020, 12, 1)) == "DJF"
