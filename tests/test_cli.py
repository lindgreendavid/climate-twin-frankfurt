from __future__ import annotations

import json
from pathlib import Path

import pytest

from climate_twin_frankfurt.cli import main


def test_summarize_prints_gap_and_trend(
    urban_station_file: Path, reference_station_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(
        [
            "summarize",
            "--urban",
            str(urban_station_file),
            "--reference",
            str(reference_station_file),
        ]
    )
    assert exit_code == 0
    out = capsys.readouterr().out
    assert "valid paired days" in out
    assert "Mean urban-reference gap" in out
    assert "Trend" in out


def test_registry_command_writes_output_file(
    urban_station_file: Path, reference_station_file: Path, tmp_path: Path
) -> None:
    output = tmp_path / "registry.json"
    exit_code = main(
        [
            "registry",
            "--urban",
            str(urban_station_file),
            "--reference",
            str(reference_station_file),
            "--output",
            str(output),
        ]
    )
    assert exit_code == 0
    data = json.loads(output.read_text())
    assert data["schema_version"] == 1


def test_registry_command_prints_to_stdout(
    urban_station_file: Path, reference_station_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = main(
        ["registry", "--urban", str(urban_station_file), "--reference", str(reference_station_file)]
    )
    assert exit_code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["schema_version"] == 1


def test_main_requires_a_command() -> None:
    with pytest.raises(SystemExit):
        main([])
