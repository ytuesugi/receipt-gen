# JSON

サンプルをコピーし、領収書の内容を編集します。

```bash
cp input/example.json input/receipts.json
python generate.py input/receipts.json
```

Windows では `Copy-Item input\example.json input\receipts.json` を使用します。`input/` 内のサンプル以外は Git 管理から除外されます。

## Fields

### `issuer`

| キー | 必須 | 内容 |
| --- | --- | --- |
| `name` | ○ | 発行者名 |
| `email` |  | メールアドレス。`null` で非表示 |
| `invoice_registration_number` |  | 適格請求書発行事業者の登録番号。`null` で非表示 |
| `stamp_file` |  | 印影画像の相対パス。`null` で非表示 |
| `tax_rounding` |  | 税額計算の端数処理。`floor` / `round` / `ceil` |

### `receipts[]`

| キー | 必須 | 内容 |
| --- | --- | --- |
| `name` | ○ | 宛名 |
| `issue_date` | ○ | 発行日（`YYYY-MM-DD`） |
| `file_id` |  | PDF 名。`null` なら発行日と宛名から自動生成 |
| `amount_note` |  | 但し書き |
| `remarks` |  | 備考の配列 |
| `items` | ○ | 明細の配列 |

### `items[]`

| キー | 必須 | 内容 |
| --- | --- | --- |
| `name` | ○ | 項目名 |
| `quantity` |  | 数量。省略時は `1` |
| `unit_price` | ○ | 税込単価（円） |
| `tax_category` |  | 税区分 |
| `tax_rate` |  | 税率（%） |
| `tax_amount` |  | 消費税額。`null` なら自動計算 |

税関連項目をすべて `null` または省略すると、税欄は表示されません。詳細は [`tax.md`](tax.md) を参照してください。
