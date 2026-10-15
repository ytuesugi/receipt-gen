import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from receipt_gen.cli import main
from receipt_gen.generator import ConfigError, generate_receipts_from_config
from receipt_gen.sheet import (
    Table,
    build_config,
    build_config_from_mapping,
    is_mapping,
    preview_rows,
    validate_mapping,
)


MAPPING = {
    "issuer": {"name": "テスト研究会", "stamp_file": None},
    "source": {"type": "csv", "path": "participants.csv"},
    "receipt": {
        "name": {"column": "氏名", "suffix": " 様"},
        "issue_date": "2026-07-11",
    },
    "items": [
        {"name": "参加費（一般）", "quantity": {"column": "一般"}, "unit_price": 31000},
        {"name": "参加費（学生）", "quantity": {"column": "学生"}, "unit_price": 20000},
        {
            "name": "懇親会費",
            "quantity": {"column": "懇親会"},
            "unit_price": {"column": "懇親会費"},
        },
    ],
}
HEADERS = ["氏名", "一般", "学生", "懇親会", "懇親会費"]


def table(*rows):
    return Table(
        headers=list(HEADERS),
        rows=[(number, list(row)) for number, row in enumerate(rows, start=2)],
    )


class BuildConfigTests(unittest.TestCase):
    def setUp(self):
        self.mapping = copy.deepcopy(MAPPING)

    def test_each_row_becomes_one_receipt_and_zero_quantities_are_omitted(self):
        config, skipped = build_config(
            self.mapping,
            table(
                ["テスト 太郎", "1", "0", "1", "5000"],
                ["サンプル 花子", "0", "1", "0", "3000"],
            ),
        )

        self.assertEqual(skipped, [])
        first, second = config["receipts"]
        self.assertEqual(first["name"], "テスト 太郎 様")
        self.assertEqual(
            [(item["name"], item["quantity"], item["unit_price"]) for item in first["items"]],
            [("参加費（一般）", 1, 31000), ("懇親会費", 1, 5000)],
        )
        self.assertEqual([item["name"] for item in second["items"]], ["参加費（学生）"])
        self.assertEqual(
            [row["total"] for row in preview_rows(config)], [36000, 20000]
        )

    def test_parses_spreadsheet_style_values(self):
        self.mapping["receipt"]["issue_date"] = {"column": "発行日"}
        rows = Table(
            headers=HEADERS + ["発行日"],
            rows=[
                (2, ["Ａ 様", "１", "", "TRUE", "¥5,000", "2026/07/11"]),
                (3, ["B", 1.0, None, False, 5000.0, datetime(2026, 7, 12, 9, 30)]),
            ],
        )

        config, _ = build_config(self.mapping, rows)

        first, second = config["receipts"]
        self.assertEqual(first["name"], "Ａ 様")
        self.assertEqual(first["issue_date"], "2026-07-11")
        self.assertEqual(first["items"][1]["unit_price"], 5000)
        self.assertEqual(second["issue_date"], "2026-07-12")
        self.assertEqual([item["name"] for item in second["items"]], ["参加費（一般）"])

    def test_header_names_are_matched_after_normalization(self):
        rows = Table(
            headers=["氏名", "一般", "学生", "懇親会", "懇親会費"],
            rows=[(2, ["A", "1", "0", "0", "0"])],
        )
        self.mapping["items"][0]["quantity"] = {"column": " 一般 "}

        config, _ = build_config(self.mapping, rows)

        self.assertEqual(len(config["receipts"]), 1)

    def test_skips_blank_rows_and_rows_without_items(self):
        config, skipped = build_config(
            self.mapping,
            table(
                ["A", "1", "0", "0", "5000"],
                ["", "", "", "", ""],
                ["B", "0", "0", "0", "5000"],
            ),
        )

        self.assertEqual(len(config["receipts"]), 1)
        self.assertEqual(len(skipped), 1)
        self.assertIn("row 4 (B 様)", skipped[0])

    def test_include_if_filters_rows(self):
        self.mapping["include_if"] = {"column": "入金", "in": ["済", "TRUE"]}
        rows = Table(
            headers=HEADERS + ["入金"],
            rows=[
                (2, ["A", "1", "0", "0", "0", "済"]),
                (3, ["B", "1", "0", "0", "0", ""]),
                (4, ["C", "1", "0", "0", "0", True]),
            ],
        )

        config, skipped = build_config(self.mapping, rows)

        self.assertEqual([r["name"] for r in config["receipts"]], ["A 様", "C 様"])
        self.assertIn("row 3", skipped[0])

    def test_tax_fields_from_literals_and_columns(self):
        self.mapping["items"] = [
            {
                "name": "参加費",
                "quantity": {"column": "一般"},
                "unit_price": 11000,
                "tax_category": {"column": "税区分"},
                "tax_rate": 10,
                "tax_amount": {"column": "税額"},
            }
        ]
        rows = Table(
            headers=HEADERS + ["税区分", "税額"],
            rows=[(2, ["A", "1", "", "", "", "課税", "1,000"])],
        )

        config, _ = build_config(self.mapping, rows)

        item = config["receipts"][0]["items"][0]
        self.assertEqual(item["tax_category"], "taxable")
        self.assertEqual(item["tax_rate"], 10)
        self.assertEqual(item["tax_amount"], 1000)

    def test_reports_row_and_column_for_bad_values(self):
        with self.assertRaisesRegex(ConfigError, r'row 3, .*column "一般".*1\.5'):
            build_config(
                self.mapping,
                table(["A", "1", "0", "0", "0"], ["B", "1.5", "0", "0", "0"]),
            )

    def test_rejects_missing_column_before_reading_rows(self):
        self.mapping["items"][0]["quantity"] = {"column": "一般参加"}

        with self.assertRaisesRegex(ConfigError, '"一般参加" not found. Available: 氏名'):
            build_config(self.mapping, table(["A", "1", "0", "0", "0"]))

    def test_rejects_blank_name_with_items(self):
        with self.assertRaisesRegex(ConfigError, "row 2: name is blank"):
            build_config(self.mapping, table(["", "1", "0", "0", "0"]))

    def test_rejects_blank_unit_price_when_item_is_used(self):
        with self.assertRaisesRegex(ConfigError, "unit_price is blank"):
            build_config(self.mapping, table(["A", "0", "0", "1", ""]))

    def test_rejects_when_no_receipts_remain(self):
        with self.assertRaisesRegex(ConfigError, "No receipts to generate"):
            build_config(self.mapping, table(["A", "0", "0", "0", "0"]))


