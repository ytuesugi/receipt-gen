# CSV / XLSX

参加者名簿の 1 行から領収書を 1 枚生成します。列と領収書項目の対応は mapping JSON で指定します。

## Run

サンプルは [`input/sheet-example.csv`](../input/sheet-example.csv) と [`input/sheet-example.json`](../input/sheet-example.json) です。

```bash
python generate.py input/sheet-example.json --dry-run
python generate.py input/sheet-example.json
```

別のファイルを一時的に読む場合は `--source` を使います。

```bash
python generate.py input/sheet-example.json \
  --source ~/Downloads/participants.xlsx \
  --worksheet "Participants" \
  --dry-run
```

## Mapping

```json
{
  "issuer": {
    "name": "第1回テスト研究会",
    "email": "test@example.com",
    "invoice_registration_number": null,
    "stamp_file": "../assets/sample-stamp.png"
  },
  "source": {
    "type": "csv",
    "path": "sheet-example.csv",
    "header_row": 1
  },
  "include_if": {"column": "入金", "in": ["済"]},
  "receipt": {
    "name": {"column": "氏名", "suffix": " 様"},
    "issue_date": "2026-07-11",
    "amount_note": "但し、研究会参加費等として上記正に領収いたしました。",
    "remarks": ["本会は適格請求書発行事業者ではありません。"]
  },
  "items": [
    {"name": "研究会参加費（一般）", "quantity": {"column": "一般"}, "unit_price": 31000},
    {"name": "研究会参加費（学生）", "quantity": {"column": "学生"}, "unit_price": 20000},
    {"name": "懇親会費", "quantity": {"column": "懇親会"}, "unit_price": {"column": "懇親会費"}}
  ]
}
```

固定値はそのまま、列から読む値は `{"column": "列名"}` と書きます。列指定には `default`、`prefix`、`suffix` も設定できます。

## Sections

### `source`

| キー | 内容 |
| --- | --- |
| `type` | `csv` または `xlsx` |
| `path` | mapping JSON から見たファイルの相対パス |
| `worksheet` | XLSX のシート名。省略時は先頭 |
| `header_row` | 見出し行。既定は `1` |
| `encoding` | CSV の文字コード。Excel 由来なら `cp932` を指定可能 |

### `include_if`

任意です。`{"column": "入金", "in": ["済"]}` なら、「入金」が「済」の行だけを対象にします。除外条件には `not_in` を使います。

### `receipt`

`name` と `issue_date` が必須です。`file_id`、`amount_note`、`remarks` も指定できます。

### `items`

`name`、`quantity`、`unit_price` を指定します。数量が `0` または空欄の項目は領収書に載りません。税項目は [`tax.md`](tax.md) を参照してください。

## Values

- `31000`、`31,000`、`¥31,000`、`31000円` を数値として読めます。
- チェックボックスの `TRUE` / `FALSE` は数量の `1` / `0` として読めます。
- 空行は無視します。
- 不正な値は行番号と列名を表示して停止します。

Google Spreadsheet を読む場合は [`colab.md`](colab.md) を参照してください。
