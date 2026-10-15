# 印影画像

印影を表示する場合は、このフォルダに PNG または JPEG 画像を置きます。例:

```text
assets/stamp.png
```

その後、`config.json` の発行者設定を次のようにします。

```json
"stamp_file": "assets/stamp.png"
```

印影が不要な場合は `null` のままにしてください。

このフォルダ内の画像は、個人情報を誤って公開しないよう `.gitignore` で除外されています。
