# THIRD_PARTY_LICENSES

本PoCが使用する第三者のモデル・OSSライブラリの一覧です。

- ライセンス名は各配布元の表記（2026年9月時点で確認したもの）に基づきます。**再配布・商用利用・成果物への同梱の前に、必ず配布元の最新の LICENSE / モデルカードを一次情報として確認してください。**
- モデルは「コードのライセンス」と「重み（weights）のライセンス」が異なる場合があるため、モデルについては配布元のモデルカードの記載を優先します。

## モデル

| 名称 | 用途 | ライセンス | 配布元 | 備考 |
|---|---|---|---|---|
| Qwen3（`qwen3:8b` / `qwen3:4b`） | 回答生成（LLM 推論。Ollama 経由） | Apache-2.0 | https://ollama.com/library/qwen3 / https://huggingface.co/Qwen | 利用前に配布元のモデルカードで最終確認すること |
| `cl-nagoya/ruri-v3-310m` | 日本語埋め込み（1段目検索） | Apache-2.0 | https://huggingface.co/cl-nagoya/ruri-v3-310m | 利用前に配布元のモデルカードで最終確認すること |
| `BAAI/bge-reranker-v2-m3` | 再ランク（2段目検索） | Apache-2.0 | https://huggingface.co/BAAI/bge-reranker-v2-m3 | 利用前に配布元のモデルカードで最終確認すること |

## ライブラリ・ツール

| 名称 | 用途 | ライセンス | 配布元 |
|---|---|---|---|
| Ollama | ローカル LLM 推論サーバ | MIT | https://github.com/ollama/ollama |
| ChromaDB (`chromadb`) | ベクタDB（ローカル永続化） | Apache-2.0 | https://github.com/chroma-core/chroma |
| Streamlit (`streamlit`) | チャット UI | Apache-2.0 | https://github.com/streamlit/streamlit |
| sentence-transformers | 埋め込み・CrossEncoder の実行 | Apache-2.0 | https://github.com/UKPLab/sentence-transformers |
| Transformers (`transformers`) | トークナイザ・モデルロード基盤 | Apache-2.0 | https://github.com/huggingface/transformers |
| PyTorch (`torch`) | 深層学習ランタイム（CPU/GPU 自動判定） | BSD-3-Clause | https://github.com/pytorch/pytorch |
| NumPy (`numpy`) | 再ランクスコアの数値処理 | BSD-3-Clause | https://github.com/numpy/numpy |
| SentencePiece (`sentencepiece`) | トークナイザ依存 | Apache-2.0 | https://github.com/google/sentencepiece |
| pypdf | PDF テキスト抽出（主） | BSD-3-Clause | https://github.com/py-pdf/pypdf |
| pdfplumber | PDF テキスト抽出（表崩れ時のフォールバック） | MIT | https://github.com/jsvine/pdfplumber |
| PyYAML (`pyyaml`) | golden_set.yaml の読み込み | MIT | https://github.com/yaml/pyyaml |
| Requests (`requests`) | Ollama API へのローカル HTTP 通信 | Apache-2.0 | https://github.com/psf/requests |
| python-dotenv | `.env` による設定上書き | BSD-3-Clause | https://github.com/theskumar/python-dotenv |

## 補足

- 上記モデル・ライブラリはすべて**ローカルで実行**され、ドキュメントや質問文が外部サービスへ送信されることはありません（ネットワークを使うのはモデル・パッケージの初回ダウンロードのみ）。
- Docker ルートで使用するベースイメージ（`python:3.11-slim`、`ollama/ollama`）には、それぞれのイメージ・同梱ソフトウェアのライセンスが適用されます。配布時は各イメージの配布元の表記を確認してください。
