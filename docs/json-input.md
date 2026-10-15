# JSON 入力

領収書の内容をすべて JSON に書いて生成する方法です。サンプルをコピーして編集します。

```bash
cp input/example.json input/receipts.json
python generate.py input/receipts.json
```

Windows では `Copy-Item input\example.json input\receipts.json` を使います。

`input/` 内のサンプル以外のファイルは `.gitignore` で除外されます。

## 構成

```json
{
  "issuer": { ... },
  "receipts": [ { ..., "items": [ ... ] } ]
}
```

`_comment` は説明用で、PDF の生成には使われません。

### issuer（発行者）

| キー | 必須 | 内容 |
| --- | --- | --- |
| `name` | ○ | 発行者名（例：第1回テスト研究会） |
| `email` |  | 連絡先メールアドレス。`null` なら表示しません |
| `invoice_registration_number` |  | 適格請求書発行事業者の登録番号（`T` から始まる番号）。未登録なら `null` |
| `stamp_file` |  | 印影画像（PNG または JPEG）。JSON ファイルから見た相対パス。`null` なら印影なし |

### receipts[]（領収書 1 枚ごと）

| キー | 必須 | 内容 |
| --- | --- | --- |
| `name` | ○ | 宛名（例：`テスト 太郎 様`） |
| `issue_date` | ○ | 発行日。`YYYY-MM-DD` 形式 |
| `file_id` |  | 出力ファイル名（拡張子なし）。英数字・`.`・`_`・`-` のみ。`null` なら `発行日_宛名` から自動生成 |
| `amount_note` |  | 金額の下の但し書き。省略時は「但し、研究会参加費として上記正に領収いたしました。」 |
| `remarks` |  | 備考の文字列の配列 |
| `items` | ○ | 明細の配列（1 件以上） |

### items[]（明細）

| キー | 必須 | 内容 |
| --- | --- | --- |
| `name` | ○ | 項目名 |
| `quantity` |  | 数量（正の整数）。省略時は 1 |
| `unit_price` | ○ | 単価（円、0 以上の整数） |
| `tax_category` |  | `taxable`（課税）/ `reduced_taxable`（課税・軽減税率）/ `non_taxable`（非課税）/ `out_of_scope`（不課税）/ `exempt`（免税） |
| `tax_rate` |  | 税率（%） |
| `tax_amount` |  | この明細に含まれる消費税額（円） |

税関連の 3 項目をすべて `null` または省略すると、税区分と税の内訳は表示されません。詳しくは [tax.md](tax.md) を参照してください。
