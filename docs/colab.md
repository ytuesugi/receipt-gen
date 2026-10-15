# Google Colab

Google Spreadsheet を読み、領収書 PDF を Google Drive へ保存します。ローカルへのインストールは不要です。

## Open

1. [`receipt_gen_colab.ipynb`](../notebooks/receipt_gen_colab.ipynb)をダウンロードします。
2. [Google Drive](https://drive.google.com/)を開きます。
3. 作業フォルダを作成し、Notebook をアップロードします。
4. アップロードした Notebook を Google Colaboratory で開きます。

## Run

1. `SPREADSHEET_URL`、`WORKSHEET`、`DRIVE_DIR` を設定します。
2. セルを上から順に実行します。
3. 自動作成された `DRIVE_DIR/mapping.json` をシートに合わせて編集します。
4. 内容を確認し、PDF を生成します。

PDF は `DRIVE_DIR/output/日時/` に保存されます。mapping の書き方は [`spreadsheet.md`](spreadsheet.md) を参照してください。

電子印は `DRIVE_DIR` に置き、`mapping.json` の `issuer.stamp_file` にファイル名を指定します。
