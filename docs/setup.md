# インストール

Python 3.10 以上を使用します。PDF の生成には [WeasyPrint](https://doc.courtbouillon.org/weasyprint/stable/) を使います。

Google スプレッドシートを Google Colab から読むだけの場合、ここでの準備は不要です。[colab.md](colab.md) を参照してください。

## macOS

```bash
brew install weasyprint
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Windows

WeasyPrint の公式手順に従い、[MSYS2](https://www.msys2.org/) をインストールします。MSYS2 UCRT64 で次を実行します。

```bash
pacman -S mingw-w64-ucrt-x86_64-pango
```

続いて PowerShell で実行します。

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

詳細は [WeasyPrint 公式インストール手順](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows)を参照してください。

## 依存パッケージ

| パッケージ | 用途 |
| --- | --- |
| Jinja2 | HTML テンプレート |
| WeasyPrint | HTML から PDF への変換 |
| openpyxl | XLSX の読み込み |
| tqdm | 生成中の進捗表示 |

Google スプレッドシートを直接読む機能は `gspread` と `google-auth` を使います。どちらも Google Colab に最初から入っているため、`requirements.txt` には含めていません。
