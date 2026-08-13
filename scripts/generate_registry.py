#!/usr/bin/env python3
"""Generate the frozen v0.1.0 result registry deterministically.

Usage: python scripts/generate_registry.py \
    --output reports/v0.1-climate-twin-frankfurt-registry.json

Requires both stations' produkt files to already exist locally (see
`scripts/fetch_stations.py`). Regenerates byte-identically given fixed
input files and the fixed bootstrap seed in `climate_twin_frankfurt.stats`,
and is checked against the committed registry by `tests/test_registry.py`
and the CI `research-registry` job.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from climate_twin_frankfurt.registry import build_registry


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--urban",
        default="data/external/produkt_klima_tag_01424.txt",
        help="Path to the urban station's produkt file (from scripts/fetch_stations.py)",
    )
    parser.add_argument(
        "--reference",
        default="data/external/produkt_klima_tag_01420.txt",
        help="Path to the reference station's produkt file (from scripts/fetch_stations.py)",
    )
    args = parser.parse_args()

    registry = build_registry(Path(args.urban), Path(args.reference))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n")
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
