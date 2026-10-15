# Google Colab

Google Spreadsheet を読み、領収書 PDF を Google Drive に保存します。

## 準備

次のファイルをダウンロードします。

- [`receipt_gen_colab.ipynb`](../notebooks/receipt_gen_colab.ipynb)

## 開き方

1. [Google Drive](https://drive.google.com/) を開きます。
2. 作業フォルダを作成し、`receipt_gen_colab.ipynb` をアップロードします。
3. アップロードしたファイルを「Google Colaboratory」で開きます。

## 手順

1. `SPREADSHEET_URL`、`WORKSHEET`（タブ名）、`DRIVE_DIR`（上で作成した作業フォルダのパス）を書き換えます。
2. Drive をマウントします。`DRIVE_DIR/code/` にコード一式を取得し、必要なパッケージをインストールします。
3. Google Spreadsheet を読むため、Google アカウントでログインします。
4. テンプレートから `DRIVE_DIR/mapping.json` を自動作成します。
5. 左のファイル欄から `mapping.json` を開き、シートの見出しや金額に合わせて編集します。書き方は [spreadsheet.md](spreadsheet.md) を参照してください。
6. 宛名・明細・合計を確認します。mapping を直した場合は、このセルを再実行します。
7. `DRIVE_DIR/output/日時/` に PDF を保存します。
8. ZIP でダウンロード（任意）

## 補足

- 2回目以降は Drive に保存済みのコードと `mapping.json` を使用します。
- 電子印画像は `DRIVE_DIR` に置き、`issuer.stamp_file` にファイル名（例：`"stamp.png"`）を書きます。
