# QuizCardsGenerator

**QuizCardsGenerator** は、Excelファイルに記載されたクイズ情報をもとに、画像ファイルを自動生成するPythonスクリプトです。OGPサイズ（1200x630）で出力され、SNS投稿やクイズイベント、プレゼン資料として即座に活用可能です。

---

## 🎯 特徴

- Excelファイルから複数のクイズカード画像を一括生成
- 背景画像 + テキスト描画（日本語フォント対応）
- 明るさ・コントラスト・ぼかしの画像調整機能あり
- テストモードで画像調整の確認が可能
- 設定ファイル（config.json）で柔軟にカスタマイズ可能

---

## 🔧 必要な環境

- Python 3.8+
- Windows推奨（日本語フォントパスがWindows依存）

### 必要ライブラリ

```bash
pip install pillow pandas
```

---

## 🗂️ ファイル構成

```
📦 QuizCardsGenerator/
├── QuizCardsGenerator.py      # メインスクリプト
├── config.json                # 設定ファイル
├── README.md                  # このファイル
```

---

## 📄 config.json の内容（例）

```json
{
  "image": {
    "width": 1200,
    "height": 630,
    "background_color": "#000000",
    "brightness": 0.5,
    "contrast": 1.0,
    "blur": 3.0
  },
  "font": {
    "path": "C:/Windows/Fonts/BIZ-UDGOTHICR.ttc",
    "title_size": 42,
    "question_size": 36,
    "answer_size": 36
  },
  "color": {
    "title_text": "white",
    "title_outline": "black",
    "question_text": "white",
    "question_outline": "black",
    "answer_text": "yellow",
    "answer_outline": "black"
  },
  "layout": {
    "line_spacing_ratio": 1.4,
    "x_margin": 30
  },
  "test": {
    "title": "テストラウンド 1問目",
    "question": "この画像はテストモードで生成されたものです。",
    "answer": "テスト用の答え",
    "output": "test_output.png"
  }
}
```

---
## 📥 通常モード

```bash
python QuizCardsGenerator.py
```

実行後、以下を順に選択します：

1. Excelファイル（クイズデータ）
2. 背景画像ファイル（JPG/PNG）

---

## 🧪 テストモード（画像調整確認用）

```bash
python QuizCardsGenerator.py test --brightness 0.7 --contrast 1.2 --blur 2.0 --background path/to/image.jpg
```

### オプション

| オプション       | 説明                          |
|------------------|-------------------------------|
| `--brightness`   | 明るさの係数（例: 0.8）       |
| `--contrast`     | コントラスト係数（例: 1.2）   |
| `--blur`         | ぼかし半径（例: 2.0）         |
| `--background`   | 背景画像ファイルのパス(省略するとGUIで選択可能)        |

---


## 📝 Excelファイル仕様

| 列名             | 内容例               | 必須 |
|------------------|----------------------|------|
| ラウンド         | 第1ラウンド           | ○    |
| 出題順           | 1, 2, 3...           | ○    |
| 問題文           | 日本語のクイズ文     | ○    |
| 答え             | 答えの文字列         | ○    |
| フォルダ名       | 出力先フォルダ名     | ○    |
| ファイル名接頭辞 | 例: `Q_`（任意）     | ×    |

---

## 🖼️ 出力ファイル例

```
<フォルダ名>/<ファイル名接頭辞><出題順（3桁ゼロ埋め）>.png
例: Round1/Q_001.png
```

---

## 📄 ライセンス

このプロジェクトは MIT ライセンスのもとで公開されています。

---

## 🙌 貢献・フィードバック歓迎！

- Issue や Pull Request お待ちしています！
