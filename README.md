# スクレイピングされたウェブサイト

このディレクトリには、以下のURLからスクレイピングされた完全なウェブサイトのファイルが含まれています：

**元URL:** https://sb-preview.squadbeyond.com/articles/zrJcXiSngBrbG-KirGCmg/preview

## ファイル構造

```
scraped_website/
├── index.html              # メインHTMLファイル
├── css/
│   └── styles.css          # スタイルシート（インラインCSSから抽出）
├── js/
│   ├── application-...js   # メインJavaScriptファイル
│   ├── cvsu.js            # トラッキング用JavaScript
│   ├── URI.min.js         # URI操作ライブラリ
│   ├── smooth-scroll.min.js # スムーススクロールライブラリ
│   └── index.js           # その他JavaScript
├── images/
│   ├── 382a8a6d-ad97-41c3-ab5a-16f575c30ae7.jpg  # 背景画像
│   └── lazy.png           # 遅延読み込み用画像
└── assets/
    └── (アセットファイル)
```

## 使い方

1. このディレクトリをウェブサーバーにアップロード
2. `index.html` をブラウザで開く
3. ローカルで確認する場合は、簡易サーバーを起動：
   ```bash
   python -m http.server 8000
   ```
   その後、ブラウザで `http://localhost:8000` にアクセス

## 特徴

- ✅ 完全なHTML構造を保持
- ✅ 全てのCSSスタイルを抽出・整理
- ✅ JavaScript機能を保持
- ✅ 画像ファイルを取得
- ✅ 相対パスに修正済み（移植可能）
- ✅ オフラインで動作可能

## 注意点

- 外部サービスのAPI呼び出しなど、一部の動的機能は動作しない場合があります
- フォーム送信などのインタラクティブ機能は元のサーバーに依存するため動作しません
