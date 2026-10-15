import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from receipt_gen.generator import ConfigError, generate_receipts, load_config, render_receipt_html


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "issuer": {"name": "テスト研究会", "stamp_file": None},
            "receipts": [
                {
                    "file_id": None,
                    "name": "テスト 太郎 様",
                    "issue_date": "2026-07-11",
                    "items": [{"name": "研究会参加費", "unit_price": 3000}],
                }
            ],
        }

    def test_hides_tax_fields_when_all_are_null(self):
        self.config["issuer"]["invoice_registration_number"] = None
        self.config["receipts"][0]["items"][0].update(
            {"tax_category": None, "tax_rate": None, "tax_amount": None}
        )
        html = render_receipt_html(
            self.config["receipts"][0], self.config["issuer"]
        )

        self.assertNotIn("税区分</th>", html)
        self.assertNotIn('<div class="tax-summary">', html)
        self.assertNotIn("登録番号", html)

    def test_shows_tax_fields_when_configured(self):
        self.config["issuer"]["invoice_registration_number"] = "T1234567890123"
        item = self.config["receipts"][0]["items"][0]
        item.update(
            {"tax_category": "taxable", "tax_rate": 10, "tax_amount": 273}
        )

        html = render_receipt_html(
            self.config["receipts"][0], self.config["issuer"]
        )

        self.assertIn("税区分</th>", html)
        self.assertIn("課税 10%", html)
        self.assertIn("消費税額 ¥273", html)
        self.assertIn("T1234567890123", html)

    def test_shows_remarks_when_configured(self):
        self.config["receipts"][0]["remarks"] = [
            "参加費の内訳を個別に区分することはできません。",
            "本会は適格請求書発行事業者ではありません。",
        ]

        html = render_receipt_html(
            self.config["receipts"][0], self.config["issuer"]
        )

        self.assertIn('<div class="remarks">', html)
        self.assertIn("参加費の内訳を個別に区分することはできません。", html)
        self.assertIn("本会は適格請求書発行事業者ではありません。", html)

    def test_shows_custom_amount_note(self):
        self.config["receipts"][0]["amount_note"] = (
            "但し、研究会参加費及び資料代として上記正に領収いたしました。"
        )

        html = render_receipt_html(
            self.config["receipts"][0], self.config["issuer"]
        )

        self.assertIn("研究会参加費及び資料代として", html)

    def test_generates_pdf_with_minimum_configuration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "config.json"
            config_path.write_text(
                json.dumps(self.config, ensure_ascii=False), encoding="utf-8"
            )

            output_files = generate_receipts(
                config_path, temp_path / "output", timestamped=False
            )

            self.assertEqual(len(output_files), 1)
            self.assertEqual(output_files[0].name, "2026-07-11_テスト太郎.pdf")
            self.assertTrue(output_files[0].read_bytes().startswith(b"%PDF"))

    def test_automatic_file_ids_are_unique(self):
        self.config["receipts"].append(dict(self.config["receipts"][0]))

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "config.json"
            config_path.write_text(
                json.dumps(self.config, ensure_ascii=False), encoding="utf-8"
            )

            output_files = generate_receipts(
                config_path, temp_path / "output", timestamped=False
            )

            self.assertEqual(
                [output_file.name for output_file in output_files],
                ["2026-07-11_テスト太郎.pdf", "2026-07-11_テスト太郎-2.pdf"],
            )

    def test_load_config_rejects_invalid_tax_category(self):
        self.config["receipts"][0]["items"][0]["tax_category"] = "unknown"

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                json.dumps(self.config, ensure_ascii=False), encoding="utf-8"
            )

            with self.assertRaisesRegex(ConfigError, "tax_category"):
                load_config(config_path)

    def test_load_config_rejects_unsafe_file_id(self):
        self.config["receipts"][0]["file_id"] = "../private"

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                json.dumps(self.config, ensure_ascii=False), encoding="utf-8"
            )

            with self.assertRaisesRegex(ConfigError, "file_id"):
                load_config(config_path)


if __name__ == "__main__":
    unittest.main()
