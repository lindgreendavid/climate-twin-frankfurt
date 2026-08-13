#!/usr/bin/env python3
"""Fetch and verify the two DWD CDC daily-KL station archives used by this project.

Downloads the `historical/` archives (not `recent/` -- see
`docs/research-protocol.md`, "Reproducibility and snapshot pinning") for
Frankfurt/Main-Westend (01424, urban) and Frankfurt/Main (01420, DWD's own
designated reference counterpart), extracts each `produkt_klima_tag_*.txt`
file, and re-runs the sanity checks implemented in
`climate_twin_frankfurt.stations.load_station_daily_kl` before writing
anything out, aborting loudly on failure rather than silently writing a
possibly-wrong file.
"""

from __future__ import annotations

import argparse
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

from climate_twin_frankfurt.stations import StationDataError, load_station_daily_kl

BASE_URL = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical"

STATIONS = {
    "urban": {
        "id": "01424",
        "archive": "tageswerte_KL_01424_19851101_20251231_hist.zip",
    },
    "reference": {
        "id": "01420",
        "archive": "tageswerte_KL_01420_19350701_20251231_hist.zip",
    },
}


def _download(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as response:
        data: bytes = response.read()
        return data


def _extract_produkt_file(zip_bytes: bytes, station_id: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        produkt_names = [
            name for name in archive.namelist() if name.startswith("produkt_klima_tag_")
        ]
        if len(produkt_names) != 1:
            raise StationDataError(
                f"station {station_id}: expected exactly 1 produkt_klima_tag_* file in "
                f"archive, found {len(produkt_names)}: {produkt_names}"
            )
        name = produkt_names[0]
        target = output_dir / f"produkt_klima_tag_{station_id}.txt"
        target.write_bytes(archive.read(name))
        return target


def fetch_station(role: str, output_dir: Path, base_url: str = BASE_URL) -> Path:
    info = STATIONS[role]
    url = f"{base_url}/{info['archive']}"
    zip_bytes = _download(url)
    target = _extract_produkt_file(zip_bytes, info["id"], output_dir)
    # Verify by actually parsing it with the same loader the registry uses;
    # this aborts loudly (raises) if any sanity check fails.
    readings = load_station_daily_kl(target, info["id"])
    if not readings:
        raise StationDataError(f"station {info['id']}: parsed file has zero rows")
    print(f"station {info['id']} ({role}): {len(readings)} rows, wrote {target}")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data/external"))
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args(argv)

    for role in ("urban", "reference"):
        fetch_station(role, args.output_dir, args.base_url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
