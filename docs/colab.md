# Google Colab

Google Spreadsheet を読み、領収書 PDF を Google Drive へ保存します。ローカルへのインストールは不要です。

## Open

1. [`receipt_gen_colab.ipynb`](../notebooks/receipt_gen_colab.ipynb) をダウンロードします。
2. [Google Drive](https://drive.google.com/) を開きます。
3. 作業フォルダを作成し、[`receipt_gen_colab.ipynb`](../notebooks/receipt_gen_colab.ipynb) をアップロードします。
4. アップロードした [`receipt_gen_colab.ipynb`](../notebooks/receipt_gen_colab.ipynb) を Google Colaboratory で開きます。

## Run

1. `SPREADSHEET_URL`、`WORKSHEET`、`DRIVE_DIR` を設定します。
2. `mapping.json` の作成セルまで、上から順に実行します。
3. 画面左側のファイルアイコン（フォルダの形）を押します。
4. `drive` → `MyDrive` → `DRIVE_DIR` で指定した作業フォルダを開きます。
5. `mapping.json` をダブルクリックし、開いたエディタでシートに合わせて編集します。表示されない場合は、ファイル欄の更新アイコンを押します。
6. 編集内容を保存し、Notebook に戻ります。
7. 残りのセルを実行して内容を確認し、PDF を生成します。

PDF は `DRIVE_DIR/output/日時/` に保存されます。mapping の書き方は [`spreadsheet.md`](spreadsheet.md) を参照してください。

電子印は `DRIVE_DIR` に置き、`mapping.json` の `issuer.stamp_file` にファイル名を指定します。
