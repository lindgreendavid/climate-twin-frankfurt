"""Parse DWD CDC daily climate summary ("Tageswerte KL") station files.

See `docs/research-protocol.md` for the exact file format, missing-value
sentinel, and sanity checks implemented here.
"""

from __future__ import annotations

import csv
import datetime as dt
from dataclasses import dataclass
from pathlib import Path

MISSING_SENTINEL = -999
TMK_MIN = -30.0
TMK_MAX = 40.0


class StationDataError(ValueError):
    """Raised when a DWD station file fails a disclosed sanity check."""


@dataclass(frozen=True)
class DailyReading:
    """One day's DWD daily climate summary reading for one station."""

    station_id: str
    date: dt.date
    tmk: float | None  # daily mean temperature, degrees C; None if missing


def _parse_date(raw: str) -> dt.date:
    return dt.datetime.strptime(raw.strip(), "%Y%m%d").date()


def load_station_daily_kl(path: Path, expected_station_id: str) -> list[DailyReading]:
    """Load a `produkt_klima_tag_*.txt` file into sorted, deduplicated daily readings.

    Applies the preregistered sanity checks: non-missing TMK must fall in
    [-30, 40] degrees C, STATIONS_ID must match `expected_station_id` for
    every row, and duplicate dates keep only their first occurrence.
    """
    path = Path(path)
    with path.open(newline="", encoding="latin-1") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        if reader.fieldnames is None or "TMK" not in [f.strip() for f in reader.fieldnames]:
            raise StationDataError(f"{path}: missing expected TMK column in header")
        field_map = {f.strip(): f for f in reader.fieldnames}

        seen_dates: set[dt.date] = set()
        readings: list[DailyReading] = []
        for row in reader:
            # DWD's own files print STATIONS_ID without zero-padding (e.g. "1424"),
            # while this project's station IDs are the zero-padded 5-digit form
            # used in DWD's file names and station lists (e.g. "01424"); compare
            # numerically so both conventions are accepted, but still report the
            # zero-padded form on the returned reading for consistency.
            raw_station_id = row[field_map["STATIONS_ID"]].strip()
            if int(raw_station_id) != int(expected_station_id):
                raise StationDataError(
                    f"{path}: row has STATIONS_ID {raw_station_id!r}, "
                    f"expected {expected_station_id!r}"
                )
            station_id = expected_station_id
            date = _parse_date(row[field_map["MESS_DATUM"]])
            if date in seen_dates:
                continue  # duplicate date: keep first occurrence only, per protocol
            seen_dates.add(date)

            raw_tmk = round(float(row[field_map["TMK"]].strip()))
            tmk: float | None
            if raw_tmk == MISSING_SENTINEL:
                tmk = None
            else:
                tmk = float(row[field_map["TMK"]].strip())
                if not (TMK_MIN <= tmk <= TMK_MAX):
                    raise StationDataError(
                        f"{path}: TMK={tmk} on {date} outside sanity range "
                        f"[{TMK_MIN}, {TMK_MAX}] degrees C"
                    )
            readings.append(DailyReading(station_id=station_id, date=date, tmk=tmk))

    readings.sort(key=lambda r: r.date)
    return readings


def valid_readings(readings: list[DailyReading]) -> list[DailyReading]:
    """Drop readings with a missing (None) TMK value."""
    return [r for r in readings if r.tmk is not None]
