from __future__ import annotations

import base64
import json
import mimetypes
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape


FILE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class ConfigError(ValueError):
    """Raised when the receipt configuration is invalid."""


def load_config(config_path: Path) -> dict[str, Any]:
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ConfigError(f"設定ファイルが見つかりません: {config_path}") from error
    except json.JSONDecodeError as error:
        raise ConfigError(
            f"設定 JSON の {error.lineno} 行目付近を確認してください: {error.msg}"
        ) from error

    _validate_config(config)
    return config


def generate_receipts(
    config_path: Path,
    output_root: Path = Path("output"),
    timestamped: bool = True,
) -> list[Path]:
    config_path = config_path.expanduser().resolve()
    config = load_config(config_path)
    issuer = config["issuer"]
    stamp_data_uri = _load_stamp(issuer.get("stamp_file"), config_path.parent)

    output_root = output_root.expanduser()
    output_dir = (
        output_root / datetime.now().strftime("%Y%m%dT%H%M%S")
        if timestamped
        else output_root
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from weasyprint import HTML
    except (ImportError, OSError) as error:
        raise RuntimeError(
            "WeasyPrint を読み込めません。README のセットアップ手順を確認してください。"
        ) from error

    output_files: list[Path] = []
    for receipt in config["receipts"]:
        html = render_receipt_html(receipt, issuer, stamp_data_uri)
        output_file = output_dir / f'{receipt["file_id"]}.pdf'
        HTML(string=html, base_url=str(config_path.parent)).write_pdf(output_file)
        output_files.append(output_file.resolve())

    return output_files


def render_receipt_html(
    receipt: dict[str, Any],
    issuer: dict[str, Any],
    stamp_data_uri: str | None = None,
) -> str:
    issue_date = datetime.strptime(receipt["issue_date"], "%Y-%m-%d").strftime(
        "%Y年%m月%d日"
    )
    total = sum(
        item["quantity"] * item["unit_price"] for item in receipt["items"]
    )

    environment = Environment(
        loader=PackageLoader("receipt_gen", "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    environment.filters["yen"] = lambda value: f"{value:,}"
    template = environment.get_template("receipt.html")
    return template.render(
        receipt=receipt,
        issuer=issuer,
        issue_date=issue_date,
        total=total,
        stamp_data_uri=stamp_data_uri,
    )


def _load_stamp(stamp_file: str | None, config_dir: Path) -> str | None:
    if not stamp_file:
        return None

    stamp_path = (config_dir / stamp_file).resolve()
    try:
        stamp_bytes = stamp_path.read_bytes()
    except FileNotFoundError as error:
        raise ConfigError(f"印影画像が見つかりません: {stamp_path}") from error

    mime_type, _ = mimetypes.guess_type(stamp_path.name)
    if mime_type not in {"image/png", "image/jpeg"}:
        raise ConfigError("印影画像は PNG または JPEG を指定してください。")

    encoded = base64.b64encode(stamp_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _validate_config(config: Any) -> None:
    if not isinstance(config, dict):
        raise ConfigError("設定ファイルの最上位はオブジェクトにしてください。")

    issuer = config.get("issuer")
    if not isinstance(issuer, dict) or not _is_nonempty_string(issuer.get("name")):
        raise ConfigError("issuer.name を入力してください。")
    if "email" in issuer and not isinstance(issuer["email"], str):
        raise ConfigError("issuer.email は文字列にしてください。")
    if issuer.get("stamp_file") is not None and not _is_nonempty_string(
        issuer.get("stamp_file")
    ):
        raise ConfigError("issuer.stamp_file はファイルパスまたは null にしてください。")

    receipts = config.get("receipts")
    if not isinstance(receipts, list) or not receipts:
        raise ConfigError("receipts に 1 件以上の領収書を設定してください。")

    seen_file_ids: set[str] = set()
    for index, receipt in enumerate(receipts, start=1):
        _validate_receipt(receipt, index)
        file_id = receipt["file_id"]
        if file_id in seen_file_ids:
            raise ConfigError(f"receipts[{index}] の file_id が重複しています: {file_id}")
        seen_file_ids.add(file_id)


def _validate_receipt(receipt: Any, index: int) -> None:
    label = f"receipts[{index}]"
    if not isinstance(receipt, dict):
        raise ConfigError(f"{label} はオブジェクトにしてください。")

    for field in ("file_id", "name", "issue_date", "amount_note"):
        if not _is_nonempty_string(receipt.get(field)):
            raise ConfigError(f"{label}.{field} を入力してください。")

    if not FILE_ID_PATTERN.fullmatch(receipt["file_id"]):
        raise ConfigError(
            f"{label}.file_id は英数字で始め、英数字・ピリオド・_・- のみ使用してください。"
        )

    try:
        datetime.strptime(receipt["issue_date"], "%Y-%m-%d")
    except ValueError as error:
        raise ConfigError(f"{label}.issue_date は YYYY-MM-DD 形式にしてください。") from error

    remarks = receipt.get("remarks", [])
    if not isinstance(remarks, list) or not all(
        isinstance(remark, str) for remark in remarks
    ):
        raise ConfigError(f"{label}.remarks は文字列の配列にしてください。")

    items = receipt.get("items")
    if not isinstance(items, list) or not items:
        raise ConfigError(f"{label}.items に 1 件以上の項目を設定してください。")

    for item_index, item in enumerate(items, start=1):
        item_label = f"{label}.items[{item_index}]"
        if not isinstance(item, dict) or not _is_nonempty_string(item.get("name")):
            raise ConfigError(f"{item_label}.name を入力してください。")
        if not _is_positive_integer(item.get("quantity")):
            raise ConfigError(f"{item_label}.quantity は 1 以上の整数にしてください。")
        if not _is_nonnegative_integer(item.get("unit_price")):
            raise ConfigError(f"{item_label}.unit_price は 0 以上の整数にしてください。")


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_positive_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _is_nonnegative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0
