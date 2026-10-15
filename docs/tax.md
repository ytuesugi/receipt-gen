# Tax

## Display

`tax_category`、`tax_rate`、`tax_amount` をすべて `null` または省略すると、税欄は表示されません。いずれかを設定すると、税区分・税率ごとの対象額と消費税額を表示します。

`invoice_registration_number` を設定すると、適格請求書発行事業者の登録番号を表示します。

## Categories

| 値 | 表示 |
| --- | --- |
| `taxable` | 課税 |
| `reduced_taxable` | 課税（軽減税率） |
| `non_taxable` | 非課税 |
| `out_of_scope` | 不課税 |
| `exempt` | 免税 |

## Calculation

単価は税込として扱います。`tax_amount` が `null` の場合、`taxable` と `reduced_taxable` について、税区分・税率ごとの合計から内税を計算します。

```text
消費税額 = 税込合計 × 税率 ÷ (100 + 税率)
```

端数処理は `issuer.tax_rounding` で指定します。

| 値 | 処理 |
| --- | --- |
| `floor` | 切り捨て（既定） |
| `round` | 四捨五入 |
| `ceil` | 切り上げ |

税額を指定する場合、同じ税区分・税率の明細では、すべてに `tax_amount` を指定してください。

## Reference

- [国税庁：適格請求書等の記載事項](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shohi/6625.htm)
- [国税庁：非課税と不課税の違い](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shohi/6209.htm)
