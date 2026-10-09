import datetime as dt
from pathlib import Path

import numpy as np
import pytest

from climate_twin_frankfurt.extensions import (
    build_extensions,
    load_raw_daily,
    newey_west_slope,
    paired_gaps,
    relocation_step,
    segment_means,
    step_adjusted_trend,
)

HEADER = (
    "STATIONS_ID;MESS_DATUM;QN_3;  FX;  FM;QN_4; RSK;RSKF; SDK;SHK_TAG;"
    "  NM; VPM;  PM; TMK; UPM; TXK; TNK; TGK;eor"
)


def write_station(path: Path, sid: int, start: dt.date, end: dt.date, offset) -> None:
    lines = [HEADER]
    d = start
    while d <= end:
        base = 10.0 + 8.0 * np.sin(2 * np.pi * d.timetuple().tm_yday / 365.25)
        tmk, tnk, txk = (
            base + offset(d, "TMK"),
            base - 3 + offset(d, "TNK"),
            base + 4 + offset(d, "TXK"),
        )
        lines.append(
            f"{sid};{d:%Y%m%d};-999;-999;-999;10;0.0;6;-999;0;5.0;7.0;-999;{tmk:.1f};80.0;{txk:.1f};{tnk:.1f};0.0;eor"
        )
        d += dt.timedelta(days=1)
    path.write_text("\n".join(lines) + "\n", encoding="latin-1")


def test_load_raw_daily_parses_values_and_missing(tmp_path):
    path = tmp_path / "s.txt"
    path.write_text(
        HEADER + "\n"
        "1424;19851101;-999;-999;-999;10;0.0;6;-999;0;7.7;7.6;-999;5.6;84.00;7.2;3.0;3.0;eor\n"
        "1424;19851102;-999;-999;-999;10;0.1;6;-999;0;6.3;7.2;-999;-999;78.00;8.2;-999;-1.0;eor\n",
        encoding="latin-1",
    )
    rows = load_raw_daily(path)
    assert rows[0].values == {"TMK": 5.6, "TNK": 3.0, "TXK": 7.2}
    assert rows[1].values["TMK"] is None and rows[1].values["TNK"] is None


def test_paired_gaps_skips_missing_on_either_side(tmp_path):
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    write_station(a, 1, dt.date(2000, 1, 1), dt.date(2000, 1, 5), lambda d, v: 1.0)
    write_station(b, 2, dt.date(2000, 1, 2), dt.date(2000, 1, 6), lambda d, v: 0.0)
    gaps = paired_gaps(load_raw_daily(a), load_raw_daily(b), "TMK")
    assert next(d for d, _ in gaps) == dt.date(2000, 1, 2) and len(gaps) == 4
    assert all(g == pytest.approx(1.0) for _, g in gaps)


def test_newey_west_slope_recovers_a_line():
    years = list(range(1990, 2030))
    means = [0.5 + 0.01 * (y - 1990) + 0.002 * ((-1) ** y) for y in years]
    out = newey_west_slope(years, means)
    assert out["slope_per_year"] == pytest.approx(0.01, abs=1e-3)
    assert out["ci_low"] < 0.01 < out["ci_high"]


def test_step_adjusted_trend_finds_the_step_and_no_slope():
    years = list(range(1986, 2026))
    rng = np.random.default_rng(1)
    means = [0.8 - 0.4 * (y >= 2009) + 0.2 * (y >= 2015) + rng.normal(0, 0.02) for y in years]
    out = step_adjusted_trend(years, means)
    assert out["step_2009"]["estimate"] == pytest.approx(-0.4, abs=0.05)
    assert out["step_2015"]["estimate"] == pytest.approx(0.2, abs=0.05)
    assert abs(out["slope_per_year"]["estimate"]) < 0.01


def synthetic_gaps(step_date, step):
    d, out = dt.date(2000, 1, 1), []
    rng = np.random.default_rng(2)
    while d < dt.date(2016, 1, 1):
        out.append((d, 0.5 + (step if d >= step_date else 0.0) + rng.normal(0, 0.3)))
        d += dt.timedelta(days=1)
    return out


def test_relocation_step_detects_a_real_step_and_not_a_null():
    gaps = synthetic_gaps(dt.date(2008, 7, 1), -0.4)
    real = relocation_step(gaps, dt.date(2008, 7, 1), resamples=300, seed=3)
    assert real["difference_after_minus_before"] == pytest.approx(-0.4, abs=0.08)
    assert real["ci_95_high"] < 0
    null = relocation_step(gaps, dt.date(2012, 1, 1), resamples=300, seed=3)
    assert null["ci_95_low"] < 0 < null["ci_95_high"]


def test_segment_means_cover_the_three_station_histories():
    out = segment_means(synthetic_gaps(dt.date(2008, 7, 1), -0.4))
    assert set(out) == {"1985-11_to_2008-06", "2008-07_to_2014-10", "2014-10_to_2025"}
    assert out["1985-11_to_2008-06"]["mean"] > out["2008-07_to_2014-10"]["mean"]


def test_build_extensions_end_to_end(tmp_path):
    u, r = tmp_path / "u.txt", tmp_path / "r.txt"
    start, end = dt.date(1986, 1, 1), dt.date(2025, 12, 31)
    write_station(
        u, 1424, start, end, lambda d, v: 0.5 - (0.4 if d >= dt.date(2008, 7, 1) else 0.0)
    )
    write_station(r, 1420, start, end, lambda d, v: 0.0)
    out = build_extensions(u, r)
    assert set(out["variables"]) == {"TMK", "TNK", "TXK"}
    step = out["relocation_steps"]["TMK"]["urban_relocation_2008-07-01"]
    assert step["difference_after_minus_before"] == pytest.approx(-0.4, abs=0.02)
    assert out["variables"]["TMK"]["n_years"] == 40
    assert out["label"].startswith("POST-HOC")
