# =============================================================================
# local-rag-poc — Docker を使わない環境向けの実行ルート（仕様書 §13-3）
#
# Docker Desktop が無い場合でも、この Makefile ＋ ネイティブ Ollama だけで
# セットアップから評価まで完結する。典型的な流れ:
#   make setup       # venv 作成＋依存インストール
#   make pull-model  # Ollama モデル取得（初回のみ・要ネットワーク）
#   make ingest      # data/corpus/ の取り込み（ベクタDB構築）
#   make run         # Streamlit UI 起動（http://localhost:8501）
#   make eval        # ゴールデンセット評価（CSV 出力）
#
# 注意: Ubuntu 24.04 はシステム Python への pip install がブロックされる
# （externally-managed-environment）ため、必ず venv を使う（仕様書 §3）。
# =============================================================================

# venv のパスはここで一元管理する（ターゲットごとの直書きで食い違わないように）
VENV   := venv
PYTHON := $(VENV)/bin/python
PIP    := $(VENV)/bin/pip

# eval/ や data/ など同名のディレクトリが存在しても「up to date」で
# スキップされないよう、全ターゲットを PHONY 宣言する
.PHONY: help setup pull-model ingest run eval clean-db check-venv

.DEFAULT_GOAL := help

help:
	@echo "使い方: make <target>"
	@echo "  setup       venv を作成し依存パッケージをインストール"
	@echo "  pull-model  Ollama モデル（qwen3 8b/4b）を取得"
	@echo "  ingest      data/corpus/ を取り込んでベクタDBを構築"
	@echo "  run         Streamlit UI を起動"
	@echo "  eval        ゴールデンセット評価を実行し CSV 出力"
	@echo "  clean-db    ベクタDB（ChromaDB 永続化データ）を削除"

# venv 作成に失敗する典型原因は python3-venv 未導入のため、対処法を添える
setup:
	@command -v python3 >/dev/null 2>&1 || { echo "エラー: python3 が見つかりません → sudo apt install python3 python3-venv を実行してください"; exit 1; }
	python3 -m venv $(VENV) || { echo "エラー: venv の作成に失敗しました → sudo apt install python3-venv を実行してから再試行してください"; exit 1; }
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "セットアップ完了。次は make pull-model を実行してください"

# venv 未作成のまま他ターゲットを実行したとき、原因と対処を明示するための
# 内部チェック（仕様書 §11: エラーは利用者向け対処法つきで表示する）
check-venv:
	@test -x "$(PYTHON)" || { echo "エラー: venv が見つかりません → 先に make setup を実行してください"; exit 1; }

# GPU 判定は Make からは行わない（nvidia-smi の有無等は環境依存で壊れやすい）。
# 代わりに 8b/4b の両方を pull する。両方あれば GPU 有無どちらの環境でも
# config.py の自動フォールバックが機内モードのまま成立する（仕様書 §2, §4）。
# 回線が細い場合は CPU 既定の 4b だけでもよい: `ollama pull qwen3:4b`
# モデル名は config.py から読む（Makefile と config の二重管理を避けるため）
pull-model: check-venv
	@command -v ollama >/dev/null 2>&1 || { echo "エラー: ollama コマンドが見つかりません → https://ollama.com/download からインストールするか、Docker がある場合は docker compose ルートを使ってください"; exit 1; }
	@set -e; \
	models=$$($(PYTHON) -c "from src import config; print(config.OLLAMA_MODEL); print(config.OLLAMA_FALLBACK_MODEL)"); \
	for m in $$models; do \
		echo "=== ollama pull $$m ==="; \
		ollama pull "$$m"; \
	done

ingest: check-venv
	$(PYTHON) -m src.ingest

run: check-venv
	$(VENV)/bin/streamlit run src/app.py

eval: check-venv
	$(PYTHON) -m eval.run_eval

# チャンクサイズ等の調整後にベクタDBを作り直したいときに使う。
# 削除先のパスは config.py の CHROMA_DIR を参照する（パスの二重管理を避け、
# 環境変数 CHROMA_DIR で場所を変えている場合にも正しく追従させるため）。
# ディレクトリごと消さず「中身のみ」削除するのは、git 管理下の
# data/chroma/.gitkeep まで消して git status が汚れるのを防ぐため
clean-db: check-venv
	$(PYTHON) -c "from src import config; import shutil; d = config.CHROMA_DIR; [shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink(missing_ok=True) for p in d.glob('*') if p.name != '.gitkeep']; print('削除しました:', d)"
