# receipt-gen

JSON に入力した内容から、日本語の領収書 PDF を一括生成する小さな Python ツールです。

Google Colab や Google Drive は使いません。データはローカルで処理され、領収書ごとの金額は `数量 × 単価` から自動計算されます。印影画像は任意です。

## 必要なもの

- macOS
- Python 3.10 以上

## セットアップ

ターミナルでこのフォルダに移動し、次を実行します。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

WeasyPrint のインストール時または実行時に共有ライブラリのエラーが出る場合は、Homebrew を導入したうえで次を実行し、もう一度インストールしてください。

```bash
brew install pango libffi
```

## 使い方

1. サンプル設定を、Git 管理されない作業用ファイルにコピーします。

   ```bash
   cp config.example.json config.json
   ```

2. `config.json` を編集します。`receipts` に複数の領収書を並べると、一度に生成できます。
3. PDF を生成します。

   ```bash
   receipt-gen config.json
   ```

PDF は `output/20260711T120000/receipt-001.pdf` のような日時付きフォルダに作成されます。保存先を変える場合は次のようにします。

```bash
receipt-gen config.json --output-dir ~/Desktop/receipts
```

日時フォルダを作らず、指定先へ直接出力することもできます。

```bash
receipt-gen config.json --output-dir output --no-timestamp
```

インストールせずに実行したい場合は、仮想環境で依存パッケージを入れた後、次のコマンドも使えます。

```bash
PYTHONPATH=src python -m receipt_gen config.json
```

## 設定ファイル

`config.example.json` が安全なサンプルです。

- `issuer`: 発行者名、メールアドレス、任意の印影画像
- `receipts`: 生成する領収書の一覧
- `file_id`: PDF のファイル名（英数字、`.`、`_`、`-` が使用可能）
- `issue_date`: 発行日（`YYYY-MM-DD`）
- `items`: 項目、数量、単価（円）の一覧
- `remarks`: 備考の一覧。不要なら空配列にできます

金額は整数の円として扱います。合計額は各項目の `quantity * unit_price` の合計です。

## 印影画像を使う

印影なしでも生成できます。使う場合は PNG または JPEG を `assets/stamp.png` などの名前で配置し、`config.json` の `stamp_file` を設定します。

```json
"stamp_file": "assets/stamp.png"
```

パスは `config.json` があるフォルダを基準に解決されます。画像が設定されているのに見つからない場合は、PDF を生成せずエラーにします。詳しくは `assets/README.md` を参照してください。

## GitHub で共有する前に

`config.json`、`output/`、`assets/` 内の印影画像は `.gitignore` の対象です。実際の宛名、メールアドレス、領収金額、印影が Git に含まれていないことを、公開前に必ず確認してください。

```bash
git status
```

サンプルを変更する場合も、実在する個人や非公開の連絡先は使わないでください。

## テスト

```bash
python -m unittest discover -s tests
```