class MappingValidationTests(unittest.TestCase):
    def test_rejects_unknown_keys_to_catch_typos(self):
        mapping = copy.deepcopy(MAPPING)
        mapping["items"][0]["unit_prise"] = 100

        with self.assertRaisesRegex(ConfigError, "unit_prise"):
            validate_mapping(mapping)

    def test_requires_url_for_google_sheets(self):
        mapping = copy.deepcopy(MAPPING)
        mapping["source"] = {"type": "google_sheets"}

        with self.assertRaisesRegex(ConfigError, "source.url"):
            validate_mapping(mapping)

    def test_is_mapping(self):
        self.assertTrue(is_mapping(MAPPING))
        self.assertFalse(is_mapping({"issuer": {}, "receipts": []}))


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name)
        self.mapping_path = self.path / "mapping.json"
        self.mapping_path.write_text(json.dumps(MAPPING, ensure_ascii=False), encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_csv(self, name="participants.csv", encoding="utf-8-sig"):
        csv_path = self.path / name
        csv_path.write_text(
            "氏名,一般,学生,懇親会,懇親会費\nテスト 太郎,1,0,1,5000\n", encoding=encoding
        )
        return csv_path

    def test_reads_csv_relative_to_mapping(self):
        self.write_csv()

        result = build_config_from_mapping(self.mapping_path)

        self.assertEqual(result.config["receipts"][0]["name"], "テスト 太郎 様")
        self.assertEqual(result.base_dir, self.path.resolve())

    def test_reads_xlsx_with_header_row_and_worksheet(self):
        from openpyxl import Workbook

        workbook = Workbook()
        workbook.active.title = "表紙"
        sheet = workbook.create_sheet("参加者")
        sheet.append(["第1回テスト研究会 参加者一覧"])
        sheet.append(HEADERS)
        sheet.append(["テスト 太郎", 1, 0, 1, 5000])
        xlsx_path = self.path / "participants.xlsx"
        workbook.save(xlsx_path)

        result = build_config_from_mapping(
            self.mapping_path,
            source_override={"type": "xlsx", "path": "participants.xlsx", "header_row": 2},
            worksheet="参加者",
        )

        receipt = result.config["receipts"][0]
        self.assertEqual(receipt["_source_row"], 3)
        self.assertEqual(receipt["items"][1]["unit_price"], 5000)

    def test_source_override_path_detects_type(self):
        csv_path = self.write_csv("other.csv")

        result = build_config_from_mapping(self.mapping_path, source_override=str(csv_path))

        self.assertEqual(len(result.config["receipts"]), 1)

    def test_reads_google_sheets_through_given_client(self):
        opened = {}

        class FakeWorksheet:
            def get_all_values(self):
                return [HEADERS, ["テスト 太郎", "1", "0", "TRUE", "¥5,000"]]

        class FakeSpreadsheet:
            def worksheet(self, name):
                opened["worksheet"] = name
                return FakeWorksheet()

        class FakeClient:
            def open_by_url(self, url):
                opened["url"] = url
                return FakeSpreadsheet()

        url = "https://docs.google.com/spreadsheets/d/abc/edit"
        result = build_config_from_mapping(
            self.mapping_path,
            source_override=url,
            worksheet="フォームの回答 1",
            gspread_client=FakeClient(),
        )

        self.assertEqual(opened, {"url": url, "worksheet": "フォームの回答 1"})
        self.assertEqual(result.config["receipts"][0]["items"][1]["unit_price"], 5000)

    def test_cli_rejects_google_spreadsheet_url(self):
        with self.assertRaises(SystemExit):
            main(
                [
                    str(self.mapping_path),
                    "--source",
                    "https://docs.google.com/spreadsheets/d/abc/edit",
                    "--dry-run",
                ]
            )

    def test_generates_pdf_from_csv(self):
        self.write_csv()
        result = build_config_from_mapping(self.mapping_path)

        output_files = generate_receipts_from_config(
            result.config, result.base_dir, self.path / "output", timestamped=False
        )

        self.assertEqual([path.name for path in output_files], ["2026-07-11_テスト太郎.pdf"])
        self.assertTrue(output_files[0].read_bytes().startswith(b"%PDF"))

    def test_cli_dry_run_writes_nothing(self):
        self.write_csv()
        output_dir = self.path / "output"

        exit_code = main(
            [str(self.mapping_path), "--dry-run", "--output-dir", str(output_dir)]
        )

        self.assertEqual(exit_code, 0)
        self.assertFalse(output_dir.exists())


if __name__ == "__main__":
    unittest.main()
