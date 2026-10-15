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
3. 以下の手順で `mapping.json` を編集します。
   1. 画面左側のフォルダの形をしたアイコンを押します。
   2. `drive` → `MyDrive` → `DRIVE_DIR` で指定した作業フォルダを開きます。
   3. `mapping.json` をダブルクリックし、開いたエディタでシートに合わせて編集します。表示されない場合は、ファイル欄の更新アイコンを押します。`mapping.json` の書き方は [`spreadsheet.md`](spreadsheet.md) の Mapping の章以降を参照してください。
   4. 電子印を使う場合は `DRIVE_DIR` に置き、`mapping.json` の `issuer.stamp_file` にファイル名を指定します。
4. 残りのセルを実行して内容を確認し、PDF を生成します。PDF は `DRIVE_DIR/output/日時/` に保存されます。


