from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .generator import (
    ConfigError,
    generate_receipts_from_config,
    load_json,
    validate_config,
)
from .sheet import build_config_from_mapping, is_mapping, preview_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate receipt PDFs from a receipt JSON file, or from a "
            "spreadsheet described by a mapping JSON file."
        )
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Receipt JSON, or spreadsheet mapping JSON (one with a \"source\" key)",
    )
    parser.add_argument(
        "--source",
        help=(
            "Mapping JSON only: read this CSV/XLSX file or Google Sheets URL "
            "instead of the source written in the mapping"
        ),
    )
    parser.add_argument(
        "--worksheet",
        help="Mapping JSON only: worksheet name to read (XLSX or Google Sheets)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the receipts that would be generated without writing PDFs",
    )
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
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config_path = args.config.expanduser().resolve()
        data = load_json(config_path)
        if is_mapping(data):
            result = build_config_from_mapping(
                config_path, source_override=args.source, worksheet=args.worksheet
            )
            config, base_dir = result.config, result.base_dir
            for note in result.skipped:
                print(f"Skipped {note}", file=sys.stderr)
        else:
            if args.source or args.worksheet:
                parser.error("--source and --worksheet need a mapping JSON.")
            validate_config(data)
            config, base_dir = data, config_path.parent

        if args.dry_run:
            _print_preview(config)
            return 0

        output_files = generate_receipts_from_config(
            config,
            base_dir=base_dir,
            output_root=args.output_dir,
            timestamped=not args.no_timestamp,
            show_progress=True,
        )
    except (ConfigError, OSError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Generated {len(output_files)} receipt(s):")
    for output_file in output_files:
        print(output_file)
    return 0


def _print_preview(config: dict) -> None:
    rows = preview_rows(config)
    for row in rows:
        source_row = f'row {row["row"]}: ' if row["row"] is not None else ""
        print(
            f'{source_row}{row["name"]}  {row["issue_date"]}  '
            f'¥{row["total"]:,}  [{row["items"]}]'
        )
    total = sum(row["total"] for row in rows)
    print(f"{len(rows)} receipt(s), total ¥{total:,} (dry run, no PDFs written)")
