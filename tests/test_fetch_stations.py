from __future__ import annotations

import importlib.util
import io
import sys
import zipfile
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "fetch_stations.py"
_spec = importlib.util.spec_from_file_location("fetch_stations", SCRIPT_PATH)
assert _spec is not None and _spec.loader is not None
fetch_stations = importlib.util.module_from_spec(_spec)
sys.modules["fetch_stations"] = fetch_stations
_spec.loader.exec_module(fetch_stations)

HEADER = (
    "STATIONS_ID;MESS_DATUM;QN_3;FX;FM;QN_4;RSK;RSKF;SDK;SHK_TAG;NM;VPM;PM;TMK;UPM;TXK;TNK;TGK;eor"
)


def _make_zip(produkt_name: str, station_id: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        row = (
            f"{station_id};20200101;1;-999;-999;1;0.0;0;-999;0;5.0;"
            "8.0;-999;3.0;70.0;9.0;2.0;-999;eor"
        )
        content = HEADER + "\n" + row + "\n"
        archive.writestr(produkt_name, content)
        archive.writestr("Metadaten_Geographie_x.txt", "irrelevant")
    return buffer.getvalue()


def test_extract_produkt_file_writes_expected_target(tmp_path: Path) -> None:
    zip_bytes = _make_zip("produkt_klima_tag_19851101_20251231_01424.txt", "1424")
    target = fetch_stations._extract_produkt_file(zip_bytes, "01424", tmp_path)
    assert target.name == "produkt_klima_tag_01424.txt"
    assert target.exists()


def test_extract_produkt_file_raises_on_zero_matches(tmp_path: Path) -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("Metadaten_Geographie_x.txt", "irrelevant")
    from climate_twin_frankfurt.stations import StationDataError

    with pytest.raises(StationDataError, match="expected exactly 1"):
        fetch_stations._extract_produkt_file(buffer.getvalue(), "01424", tmp_path)


def test_extract_produkt_file_raises_on_multiple_matches(tmp_path: Path) -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("produkt_klima_tag_a.txt", "x")
        archive.writestr("produkt_klima_tag_b.txt", "y")
    from climate_twin_frankfurt.stations import StationDataError

    with pytest.raises(StationDataError, match="expected exactly 1"):
        fetch_stations._extract_produkt_file(buffer.getvalue(), "01424", tmp_path)


def test_fetch_station_downloads_extracts_and_verifies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    zip_bytes = _make_zip("produkt_klima_tag_19851101_20251231_01424.txt", "1424")
    monkeypatch.setattr(fetch_stations, "_download", lambda url: zip_bytes)
    target = fetch_stations.fetch_station("urban", tmp_path)
    assert target.exists()


def test_fetch_station_raises_on_empty_parsed_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("produkt_klima_tag_19851101_20251231_01424.txt", HEADER + "\n")
    monkeypatch.setattr(fetch_stations, "_download", lambda url: buffer.getvalue())
    from climate_twin_frankfurt.stations import StationDataError

    with pytest.raises(StationDataError, match="zero rows"):
        fetch_stations.fetch_station("urban", tmp_path)


def test_main_fetches_both_stations(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_download(url: str) -> bytes:
        station_id = "1424" if "01424" in url else "1420"
        name = f"produkt_klima_tag_19000101_20251231_{station_id.zfill(5)}.txt"
        return _make_zip(name, station_id)

    monkeypatch.setattr(fetch_stations, "_download", fake_download)
    exit_code = fetch_stations.main(["--output-dir", str(tmp_path)])
    assert exit_code == 0
    assert (tmp_path / "produkt_klima_tag_01424.txt").exists()
    assert (tmp_path / "produkt_klima_tag_01420.txt").exists()
