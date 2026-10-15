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
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
DEFAULT_AMOUNT_NOTE = "但し、研究会参加費として上記正に領収いたしました。"
TAX_LABELS = {
    "taxable": "課税",
    "reduced_taxable": "課税（軽減税率）",
    "non_taxable": "非課税",
    "out_of_scope": "不課税",
    "exempt": "免税",
}
TAX_FIELDS = ("tax_category", "tax_rate", "tax_amount")
FONT_FILE = Path(__file__).with_name("fonts") / "NotoSansJP-Variable.ttf"


class ConfigError(ValueError):
    """Raised when the receipt configuration is invalid."""


def load_config(config_path: Path) -> dict[str, Any]:
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ConfigError(f"Configuration file not found: {config_path}") from error
    except json.JSONDecodeError as error:
        raise ConfigError(
            f"Invalid JSON near line {error.lineno}: {error.msg}"
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
    stamp_data_uri = _load_stamp(
        config["issuer"].get("stamp_file"), config_path.parent
    )

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
            "Could not load WeasyPrint. See the setup instructions in README.md."
        ) from error

    reserved_file_ids = {
        receipt["file_id"]
        for receipt in config["receipts"]
        if receipt.get("file_id") is not None
    }
    used_file_ids: set[str] = set()
    output_files: list[Path] = []
    for index, receipt in enumerate(config["receipts"], start=1):
        html = render_receipt_html(receipt, config["issuer"], stamp_data_uri)
        file_id = receipt.get("file_id") or _automatic_file_id(receipt, index)
        if receipt.get("file_id") is None:
            file_id = _unique_file_id(file_id, used_file_ids | reserved_file_ids)
        used_file_ids.add(file_id)
        output_file = output_dir / f"{file_id}.pdf"
        HTML(string=html, base_url=str(config_path.parent)).write_pdf(output_file)
        output_files.append(output_file.resolve())

    return output_files


def _automatic_file_id(receipt: dict[str, Any], index: int) -> str:
    recipient = re.sub(r"(?:様|御中)\s*$", "", receipt["name"].strip())
    recipient = re.sub(r"\s+", "", recipient)
    recipient = INVALID_FILENAME_CHARS.sub("-", recipient).strip(" .-_")
    if not recipient:
        recipient = f"receipt-{index:03d}"
    return f'{receipt["issue_date"]}_{recipient}'


def _unique_file_id(file_id: str, unavailable: set[str]) -> str:
    candidate = file_id
    suffix = 2
    while candidate in unavailable:
        candidate = f"{file_id}-{suffix}"
        suffix += 1
    return candidate


def render_receipt_html(
    receipt: dict[str, Any],
    issuer: dict[str, Any],
    stamp_data_uri: str | None = None,
) -> str:
    items = [_prepare_item(item) for item in receipt["items"]]
    total = sum(item["quantity"] * item["unit_price"] for item in items)
    show_tax = any(
        any(item.get(field) is not None for field in TAX_FIELDS) for item in items
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
        items=items,
        total=total,
        issue_date=datetime.strptime(receipt["issue_date"], "%Y-%m-%d").strftime(
            "%Y年%m月%d日"
        ),
        amount_note=receipt.get("amount_note", DEFAULT_AMOUNT_NOTE),
        remarks=receipt.get("remarks", []),
        show_tax=show_tax,
        tax_summaries=_build_tax_summaries(items) if show_tax else [],
        stamp_data_uri=stamp_data_uri,
        font_uri=FONT_FILE.resolve().as_uri(),
    )


def _prepare_item(item: dict[str, Any]) -> dict[str, Any]:
    prepared = {**item, "quantity": item.get("quantity", 1)}
    category = item.get("tax_category")
    rate = item.get("tax_rate")
    label = TAX_LABELS.get(category, "")
    if label and rate is not None:
        label = f"{label} {rate:g}%"
    prepared["tax_label"] = label
    return prepared


def _build_tax_summaries(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str | None, float | None], dict[str, Any]] = {}
    for item in items:
        category = item.get("tax_category")
        rate = item.get("tax_rate")
        if category is None and rate is None and item.get("tax_amount") is None:
            continue

        key = (category, rate)
        entry = grouped.setdefault(
            key,
            {
                "label": item["tax_label"] or "税区分未設定",
                "amount": 0,
                "tax_amount": 0,
                "tax_amount_complete": True,
            },
        )
        entry["amount"] += item["quantity"] * item["unit_price"]
        if item.get("tax_amount") is None:
            entry["tax_amount_complete"] = False
        else:
            entry["tax_amount"] += item["tax_amount"]

    summaries = []
    for entry in grouped.values():
        if not entry.pop("tax_amount_complete"):
            entry["tax_amount"] = None
        summaries.append(entry)
    return summaries


