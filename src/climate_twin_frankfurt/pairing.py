"""Build the daily urban-minus-reference temperature gap series.

See `docs/research-protocol.md`: a day is included only if both stations
report a non-missing TMK for that exact calendar date.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from climate_twin_frankfurt.stations import DailyReading

MIN_VALID_DAYS_PER_YEAR = 300


@dataclass(frozen=True)
class PairedDay:
    date: dt.date
    urban_tmk: float
    reference_tmk: float

    @property
    def gap(self) -> float:
        """Urban minus reference daily mean temperature, degrees C."""
        return self.urban_tmk - self.reference_tmk


def build_paired_series(
    urban_readings: list[DailyReading],
    reference_readings: list[DailyReading],
) -> list[PairedDay]:
    """Inner-join both stations' readings on date, keeping only non-missing TMK on both sides."""
    reference_by_date = {r.date: r.tmk for r in reference_readings if r.tmk is not None}
    paired: list[PairedDay] = []
    for reading in urban_readings:
        if reading.tmk is None:
            continue
        ref_tmk = reference_by_date.get(reading.date)
        if ref_tmk is None:
            continue
        paired.append(PairedDay(date=reading.date, urban_tmk=reading.tmk, reference_tmk=ref_tmk))
    paired.sort(key=lambda p: p.date)
    return paired


def years_with_sufficient_coverage(
    paired: list[PairedDay], min_valid_days: int = MIN_VALID_DAYS_PER_YEAR
) -> dict[int, int]:
    """Return {year: count} for every year present, regardless of threshold.

    Callers decide inclusion by comparing counts to `min_valid_days`; this
    function itself performs no filtering so the full disclosed count is
    always available to report.
    """
    counts: dict[int, int] = {}
    for day in paired:
        counts[day.date.year] = counts.get(day.date.year, 0) + 1
    return dict(sorted(counts.items()))


def meteorological_season(date: dt.date) -> str:
    """Meteorological (not astronomical) season: DJF/MAM/JJA/SON."""
    month = date.month
    if month in (12, 1, 2):
        return "DJF"
    if month in (3, 4, 5):
        return "MAM"
    if month in (6, 7, 8):
        return "JJA"
    return "SON"
