from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

from climate_twin_frankfurt.stations import (
    StationDataError,
    load_station_daily_kl,
    valid_readings,
)

from .conftest import HEADER


def test_load_station_parses_rows_and_handles_missing(urban_station_file: Path) -> None:
    readings = load_station_daily_kl(urban_station_file, "01424")
    assert len(readings) == 5
    assert readings[0].date == dt.date(2020, 1, 1)
    assert readings[0].tmk == 3.5
    assert readings[1].tmk is None  # -999 sentinel


def test_load_station_sorts_by_date(urban_station_file: Path) -> None:
    readings = load_station_daily_kl(urban_station_file, "01424")
    dates = [r.date for r in readings]
    assert dates == sorted(dates)


def test_load_station_accepts_unpadded_station_id(urban_station_file: Path) -> None:
    # the raw file contains "1424", not "01424"; the loader must accept both
    readings = load_station_daily_kl(urban_station_file, "01424")
    assert all(r.station_id == "01424" for r in readings)


def test_load_station_rejects_wrong_station_id(urban_station_file: Path) -> None:
    with pytest.raises(StationDataError, match="STATIONS_ID"):
        load_station_daily_kl(urban_station_file, "99999")


def test_valid_readings_drops_missing(urban_station_file: Path) -> None:
    readings = load_station_daily_kl(urban_station_file, "01424")
    valid = valid_readings(readings)
    assert len(valid) == 4
    assert all(r.tmk is not None for r in valid)


def test_load_station_missing_tmk_column(tmp_path: Path) -> None:
    path = tmp_path / "bad.txt"
    path.write_text("STATIONS_ID;MESS_DATUM;eor\n1420;20200101;eor\n", encoding="latin-1")
    with pytest.raises(StationDataError, match="TMK"):
        load_station_daily_kl(path, "01420")


def test_load_station_duplicate_date_keeps_first(tmp_path: Path) -> None:
    rows = [
        HEADER,
        "1420;20200101;1;-999;-999;1;0.0;0;-999;0;5.0;8.0;-999;3.0;70.0;9.0;2.0;-999;eor",
        "1420;20200101;1;-999;-999;1;0.0;0;-999;0;5.0;8.0;-999;99.0;70.0;9.0;2.0;-999;eor",
    ]
    path = tmp_path / "dup.txt"
    path.write_text("\n".join(rows) + "\n", encoding="latin-1")
    readings = load_station_daily_kl(path, "01420")
    assert len(readings) == 1
    assert readings[0].tmk == 3.0  # first occurrence kept, not the second (bogus 99.0)


def test_load_station_out_of_range_tmk_raises(tmp_path: Path) -> None:
    rows = [
        HEADER,
        "1420;20200101;1;-999;-999;1;0.0;0;-999;0;5.0;8.0;-999;123.0;70.0;9.0;2.0;-999;eor",
    ]
    path = tmp_path / "bad_range.txt"
    path.write_text("\n".join(rows) + "\n", encoding="latin-1")
    with pytest.raises(StationDataError, match="sanity range"):
        load_station_daily_kl(path, "01420")
