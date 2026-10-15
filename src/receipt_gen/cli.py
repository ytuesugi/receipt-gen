from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .generator import ConfigError, generate_receipts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="JSON の設定から領収書 PDF を生成します。"
    )
    parser.add_argument("config", type=Path, help="設定 JSON ファイル")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="出力先の親フォルダ（既定: output）",
    )
    parser.add_argument(
        "--no-timestamp",
        action="store_true",
        help="出力先に日時フォルダを作成しない",
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
        print(f"エラー: {error}", file=sys.stderr)
        return 1

    print(f"{len(output_files)} 件の領収書を生成しました。")
    for output_file in output_files:
        print(output_file)
    return 0
