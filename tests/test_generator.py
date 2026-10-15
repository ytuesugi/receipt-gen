import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from receipt_gen.generator import (
    ConfigError,
    validate_config,
    compute_included_tax,
    generate_receipts,
    load_config,
    render_receipt_html,
)


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

    def test_computes_tax_once_per_rate_when_tax_amount_is_null(self):
        self.config["receipts"][0]["items"] = [
            {"name": "参加費", "unit_price": 31000, "tax_category": "taxable",
             "tax_rate": 10, "tax_amount": None},
            {"name": "資料代", "quantity": 2, "unit_price": 1000,
             "tax_category": "taxable", "tax_rate": 10},
            {"name": "弁当", "unit_price": 1080, "tax_category": "reduced_taxable",
             "tax_rate": 8, "tax_amount": None},
        ]

        html = render_receipt_html(self.config["receipts"][0], self.config["issuer"])

        # 33000 * 10 / 110 = 3000. Per-item rounding would give 2818 + 181.
        self.assertIn("課税 10% 対象額 ¥33,000", " ".join(html.split()))
        self.assertIn("消費税額 ¥3,000", html)
        self.assertIn("消費税額 ¥80", html)

    def test_uses_given_tax_amount(self):
        self.config["receipts"][0]["items"][0].update(
            {"tax_category": "taxable", "tax_rate": 10, "tax_amount": 273}
        )

        html = render_receipt_html(self.config["receipts"][0], self.config["issuer"])

        self.assertIn("消費税額 ¥273", html)

    def test_does_not_compute_tax_for_untaxed_categories(self):
        self.config["receipts"][0]["items"][0].update(
            {"tax_category": "non_taxable", "tax_rate": None, "tax_amount": None}
        )

        html = render_receipt_html(self.config["receipts"][0], self.config["issuer"])

        self.assertIn("非課税 対象額 ¥3,000", " ".join(html.split()))
        self.assertNotIn("消費税額", html)

    def test_tax_rounding_modes(self):
        # 1001 * 10 / 110 = 91.0
        self.assertEqual(compute_included_tax(1001, 10, "floor"), 91)
        # 1005 * 10 / 110 = 91.36..., 1012 * 10 / 110 = 92.0, 1007 * 10 / 110 = 91.54...
        self.assertEqual(compute_included_tax(1005, 10, "floor"), 91)
        self.assertEqual(compute_included_tax(1005, 10, "ceil"), 92)
        self.assertEqual(compute_included_tax(1005, 10, "round"), 91)
        self.assertEqual(compute_included_tax(1007, 10, "round"), 92)
        self.assertEqual(compute_included_tax(1080, 8, "floor"), 80)

    def test_issuer_tax_rounding_is_applied(self):
        self.config["issuer"]["tax_rounding"] = "ceil"
        self.config["receipts"][0]["items"][0].update(
            {"unit_price": 1005, "tax_category": "taxable", "tax_rate": 10}
        )

        html = render_receipt_html(self.config["receipts"][0], self.config["issuer"])

        self.assertIn("消費税額 ¥92", html)

    def test_rejects_unknown_tax_rounding(self):
        self.config["issuer"]["tax_rounding"] = "truncate"

        with self.assertRaisesRegex(ConfigError, "tax_rounding"):
            validate_config(self.config)

    def test_rejects_partly_given_tax_amounts_in_one_rate(self):
        self.config["receipts"][0]["items"] = [
            {"name": "A", "unit_price": 1100, "tax_category": "taxable",
             "tax_rate": 10, "tax_amount": 100},
            {"name": "B", "unit_price": 1100, "tax_category": "taxable",
             "tax_rate": 10, "tax_amount": None},
        ]

        with self.assertRaisesRegex(ConfigError, "all set tax_amount or all leave it null"):
            validate_config(self.config)

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
