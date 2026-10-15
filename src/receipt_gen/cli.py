from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .generator import ConfigError, generate_receipts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate receipt PDFs from a JSON configuration file."
    )
    parser.add_argument("config", type=Path, help="Path to the JSON configuration file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Parent output directory (default: output)",
    )
    parser.add_argument(
        "--no-timestamp",
        action="store_true",
        help="Write directly to the output directory",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        output_files = generate_receipts(
            config_path=args.config,
            output_root=args.output_dir,
            timestamped=not args.no_timestamp,
        )
    except (ConfigError, OSError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Generated {len(output_files)} receipt(s):")
    for output_file in output_files:
        print(output_file)
    return 0
