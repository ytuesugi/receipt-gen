# receipt-gen

研究会向けの領収書 PDF を、`input/` の JSON から生成します。

## Setup

Python 3.10 以上を使用します。

### macOS

```bash
brew install weasyprint
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Windows

WeasyPrint の公式手順に従い、[MSYS2](https://www.msys2.org/) をインストールします。MSYS2 UCRT64 で次を実行します。

```bash
pacman -S mingw-w64-ucrt-x86_64-pango
```

続いて PowerShell で実行します。

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

詳細は [WeasyPrint公式インストール手順](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)を参照してください。

## Input

サンプルをコピーして編集します。

```bash
cp input/example.json input/receipts.json
```

Windowsでは次のコマンドを使用します。

```powershell
Copy-Item input\example.json input\receipts.json
```

### Fields

- `issuer.name`: 発行者名
- `issuer.email`: メールアドレス。不要なら `null`
- `issuer.invoice_registration_number`: インボイス登録番号。未登録なら `null`
- `issuer.stamp_file`: 印影画像のパス。不要なら `null`
- `receipts[].file_id`: PDFのファイル名。`null` なら自動生成
- `receipts[].name`: 宛名
- `receipts[].issue_date`: 発行日（`YYYY-MM-DD`）
- `receipts[].amount_note`: 但し書き。省略可能
- `receipts[].remarks`: 備考の配列。省略または空の配列で非表示
- `receipts[].items`: 明細の配列
- `items[].name`: 項目名
- `items[].quantity`: 数量。省略時は `1`
- `items[].unit_price`: 単価

### Tax

税関連項目をすべて `null` または省略すると、税区分と税内訳は表示されません。適格請求書として使う場合は、[国税庁「適格請求書等の記載事項」](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shohi/6625.htm)を確認してください。

- `items[].tax_category`: 税区分
- `items[].tax_rate`: 税率（例: `10`）
- `items[].tax_amount`: 税額。`null` なら自動計算
- `issuer.tax_rounding`: 自動計算の端数処理。`floor`（切り捨て、既定）、`round`（四捨五入）、`ceil`（切り上げ）

単価は税込とみなします。`tax_amount` が `null` の場合、領収書ごと・税区分と税率ごとに金額を合計し、`合計 × 税率 / (100 + 税率)` を 1 回だけ端数処理して消費税額を求めます（適格請求書では、端数処理は税率ごとに 1 回とされています）。自動計算するのは `taxable` と `reduced_taxable` で、`tax_rate` があるときだけです。同じ税区分・税率の明細では、`tax_amount` をすべて指定するか、すべて `null` にしてください。

`tax_category` は `taxable`（課税）、`reduced_taxable`（軽減税率）、`non_taxable`（非課税）、`out_of_scope`（不課税）、`exempt`（免税）から選びます。

「非課税」と「不課税」は異なります。税区分は取引内容によって判断し、[国税庁「非課税と不課税の違い」](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shohi/6209.htm)も確認してください。

## Run

```bash
python generate.py input/receipts.json
```

PDF は `output/YYYYMMDDThhmmss/` に保存されます。

## Font

`Noto Sans JP` をプロジェクト内に同梱し、PDFへ埋め込みます。OSへのフォントインストールは不要です。フォントとライセンスは `src/receipt_gen/fonts/` にあります。

## Test

```bash
python -m unittest discover -s tests
```
