# receipt-gen

研究会向けの領収書 PDF（Portable Document Format）を生成します。入力は次の 2 通りです。

- **JSON（JavaScript Object Notation）ファイル**：領収書の内容をすべて JSON に書く方法です。
- **スプレッドシート**：参加者名簿（Google スプレッドシート、XLSX、CSV（Comma-Separated Values））の 1 行を 1 枚の領収書にする方法です。どの列に何が入っているかは、対応関係を書いた JSON（mapping）で指定します。シート側の形式を変える必要はありません。

## Quick start

```bash
python -m pip install -r requirements.txt   # 事前準備は docs/setup.md

# JSON から生成
python generate.py input/example.json

# スプレッドシート（CSV/XLSX）から生成。まず --dry-run で内容を確認
python generate.py input/sheet-example.json --dry-run
python generate.py input/sheet-example.json
```

PDF は `output/YYYYMMDDThhmmss/` に保存されます。

Google スプレッドシートを直接読む場合は、[Google Colab のノートブック](notebooks/receipt_gen_colab.ipynb)を使います。Google Cloud の設定は不要です。

## Docs

| 内容 | ファイル |
| --- | --- |
| インストール（macOS / Windows） | [docs/setup.md](docs/setup.md) |
| JSON 入力の書き方 | [docs/json-input.md](docs/json-input.md) |
| スプレッドシート入力と対応関係 JSON の書き方 | [docs/spreadsheet.md](docs/spreadsheet.md) |
| Google Colab で Google スプレッドシートから生成する | [docs/colab.md](docs/colab.md) |
| 税区分・インボイスの注意 | [docs/tax.md](docs/tax.md) |

## Command line

```text
python generate.py CONFIG [--dry-run] [--source PATH_OR_URL] [--worksheet NAME]
                          [--output-dir DIR] [--no-timestamp]
```

| オプション | 意味 |
| --- | --- |
| `--dry-run` | PDF を作らず、宛名・明細・合計を一覧表示します |
| `--source` | 対応関係 JSON の `source` の代わりに、指定した CSV/XLSX ファイルまたは Google スプレッドシートの URL を読みます |
| `--worksheet` | 読み込むシート（タブ）名（XLSX / Google スプレッドシート） |
| `--output-dir` | 出力先の親フォルダ（既定: `output`） |
| `--no-timestamp` | 日時フォルダを作らず、出力先に直接保存します |

## Font

`Noto Sans JP` を同梱し、PDF に埋め込みます。OS へのフォントのインストールは不要です。フォントとライセンスは `src/receipt_gen/fonts/` にあります。

## Test

```bash
python -m unittest discover -s tests
```
