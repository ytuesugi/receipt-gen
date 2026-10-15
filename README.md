# receipt-gen

研究会向けの領収書 PDF（Portable Document Format）を生成します。入力は次の 2 通りです。

- **JSON ファイル**：領収書の内容をすべて JSON に書く方法です。
- **表形式ファイル**：参加者名簿（Google Spreadsheet、XLSX、CSV）の 1 行を 1 枚の領収書にする方法です。どの列に何が入っているかは、対応関係を書いた JSON で指定します。

## Quick start

```bash
python -m pip install -r requirements.txt

# JSON
python generate.py input/example.json

# CSV/XLSX
python generate.py input/sheet-example.json --dry-run
python generate.py input/sheet-example.json
```

PDF は `output/YYYYMMDDThhmmss/` に保存されます。

Google Spreadsheet を直接読む場合は、[notebooks/receipt_gen_colab.ipynb](notebooks/receipt_gen_colab.ipynb) を Google Colab 上で使います。

## Documents

| 内容 | ファイル |
| --- | --- |
| インストール（macOS / Windows） | [docs/setup.md](docs/setup.md) |
| 【JSON ファイル入力 / local】入力 JSON の書き方 | [docs/json-input.md](docs/json-input.md) |
| 【表形式ファイル入力 / local】対応関係 JSON の書き方 | [docs/spreadsheet.md](docs/spreadsheet.md) |
| 【表形式ファイル入力 / Google Colab】Google Spreadsheet から生成 | [docs/colab.md](docs/colab.md) |
| 税区分・インボイスの注意 | [docs/tax.md](docs/tax.md) |

## Command line

```text
python generate.py CONFIG [--dry-run] [--source PATH_OR_URL] [--worksheet NAME]
                          [--output-dir DIR] [--no-timestamp]
```

| オプション | 意味 |
| --- | --- |
| `--dry-run` | PDF を作らず、宛名・明細・合計を一覧表示します |
| `--source` | 対応関係 JSON の `source` の代わりに、指定した CSV/XLSX ファイルまたは Google Spreadsheetの URL を読みます |
| `--worksheet` | 読み込むシート（タブ）名（XLSX / Google Spreadsheet） |
| `--output-dir` | 出力先の親フォルダ（既定: `output`） |
| `--no-timestamp` | 日時フォルダを作らず、出力先に直接保存します |

## Font

`Noto Sans JP` を同梱し、PDF に埋め込みます。OS へのフォントのインストールは不要です。フォントとライセンスは `src/receipt_gen/fonts/` にあります。

## Test

```bash
python -m unittest discover -s tests
```
