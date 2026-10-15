# 税区分とインボイス

## 表示の切り替え

明細の `tax_category`、`tax_rate`、`tax_amount` がすべての明細で `null` または省略されている場合、税区分の列と税の内訳は表示されません。1 つでも設定すると、税区分の列と、税区分・税率ごとの対象額と消費税額が表示されます。

`issuer.invoice_registration_number` を設定すると、登録番号が表示されます。

## 消費税額

`tax_amount` は入力した値をそのまま表示します。税率と金額からの自動計算や、整合性の確認は行いません。スプレッドシートから読む場合で数量が行ごとに異なるときは、シートの列で税額を計算し、`{"column": "税額"}` のように指定してください（[spreadsheet.md](spreadsheet.md)）。

## 確認先

適格請求書として使う場合は、[国税庁「適格請求書等の記載事項」](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shohi/6625.htm)を確認してください。

「非課税」と「不課税」は異なります。税区分は取引内容によって判断し、[国税庁「非課税と不課税の違い」](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shohi/6209.htm)も確認してください。
