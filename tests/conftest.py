"""Shared pytest fixtures: small synthetic DWD-format station files for unit tests.

This fixture data is NOT real DWD station data — it exists only to exercise
the parsing, pairing, and statistics code paths deterministically and
quickly. Real-data verification lives in scripts/fetch_stations.py and is
run against the live DWD CDC source, not in this offline test suite.
"""

from __future__ import annotations

from pathlib import Path

import pytest

HEADER = (
    "STATIONS_ID;MESS_DATUM;QN_3;  FX;  FM;QN_4; RSK;RSKF; SDK;SHK_TAG;  NM; VPM;  PM; TMK;"
    " UPM; TXK; TNK; TGK;eor"
)


def _row(station_id: str, date: str, tmk: str) -> str:
    return (
        f"{station_id};{date};   1;-999;-999;    1;   0.0;   0;-999;   0;   5.0;"
        f"   8.0;    -999;{tmk:>8};   70.00;    9.0;    2.0;-999;eor"
    )


@pytest.fixture
def urban_station_file(tmp_path: Path) -> Path:
    """A tiny synthetic 'Frankfurt/Main-Westend' (01424)-shaped daily file."""
    rows = [HEADER]
    # 5 days in Jan 2020, warmer than the reference station by ~0.5-1.5 C
    values = ["3.5", "-999", "4.2", "5.0", "3.8"]  # one missing day (day 2)
    for i, tmk in enumerate(values, start=1):
        rows.append(_row("1424", f"202001{i:02d}", tmk))
    path = tmp_path / "produkt_klima_tag_01424.txt"
    path.write_text("\n".join(rows) + "\n", encoding="latin-1")
    return path


@pytest.fixture
def reference_station_file(tmp_path: Path) -> Path:
    """A tiny synthetic 'Frankfurt/Main' (01420)-shaped daily file, slightly cooler."""
    rows = [HEADER]
    values = ["2.9", "1.0", "3.6", "4.1", "3.0"]
    for i, tmk in enumerate(values, start=1):
        rows.append(_row("1420", f"202001{i:02d}", tmk))
    # one extra day the urban station lacks: 2020-01-06
    rows.append(_row("1420", "20200106", "3.3"))
    path = tmp_path / "produkt_klima_tag_01420.txt"
    path.write_text("\n".join(rows) + "\n", encoding="latin-1")
    return path
