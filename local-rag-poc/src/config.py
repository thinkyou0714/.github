"""設定の一元管理モジュール。

全ての調整可能な値をここに集約する（指示文書 §11: マジックナンバー直書き禁止）。
値は環境変数（.env）で上書き可能。秘密情報はここに置かない。
"""

import os
from pathlib import Path

# .env があれば読み込む。python-dotenv 未導入でも動くように任意依存にしている
# （Docker では environment で渡すため .env が無いケースがあるから）。
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def _env_str(key: str, default: str) -> str:
    return os.environ.get(key, default)


def _env_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, default))
    except ValueError:
        # 不正値で起動不能になるより既定値で続行し、原因を利用者に伝える
        print(f"[config] 環境変数 {key} が整数として解釈できないため既定値 {default} を使用します")
        return default


def _env_float(key: str, default: float) -> float:
    try:
        return float(os.environ.get(key, default))
    except ValueError:
        print(f"[config] 環境変数 {key} が数値として解釈できないため既定値 {default} を使用します")
        return default


# ---------------------------------------------------------------------------
# パス（プロジェクトルート基準。実行時カレントディレクトリに依存させない）
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = Path(_env_str("CORPUS_DIR", str(PROJECT_ROOT / "data" / "corpus")))
CHROMA_DIR = Path(_env_str("CHROMA_DIR", str(PROJECT_ROOT / "data" / "chroma")))
EVAL_DIR = PROJECT_ROOT / "eval"
GOLDEN_SET_PATH = Path(_env_str("GOLDEN_SET_PATH", str(EVAL_DIR / "golden_set.yaml")))
EVAL_RESULTS_DIR = Path(_env_str("EVAL_RESULTS_DIR", str(EVAL_DIR / "results")))

# ---------------------------------------------------------------------------
# 埋め込み（1段目検索）: cl-nagoya/ruri-v3-310m（指示文書 §4 で確定・変更禁止）
# ---------------------------------------------------------------------------
EMBED_MODEL_NAME = _env_str("EMBED_MODEL_NAME", "cl-nagoya/ruri-v3-310m")
# Ruri v3 はプレフィックス方式で学習されており、検索用途では
# クエリ側・文書側に下記プレフィックスを付けないと精度が大きく落ちる。
# （モデルカード記載の "1+3 プレフィックス" のうち検索用の2つ）
EMBED_QUERY_PREFIX = "検索クエリ: "
EMBED_DOC_PREFIX = "検索文書: "
EMBED_BATCH_SIZE = _env_int("EMBED_BATCH_SIZE", 32)

# ---------------------------------------------------------------------------
# 再ランク（2段目検索）: BAAI/bge-reranker-v2-m3（指示文書 §4 で確定・変更禁止）
# ---------------------------------------------------------------------------
RERANK_MODEL_NAME = _env_str("RERANK_MODEL_NAME", "BAAI/bge-reranker-v2-m3")
# rerank スコア（sigmoid 後、0〜1）がこの閾値未満のヒットしか無い場合は
# 「資料内に該当なし」として LLM を呼ばずに拒否する。
# 拒否判定をプロンプト（LLM任せ)にせずコード側で行うのは、軽量モデルが
# 指示を無視して推測で答える事例への対策（指示文書 §10 Phase 4 注記）。
RERANK_SCORE_THRESHOLD = _env_float("RERANK_SCORE_THRESHOLD", 0.30)

# ---------------------------------------------------------------------------
# 検索パラメータ（指示文書 §5: Embedding上位50件 → Reranker上位5件）
# ---------------------------------------------------------------------------
TOP_K_EMBED = _env_int("TOP_K_EMBED", 50)
TOP_K_RERANK = _env_int("TOP_K_RERANK", 5)

# ---------------------------------------------------------------------------
# チャンク分割（指示文書 §10 Phase 2: 初期値 512トークン / オーバーラップ 64）
# トークン数は埋め込みモデル（ruri-v3）のトークナイザ基準で数える。
# 文字数基準にしないのは、埋め込み時の入力上限と直結する単位で管理するため。
# ---------------------------------------------------------------------------
CHUNK_SIZE_TOKENS = _env_int("CHUNK_SIZE_TOKENS", 512)
CHUNK_OVERLAP_TOKENS = _env_int("CHUNK_OVERLAP_TOKENS", 64)