def _load_stamp(stamp_file: str | None, config_dir: Path) -> str | None:
    if not stamp_file:
        return None

    stamp_path = (config_dir / stamp_file).resolve()
    try:
        stamp_bytes = stamp_path.read_bytes()
    except FileNotFoundError as error:
        raise ConfigError(f"Stamp image not found: {stamp_path}") from error

    mime_type, _ = mimetypes.guess_type(stamp_path.name)
    if mime_type not in {"image/png", "image/jpeg"}:
        raise ConfigError("The stamp image must be a PNG or JPEG file.")

    encoded = base64.b64encode(stamp_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _validate_config(config: Any) -> None:
    if not isinstance(config, dict):
        raise ConfigError("The configuration root must be an object.")

    issuer = config.get("issuer")
    if not isinstance(issuer, dict) or not _is_nonempty_string(issuer.get("name")):
        raise ConfigError("issuer.name is required.")
    for field in ("email", "invoice_registration_number"):
        if issuer.get(field) is not None and not _is_nonempty_string(issuer[field]):
            raise ConfigError(f"issuer.{field} must be a non-empty string or null.")
    if issuer.get("stamp_file") is not None and not _is_nonempty_string(
        issuer.get("stamp_file")
    ):
        raise ConfigError("issuer.stamp_file must be a file path or null.")

    receipts = config.get("receipts")
    if not isinstance(receipts, list) or not receipts:
        raise ConfigError("receipts must contain at least one receipt.")

    seen_file_ids: set[str] = set()
    for index, receipt in enumerate(receipts, start=1):
        _validate_receipt(receipt, index)
        file_id = receipt.get("file_id")
        if file_id is not None:
            if file_id in seen_file_ids:
                raise ConfigError(f"Duplicate file_id in receipts[{index}]: {file_id}")
            seen_file_ids.add(file_id)


def _validate_receipt(receipt: Any, index: int) -> None:
    label = f"receipts[{index}]"
    if not isinstance(receipt, dict):
        raise ConfigError(f"{label} must be an object.")

    for field in ("name", "issue_date"):
        if not _is_nonempty_string(receipt.get(field)):
            raise ConfigError(f"{label}.{field} is required.")

    file_id = receipt.get("file_id")
    if file_id is not None and not _is_nonempty_string(file_id):
        raise ConfigError(f"{label}.file_id must be a non-empty string or null.")
    if file_id is not None and not FILE_ID_PATTERN.fullmatch(file_id):
        raise ConfigError(
            f"{label}.file_id must start with a letter or number and contain only "
            "letters, numbers, periods, underscores, or hyphens."
        )

    try:
        datetime.strptime(receipt["issue_date"], "%Y-%m-%d")
    except ValueError as error:
        raise ConfigError(f"{label}.issue_date must use YYYY-MM-DD format.") from error

    if "amount_note" in receipt and not _is_nonempty_string(receipt["amount_note"]):
        raise ConfigError(f"{label}.amount_note must be a non-empty string.")

    remarks = receipt.get("remarks", [])
    if not isinstance(remarks, list) or not all(
        isinstance(remark, str) for remark in remarks
    ):
        raise ConfigError(f"{label}.remarks must be an array of strings.")

    items = receipt.get("items")
    if not isinstance(items, list) or not items:
        raise ConfigError(f"{label}.items must contain at least one item.")

    for item_index, item in enumerate(items, start=1):
        _validate_item(item, f"{label}.items[{item_index}]")


def _validate_item(item: Any, label: str) -> None:
    if not isinstance(item, dict) or not _is_nonempty_string(item.get("name")):
        raise ConfigError(f"{label}.name is required.")
    if "quantity" in item and not _is_positive_integer(item["quantity"]):
        raise ConfigError(f"{label}.quantity must be a positive integer.")
    if not _is_nonnegative_integer(item.get("unit_price")):
        raise ConfigError(f"{label}.unit_price must be a non-negative integer.")

    category = item.get("tax_category")
    if category is not None and category not in TAX_LABELS:
        choices = ", ".join(TAX_LABELS)
        raise ConfigError(f"{label}.tax_category must be one of: {choices}, or null.")

    rate = item.get("tax_rate")
    if rate is not None and (
        isinstance(rate, bool) or not isinstance(rate, (int, float)) or not 0 <= rate <= 100
    ):
        raise ConfigError(f"{label}.tax_rate must be between 0 and 100, or null.")

    tax_amount = item.get("tax_amount")
    if tax_amount is not None and not _is_nonnegative_integer(tax_amount):
        raise ConfigError(f"{label}.tax_amount must be a non-negative integer or null.")
    if (rate is not None or tax_amount is not None) and category is None:
        raise ConfigError(f"{label}.tax_category is required when tax details are set.")


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_positive_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _is_nonnegative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0
