# スプレッドシート入力

参加者名簿の **1 行 = 1 枚の領収書** として生成します。シートの列の並びや見出しは自由で、どの列に何が入っているかを **対応関係 JSON（mapping）** に書きます。

サンプル：[`input/sheet-example.json`](../input/sheet-example.json) と [`input/sheet-example.csv`](../input/sheet-example.csv)

```bash
python generate.py input/sheet-example.json --dry-run   # 内容の確認
python generate.py input/sheet-example.json             # PDF の生成
```

## シートの例

| 氏名 | 所属 | 一般 | 学生 | 懇親会 | 懇親会費 | 資料 | 入金 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| テスト 太郎 | テスト大学 | 1 | 0 | 1 | 5000 | 2 | 済 |
| サンプル 花子 | サンプル大学 | 0 | 1 | 1 | 3000 | 0 | 済 |
| 未入金 三郎 | テスト大学 | 0 | 1 | 0 | 3000 | 0 |  |

- 購入項目ごとに **数量の列** を用意します。数量が `0` または空欄の項目は、その人の領収書に載りません。
- 区分（一般／学生）は、それぞれ別の項目として列を分け、該当しない方を `0` にします。
- 所属のように、対応関係で使わない列はあっても構いません。

## 対応関係 JSON

```json
{
  "issuer": { "name": "第1回テスト研究会", "email": "test@example.com",
              "invoice_registration_number": null, "stamp_file": "../assets/sample-stamp.png" },
  "source": { "type": "csv", "path": "sheet-example.csv", "header_row": 1 },
  "include_if": { "column": "入金", "in": ["済"] },
  "receipt": {
    "name": { "column": "氏名", "suffix": " 様" },
    "issue_date": "2026-07-11",
    "amount_note": "但し、研究会参加費等として上記正に領収いたしました。",
    "remarks": ["本会は適格請求書発行事業者の登録を受けておりません。"]
  },
  "items": [
    { "name": "研究会参加費（一般）", "quantity": { "column": "一般" }, "unit_price": 31000 },
    { "name": "研究会参加費（学生）", "quantity": { "column": "学生" }, "unit_price": 20000 },
    { "name": "懇親会費", "quantity": { "column": "懇親会" }, "unit_price": { "column": "懇親会費" } },
    { "name": "資料代",   "quantity": { "column": "資料" },   "unit_price": 1000 }
  ]
}
```

### 値の書き方：固定値か列か

`receipt` と `items` の各値は、次のどちらでも書けます。

| 書き方 | 意味 |
| --- | --- |
| `31000` や `"2026-07-11"` | 全員に同じ値を使います |
| `{"column": "列名"}` | 各行のその列の値を使います |

列の指定には次のオプションを付けられます。

| キー | 内容 |
| --- | --- |
| `column` | 見出しの名前（必須）。前後の空白と全角／半角の違いは無視します |
| `default` | セルが空欄のときに使う値 |
| `prefix` / `suffix` | 文字列の前後に付ける文字。すでに付いている場合は重ねません（例：`" 様"`） |

このため、**単価は mapping に固定で書くことも、シートの列から読むこともできます**。上の例では、参加費は固定、懇親会費は列から読んでいます。

### 各セクション

**`issuer`**：発行者。[json-input.md](json-input.md#issuer発行者) と同じです。`stamp_file` は mapping ファイルから見た相対パスです。

**`source`**：読み込むシート。

| キー | 内容 |
| --- | --- |
| `type` | `csv` / `xlsx` / `google_sheets` |
| `path` | CSV/XLSX のパス（mapping ファイルから見た相対パス） |
| `url` | Google スプレッドシートの URL またはキー（`google_sheets` のとき） |
| `worksheet` | シート（タブ）名。省略すると先頭のシート |
| `header_row` | 見出しの行番号（既定 1）。その下の行から読みます |
| `encoding` | CSV の文字コード（既定 UTF-8）。Excel で保存した CSV は `"cp932"` |

`--source` と `--worksheet` を指定すると、`source` の内容より優先されます。同じ mapping を、CSV でのテストと本番のシートで使い回せます。

**`include_if`**（任意）：領収書を作る行を絞り込みます。`{"column": "入金", "in": ["済"]}` なら「入金」列が「済」の行だけ、`{"column": "キャンセル", "not_in": ["TRUE"]}` なら「キャンセル」列が TRUE 以外の行だけを対象にします。

**`receipt`**：領収書全体の項目。

| キー | 必須 | 内容 |
| --- | --- | --- |
| `name` | ○ | 宛名 |
| `issue_date` | ○ | 発行日。`2026-07-11`、`2026/07/11`、`2026年7月11日`、日付型のセルを読めます |
| `file_id` |  | 出力ファイル名。省略すると `発行日_宛名` から自動生成します |
| `amount_note` |  | 但し書き |
| `remarks` |  | 備考。固定の文字列と `{"column": ...}` を混ぜた配列。空欄のセルは無視します |

**`items`**：明細の候補。

| キー | 必須 | 内容 |
| --- | --- | --- |
| `name` | ○ | 項目名（固定の文字列） |
| `quantity` | ○ | 数量。通常は `{"column": ...}` |
| `unit_price` | ○ | 単価。固定値か列 |
| `tax_category` |  | 税区分。`taxable` などのキーのほか、`課税`、`非課税` などの表示名もセルから読めます |
| `tax_rate` |  | 税率（%） |
| `tax_amount` |  | 消費税額。数量が行ごとに異なるときは、固定値ではなくシートで計算した列を指定してください |

## セルの値の読み方

- 数値：`31000`、`31,000`、`¥31,000`、`31000円`、全角数字を読めます。数量と金額は整数のみです。
- 数量：Google スプレッドシートのチェックボックス（`TRUE`/`FALSE`）も 1/0 として読めます。
- 空行は無視します。宛名があって、数量がすべて 0 の行は、スキップした旨を表示します。
- 宛名が空欄なのに数量が入っている行や、数値として読めない値があると、**行番号と列名を示してエラー** になります。PDF は 1 枚も作られません。

## Google スプレッドシート

- **Colab で直接読む**：[colab.md](colab.md) を参照してください。
- **ローカルで読む**：「ファイル → ダウンロード → カンマ区切り形式（.csv）または Microsoft Excel（.xlsx）」で保存し、`--source` で指定します。

  ```bash
  python generate.py input/mapping.json --source ~/Downloads/参加者.xlsx --worksheet "フォームの回答 1" --dry-run
  ```

  `--source` に URL を指定してローカルから直接読むこともできます。ただし、`gspread` のインストールと、Google のスプレッドシート読み取り権限を含む認証（Application Default Credentials）の設定が別途必要です。通常は Colab か CSV/XLSX を使ってください。