# ---------------------------------------------------------------------------
# ベクタDB: ChromaDB ローカル永続化（指示文書 §4）
# ---------------------------------------------------------------------------
CHROMA_COLLECTION_NAME = _env_str("CHROMA_COLLECTION_NAME", "corpus")

# ---------------------------------------------------------------------------
# 推論: Ollama（指示文書 §4: qwen3:8b、GPU無しなら qwen3:4b へ自動フォールバック）
# ---------------------------------------------------------------------------
OLLAMA_HOST = _env_str("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = _env_str("OLLAMA_MODEL", "qwen3:8b")
OLLAMA_FALLBACK_MODEL = _env_str("OLLAMA_FALLBACK_MODEL", "qwen3:4b")
# CPU-only の受入基準が 60 秒/問（指示文書 §6-6）なので、余裕を持たせつつ
# 撤退基準の 180 秒（§7）を超えたら打ち切って利用者に状況を伝える。
OLLAMA_TIMEOUT_SEC = _env_int("OLLAMA_TIMEOUT_SEC", 180)
# 事実性重視のため温度は 0（出典に基づく回答で創造性は不要）。
OLLAMA_TEMPERATURE = _env_float("OLLAMA_TEMPERATURE", 0.0)
# コンテキスト長: 512トークン×5チャンク＋プロンプト＋回答分を確保する。
OLLAMA_NUM_CTX = _env_int("OLLAMA_NUM_CTX", 8192)

# ---------------------------------------------------------------------------
# 回答仕様（指示文書 §10 Phase 4）
# ---------------------------------------------------------------------------
# 該当情報が無い場合に返す文言。評価スクリプトの拒否判定にも使うため一字一句固定。
REFUSAL_MESSAGE = "資料内に該当する情報が見つかりませんでした"


def has_gpu() -> bool:
    """CUDA GPU が利用可能かを判定する。

    埋め込み・再ランクのデバイス選択と、Ollama モデルのフォールバック判定
    （§4: GPU無しなら qwen3:4b）の両方で使うため config に置く。
    """
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


def embedding_device() -> str:
    """sentence-transformers に渡すデバイス名。"""
    return "cuda" if has_gpu() else "cpu"


def resolve_ollama_model() -> str:
    """使用する Ollama モデル名を決める。

    GPU があれば qwen3:8b、無ければ qwen3:4b（指示文書 §4 の自動フォールバック）。
    環境変数 OLLAMA_MODEL_FORCE が指定されていれば検証・デモ用にそれを優先する。
    """
    forced = os.environ.get("OLLAMA_MODEL_FORCE", "")
    if forced:
        return forced
    return OLLAMA_MODEL if has_gpu() else OLLAMA_FALLBACK_MODEL


if __name__ == "__main__":
    # `python -m src.config` で現在の設定を確認できるようにする（§11: 単体実行可能）
    print("=== local-rag-poc 設定 ===")
    print(f"PROJECT_ROOT          : {PROJECT_ROOT}")
    print(f"CORPUS_DIR            : {CORPUS_DIR}")
    print(f"CHROMA_DIR            : {CHROMA_DIR}")
    print(f"EMBED_MODEL_NAME      : {EMBED_MODEL_NAME}")
    print(f"RERANK_MODEL_NAME     : {RERANK_MODEL_NAME}")
    print(f"CHUNK_SIZE_TOKENS     : {CHUNK_SIZE_TOKENS}")
    print(f"CHUNK_OVERLAP_TOKENS  : {CHUNK_OVERLAP_TOKENS}")
    print(f"TOP_K_EMBED           : {TOP_K_EMBED}")
    print(f"TOP_K_RERANK          : {TOP_K_RERANK}")
    print(f"RERANK_SCORE_THRESHOLD: {RERANK_SCORE_THRESHOLD}")
    print(f"OLLAMA_HOST           : {OLLAMA_HOST}")
    print(f"GPU利用可否           : {has_gpu()}")
    print(f"使用モデル（解決後）  : {resolve_ollama_model()}")
