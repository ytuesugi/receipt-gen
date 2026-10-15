import json
import tempfile
import unittest
from pathlib import Path

from receipt_gen.generator import ConfigError, load_config, render_receipt_html


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "issuer": {
                "name": "テスト事務局",
                "email": "test@example.com",
                "stamp_file": None,
            },
            "receipts": [
                {
                    "file_id": "test-001",
                    "name": "テスト 太郎 様",
                    "issue_date": "2026-07-11",
                    "amount_note": "但し、参加費として領収しました。",
                    "remarks": ["テスト用です。"],
                    "items": [
                        {"name": "参加費", "quantity": 2, "unit_price": 1500}
                    ],
                }
            ],
        }

    def test_renders_date_and_calculated_total(self):
        receipt = self.config["receipts"][0]

        html = render_receipt_html(receipt, self.config["issuer"])

        self.assertIn("2026年07月11日", html)
        self.assertIn("金額 ¥3,000-", html)
        self.assertNotIn('class="stamp"', html)

    def test_load_config_rejects_unsafe_file_id(self):
        self.config["receipts"][0]["file_id"] = "../private"

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                json.dumps(self.config, ensure_ascii=False), encoding="utf-8"
            )

            with self.assertRaisesRegex(ConfigError, "file_id"):
                load_config(config_path)

    def test_load_config_rejects_invalid_date(self):
        self.config["receipts"][0]["issue_date"] = "2026/07/11"

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                json.dumps(self.config, ensure_ascii=False), encoding="utf-8"
            )

            with self.assertRaisesRegex(ConfigError, "YYYY-MM-DD"):
                load_config(config_path)


if __name__ == "__main__":
    unittest.main()
