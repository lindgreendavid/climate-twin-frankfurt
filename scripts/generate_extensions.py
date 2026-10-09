#!/usr/bin/env python3
"""Generate the POST-HOC extensions (other variables, relocation step checks)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from climate_twin_frankfurt.extensions import build_extensions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--urban", default="data/external/produkt_klima_tag_01424.txt")
    parser.add_argument("--reference", default="data/external/produkt_klima_tag_01420.txt")
    args = parser.parse_args()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    result = build_extensions(Path(args.urban), Path(args.reference))
    with out.open("w") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
