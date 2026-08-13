from __future__ import annotations

from pathlib import Path

import pytest

from climate_twin_frankfurt.registry import build_registry

from .conftest import HEADER


def test_build_registry_schema(urban_station_file: Path, reference_station_file: Path) -> None:
    registry = build_registry(urban_station_file, reference_station_file)
    assert registry["schema_version"] == 1
    assert registry["stations"]["urban"]["id"] == "01424"
    assert registry["stations"]["reference"]["id"] == "01420"
    assert registry["period"]["n_valid_paired_days"] == 4
    assert set(registry["gap"]["by_season"]) == {"DJF", "MAM", "JJA", "SON"}
    assert len(registry["daily_series"]) == 4


def test_build_registry_gap_is_urban_minus_reference(
    urban_station_file: Path, reference_station_file: Path
) -> None:
    registry = build_registry(urban_station_file, reference_station_file)
    # all 4 synthetic urban days are warmer than reference, so mean gap > 0
    assert registry["gap"]["full_period"]["mean_gap_c"] > 0


def test_build_registry_excludes_years_below_threshold(
    urban_station_file: Path, reference_station_file: Path
) -> None:
    registry = build_registry(urban_station_file, reference_station_file)
    # only 4 days total, far below MIN_VALID_DAYS_PER_YEAR=300
    assert registry["year_coverage"]["included_years"] == []
    assert registry["year_coverage"]["excluded_years"] == ["2020"]


def test_build_registry_raises_on_no_overlap(tmp_path: Path) -> None:
    urban_row = "1424;20200101;1;-999;-999;1;0.0;0;-999;0;5.0;8.0;-999;3.0;70.0;9.0;2.0;-999;eor"
    ref_row = "1420;20210101;1;-999;-999;1;0.0;0;-999;0;5.0;8.0;-999;3.0;70.0;9.0;2.0;-999;eor"
    urban = tmp_path / "produkt_klima_tag_01424.txt"
    reference = tmp_path / "produkt_klima_tag_01420.txt"
    urban.write_text(HEADER + "\n" + urban_row + "\n", encoding="latin-1")
    reference.write_text(HEADER + "\n" + ref_row + "\n", encoding="latin-1")
    with pytest.raises(ValueError, match="no overlapping"):
        build_registry(urban, reference)


def test_build_registry_is_deterministic(
    urban_station_file: Path, reference_station_file: Path
) -> None:
    a = build_registry(urban_station_file, reference_station_file)
    b = build_registry(urban_station_file, reference_station_file)
    assert a == b
