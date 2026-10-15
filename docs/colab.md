# Google Colab で生成する

[`notebooks/receipt_gen_colab.ipynb`](../notebooks/receipt_gen_colab.ipynb) を使うと、Google スプレッドシートを直接読み、PDF を Google Drive に保存できます。Google Cloud のプロジェクトや API（Application Programming Interface）キーの作成は不要で、自分の Google アカウントでログインするだけです。WeasyPrint のインストールもノートブックが行います。

## 開き方

次のどちらかで開きます。

- GitHub から：Colab の「ファイル → ノートブックを開く → GitHub」で `ytuesugi/receipt-gen` を指定します（非公開リポジトリの場合は「プライベート リポジトリを含める」にチェック）。
- Drive から：`.ipynb` を Drive にアップロードし、ダブルクリックして「Google Colaboratory」で開きます。

## 手順

1. **設定**：`SPREADSHEET_URL`、`WORKSHEET`（タブ名）、`DRIVE_DIR`（作業フォルダ）を書き換えます。
2. **Drive のマウントとインストール**：receipt-gen のコードを取得し、依存パッケージをインストールします。
   - `CODE_SOURCE = "github"`：GitHub から clone します。非公開リポジトリの場合は、Colab の「シークレット」（左の鍵アイコン）に `GITHUB_TOKEN` として、読み取り権限のある GitHub の Personal Access Token を登録します。
   - `CODE_SOURCE = "drive"`：リポジトリのフォルダを Drive にコピーしておき、`CODE_DIR_IN_DRIVE` で指定します。
3. **ログイン**：スプレッドシートを読むための許可を求められるので、許可します。
4. **mapping.json の準備**：初回はサンプルから `DRIVE_DIR/mapping.json` を作ります。表示されたシートの見出しに合わせて編集します（左のファイル欄でダブルクリックすると編集できます）。書き方は [spreadsheet.md](spreadsheet.md) を参照してください。
5. **プレビュー**：宛名・明細・合計を表で確認します。mapping を直したら、このセルだけ再実行します。
6. **生成**：`DRIVE_DIR/output/日時/` に PDF を保存します。
7. **ZIP でダウンロード**（任意）

## 補足

- 印影画像は `DRIVE_DIR` に置き、`issuer.stamp_file` にファイル名（例：`"stamp.png"`）を書きます。
- ノートブックでは、mapping の `source` にかかわらず、`SPREADSHEET_URL` と `WORKSHEET` のシートを読みます。
- 出力した PDF と mapping には個人情報が含まれます。Drive の共有設定に注意してください。
