"""Command-line entry point for Climate Twin Frankfurt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from climate_twin_frankfurt.registry import build_registry


def _cmd_summarize(args: argparse.Namespace) -> int:
    registry = build_registry(Path(args.urban), Path(args.reference))
    period = registry["period"]
    gap = registry["gap"]["full_period"]
    trend = registry["trend"]
    print(
        f"{period['n_valid_paired_days']} valid paired days, "
        f"{period['start_date']} to {period['end_date']}"
    )
    print(
        f"Mean urban-reference gap: {gap['mean_gap_c']:.3f} C "
        f"(95% CI [{gap['ci_95_low']:.3f}, {gap['ci_95_high']:.3f}])"
    )
    if trend["slope_c_per_year"] is None:
        print(f"Trend: {trend['label']}")
    else:
        print(
            f"Trend: {trend['slope_c_per_year']:.4f} C/year "
            f"(95% CI [{trend['ci_95_low']:.4f}, {trend['ci_95_high']:.4f}], "
            f"p={trend['p_value']:.4g}, significant={trend['significant']})"
        )
    return 0


def _cmd_registry(args: argparse.Namespace) -> int:
    registry = build_registry(Path(args.urban), Path(args.reference))
    text = json.dumps(registry, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        sys.stdout.write(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="climate-twin-frankfurt", description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    summarize = subparsers.add_parser("summarize", help="Print a short summary of the gap/trend")
    summarize.add_argument(
        "--urban", required=True, help="Path to the urban station's produkt file"
    )
    summarize.add_argument(
        "--reference", required=True, help="Path to the reference station's produkt file"
    )
    summarize.set_defaults(func=_cmd_summarize)

    registry = subparsers.add_parser("registry", help="Build and print the full result registry")
    registry.add_argument("--urban", required=True, help="Path to the urban station's produkt file")
    registry.add_argument(
        "--reference", required=True, help="Path to the reference station's produkt file"
    )
    registry.add_argument("--output", help="Write JSON to this path instead of stdout")
    registry.set_defaults(func=_cmd_registry)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result: int = args.func(args)
    return result


if __name__ == "__main__":
    sys.exit(main())
