"""Streamlit UI（指示文書 §10 Phase 5）。

起動方法:
    streamlit run src/app.py

チャット欄＋履歴、出典（クリックでチャンク全文展開）、サイドバーに
モデル名・Top-K・拒否閾値・応答時間の内訳・コーパス統計を表示する。
応答時間の表示は面接デモ要件（指示文書 §10 Phase 5）のため必須。
"""

import logging
import sys
import time
from pathlib import Path

# streamlit run src/app.py はカレントディレクトリ基準で実行されるため、
# `from src import ...` が解決できるようプロジェクトルートを sys.path に
# 追加してから import する（コントラクト指定。相対 import 破壊の防止）。
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import chromadb
import requests
import streamlit as st
from chromadb.config import Settings

from src import config, generate, retrieve

# ---------------------------------------------------------------------------
# UI 固有の定数
# ---------------------------------------------------------------------------
# 以下はスライダーの可動域や表示調整であり、検索仕様の既定値（config が管理）
# ではない。config.py は確定済み・変更禁止のため、UI 都合の値は名前付き定数
# としてここに置く（マジックナンバー直書き禁止の趣旨は名前と根拠で満たす）。

# Top-K（1段目）: 下限は「reranker に最低限の候補を渡せる件数」、上限は
# CPU-only 環境で再ランク時間が実用範囲に収まる程度に抑える。
_TOP_K_EMBED_MIN = 5
_TOP_K_EMBED_MAX = 100
_TOP_K_EMBED_STEP = 5
# Top-K（2段目）: 出典として画面に並べて確認できる件数の範囲。
_TOP_K_RERANK_MIN = 1
_TOP_K_RERANK_MAX = 20
# 拒否閾値: rerank スコアは sigmoid 後の 0〜1 に正規化されている（コントラクト）。
_THRESHOLD_MIN = 0.0
_THRESHOLD_MAX = 1.0
_THRESHOLD_STEP = 0.05
# Ollama の死活確認はチャット応答と違い軽い API なので、画面描画を
# 待たせないよう短いタイムアウトで打ち切る。
_OLLAMA_STATUS_TIMEOUT_SEC = 2.0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# リソースのロード（モデルは重いので 1 回だけ）
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="埋め込み・再ランクモデルをロード中…（初回は数十秒かかります）")
def load_retriever() -> retrieve.Retriever:
    """Retriever（埋め込み＋reranker＋ChromaDB クライアント）を 1 回だけ構築する。

    st.cache_resource を使うのは、Streamlit が操作のたびにスクリプト全体を
    再実行する設計であり、素直に書くと毎回数十秒のモデルロードが走るため。
    ロード失敗時は例外がキャッシュされない（次の再実行で再試行できる）。
    """
    return retrieve.Retriever()


def get_chunk_count() -> int | None:
    """コーパスのチャンク数を返す。未投入（コレクション無し）なら None。

    Retriever とは別にここでも ChromaDB を開くのは、モデルロードに失敗した
    状態でもコーパス統計と未投入警告を表示できるようにするため。設定を
    Retriever 側と完全に一致させているのは、chromadb が同一パスに異なる
    設定のクライアントを作ることを拒否するため。
    """
    try:
        client = chromadb.PersistentClient(
            path=str(config.CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
        collection = client.get_collection(config.CHROMA_COLLECTION_NAME)
        return collection.count()
    except Exception:
        # コレクションが無い＝未投入。呼び出し側で対処法つき警告に変換する
        # ため、ここでは None を返すだけにする（例外型が chromadb の
        # バージョンで異なるため型では判別しない）。
        return None


def check_ollama() -> tuple[bool, list[str]]:
    """Ollama の死活と取得済みモデル一覧を返す。

    チャット送信前に画面へ警告を出すための事前チェック。ここで失敗しても
    例外にせず (False, []) を返すのは、「Ollama 未起動でも UI 自体は落とさず
    対処法を表示する」というコントラクト要件のため。
    """
    try:
        resp = requests.get(
            f"{config.OLLAMA_HOST}/api/tags", timeout=_OLLAMA_STATUS_TIMEOUT_SEC
        )
        resp.raise_for_status()
        models = [m.get("name", "") for m in resp.json().get("models", [])]
        return True, models
    except Exception as exc:
        logger.warning("Ollama への接続確認に失敗: %s", exc)
        return False, []


def _normalize_model_name(name: str) -> str:
    """タグ無しモデル名を Ollama の一覧表記（:latest 付き）へ揃える。"""
    return name if ":" in name else f"{name}:latest"


def _model_in_tags(name: str, tags: list[str]) -> bool:
    return _normalize_model_name(name) in {_normalize_model_name(t) for t in tags}


def _clamp(value: int | float, low: int | float, high: int | float) -> int | float:
    """スライダー初期値を可動域に収める。

    config の値は環境変数で上書きできるため、可動域外の初期値を渡して
    Streamlit が例外で落ちるのを防ぐ。
    """
    return max(low, min(high, value))


# ---------------------------------------------------------------------------
# 描画部品
# ---------------------------------------------------------------------------
def render_timing(container, ans: dict | None) -> None:
    """直近の応答時間（合計・検索・生成）をサイドバーに描画する。

    面接デモ必須要件（指示文書 §10 Phase 5）。回答完了後に同じ placeholder を
    上書きすることで、サイドバーを先に描画しても最新値が反映される。
    """
    with container.container():
        st.subheader("直近の応答時間")
        if ans is None:
            st.caption("まだ質問がありません")
            return
        st.metric("合計", f"{ans['elapsed_sec']:.1f} 秒")
        st.metric("検索（embedding + rerank）", f"{ans['retrieval_sec']:.1f} 秒")
        st.metric("生成（LLM）", f"{ans['generation_sec']:.1f} 秒")
        st.caption(f"使用モデル: {ans['model']}")


def _hits_for_source(hits: list[dict], src: dict) -> list[dict]:
    """出典（file+page）に対応するチャンクを検索ヒットから引き当てる。"""
    return [
        h for h in hits if h["file"] == src["file"] and h["page"] == src["page"]
    ]


def render_answer(ans: dict) -> None:
    """回答1件（本文＋出典展開）を描画する。履歴の再描画にも使う。"""
    # 拒否時は REFUSAL_MESSAGE がそのまま answer に入っている（コントラクト）。
    st.markdown(ans["answer"])
    st.caption(
        f"応答 {ans['elapsed_sec']:.1f} 秒"
        f"（検索 {ans['retrieval_sec']:.1f} 秒 / 生成 {ans['generation_sec']:.1f} 秒）"
        f"・モデル: {ans['model']}"
    )

    if ans["refused"]:
        # 拒否時も検索ヒット自体は残っている（コントラクト）。なぜ拒否に
        # なったか（全ヒットが閾値未満）をデモで説明できるよう参考表示する。
        if ans["hits"]:
            with st.expander("参考: 閾値未満だった検索結果（回答には使用していません）"):
                for hit in ans["hits"]:
                    st.caption(
                        f"{hit['file']} p.{hit['page']}"
                        f"（rerank {hit['score']:.3f} / embed {hit['embed_score']:.3f}）"
                    )
                    st.text(hit["text"])
        return

    # 出典は generate.py がコード側で実ヒットから構築した sources を使う
    # （LLM の捏造出典を表示しないため）。各出典はクリックで全文展開。
    if ans["sources"]:
        st.markdown("**出典**")
        for i, src in enumerate(ans["sources"], start=1):
            with st.expander(f"[{i}] {src['file']} p.{src['page']}"):
                matched = _hits_for_source(ans["hits"], src)
                if not matched:
                    st.caption("該当チャンクの本文を取得できませんでした")
                    continue
                for hit in matched:
                    st.caption(
                        f"{hit['chunk_id']}"
                        f"（rerank {hit['score']:.3f} / embed {hit['embed_score']:.3f}）"
                    )
                    st.text(hit["text"])


def render_history() -> None:
    """st.session_state に積んだ会話履歴を描画する。

    Streamlit は操作のたびに全体を再実行するため、履歴を state に持たないと
    過去の回答（出典展開含む）が消えてしまう。
    """
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            elif msg.get("kind") == "error":
                st.error(msg["content"])
            else:
                render_answer(msg["answer"])


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------
def main() -> None:
    st.set_page_config(page_title="社内ナレッジRAG PoC", layout="wide")
    st.title("社内ナレッジRAGチャットボット（PoC）")
    st.caption("完全ローカル構成（外部APIなし）・出典付き回答")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_answer" not in st.session_state:
        st.session_state.last_answer = None

    # --- 事前チェック（例外で落とさず、対処法つきで画面に出す） ---
    chunk_count = get_chunk_count()
    ollama_ok, ollama_tags = check_ollama()
    resolved_model = config.resolve_ollama_model()

    if chunk_count is None or chunk_count == 0:
        st.warning(
            "コーパスが未投入です → `data/corpus/` に資料（PDF/テキスト）を置き、"
            "先に `python -m src.ingest` を実行してください"
        )
    if not ollama_ok:
        st.warning(
            "Ollamaに接続できません → `ollama serve` が起動しているか、"
            f"OLLAMA_HOST の設定（現在: {config.OLLAMA_HOST}）を確認してください"
        )
    elif not _model_in_tags(resolved_model, ollama_tags):
        if _model_in_tags(config.OLLAMA_FALLBACK_MODEL, ollama_tags):
            # モデル解決は generate.py が /api/tags を見て行うため、ここは
            # 利用者が驚かないよう事前に知らせるだけにする。
            st.info(
                f"モデル {resolved_model} が未取得のため、"
                f"フォールバックモデル {config.OLLAMA_FALLBACK_MODEL} を使用します"
            )
        else:
            st.warning(
                f"モデル {resolved_model} が Ollama に取得されていません → "
                f"`ollama pull {resolved_model}` を実行してください"
            )

    # --- モデルロード（失敗しても UI は落とさない） ---
    retriever = None
    load_error: str | None = None
    try:
        retriever = load_retriever()
    except RuntimeError as exc:
        # Retriever は利用者向け対処法つきのメッセージを組み立てて送出する
        # ので、そのまま表示する。
        load_error = str(exc)
    except Exception as exc:  # noqa: BLE001
        logger.exception("モデルロードで予期しないエラー")
        load_error = (
            f"モデルのロードで予期しないエラーが発生しました（{exc}）→ "
            "ターミナルのログを確認し、依存パッケージ（requirements.txt）が"
            "インストール済みか確認してください"
        )
    if load_error:
        st.error(load_error)

    # --- サイドバー ---
    with st.sidebar:
        st.header("設定")

        st.markdown(f"**使用モデル（解決後）**: `{resolved_model}`")
        st.caption(
            f"GPU: {'あり' if config.has_gpu() else 'なし（CPUモード）'} / "
            f"埋め込み: {config.EMBED_MODEL_NAME} / "
            f"再ランク: {config.RERANK_MODEL_NAME}"
        )

        top_k_embed = st.slider(
            "Top-K（1段目: embedding 検索）",
            min_value=_TOP_K_EMBED_MIN,
            max_value=_TOP_K_EMBED_MAX,
            value=int(_clamp(config.TOP_K_EMBED, _TOP_K_EMBED_MIN, _TOP_K_EMBED_MAX)),
            step=_TOP_K_EMBED_STEP,
        )
        top_k_rerank = st.slider(
            "Top-K（2段目: rerank 後）",
            min_value=_TOP_K_RERANK_MIN,
            max_value=_TOP_K_RERANK_MAX,
            value=int(
                _clamp(config.TOP_K_RERANK, _TOP_K_RERANK_MIN, _TOP_K_RERANK_MAX)
            ),
        )
        threshold = st.slider(
            "拒否閾値（rerank スコア）",
            min_value=_THRESHOLD_MIN,
            max_value=_THRESHOLD_MAX,
            value=float(
                _clamp(config.RERANK_SCORE_THRESHOLD, _THRESHOLD_MIN, _THRESHOLD_MAX)
            ),
            step=_THRESHOLD_STEP,
            help="全ヒットのスコアがこの値未満なら「資料内に該当なし」として回答を拒否します",
        )

        # 応答完了後に上書きできるよう placeholder にしておく（サイドバーは
        # 本文より先に描画されるため、素直に書くと1操作遅れの値になる）。
        timing_placeholder = st.empty()
        render_timing(timing_placeholder, st.session_state.last_answer)

        st.subheader("コーパス統計")
        if chunk_count is None:
            st.caption("未投入（`python -m src.ingest` を実行してください）")
        else:
            st.metric("チャンク数", f"{chunk_count:,}")

    # --- 会話履歴 ---
    render_history()

    # --- 入力と応答 ---
    prompt = st.chat_input(
        "資料への質問を入力してください",
        disabled=retriever is None,
    )
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("検索と回答生成を実行中…（CPU環境では時間がかかります）"):
            try:
                # コントラクトで generate.answer() のシグネチャは
                # (query, retriever) に固定されており Top-K を渡す口が無い。
                # 一方 retrieve.search() は呼び出し時に config のモジュール属性を
                # 参照する仕様（全モジュール共通ルール: from src import config 経由）
                # のため、サイドバーの値を実行時属性として上書きして反映する。
                # config.py ファイル自体は変更しない。
                config.TOP_K_EMBED = int(top_k_embed)
                config.TOP_K_RERANK = int(top_k_rerank)
                config.RERANK_SCORE_THRESHOLD = float(threshold)

                t0 = time.perf_counter()
                ans = generate.answer(prompt, retriever=retriever)
                logger.info(
                    "回答完了: refused=%s / 合計 %.1f秒（検索 %.1f秒 / 生成 %.1f秒）"
                    "/ 出典 %d 件 / モデル %s / UI往復 %.1f秒",
                    ans["refused"],
                    ans["elapsed_sec"],
                    ans["retrieval_sec"],
                    ans["generation_sec"],
                    len(ans["sources"]),
                    ans["model"],
                    time.perf_counter() - t0,
                )
            except retrieve.CorpusNotIngestedError as exc:
                # コーパス未投入はエラー画面にせず案内で返す（コントラクト）。
                _record_error(str(exc))
                return
            except RuntimeError as exc:
                # generate.py が対処法つきメッセージを組み立てている
                # （Ollama 未起動 / モデル未取得 / タイムアウト）。
                _record_error(str(exc))
                return
            except Exception as exc:  # noqa: BLE001
                logger.exception("回答生成で予期しないエラー")
                _record_error(
                    f"予期しないエラーが発生しました（{exc}）→ "
                    "ターミナルのログを確認してください"
                )
                return

        render_answer(ans)

    st.session_state.messages.append(
        {"role": "assistant", "kind": "answer", "answer": ans}
    )
    st.session_state.last_answer = ans
    # サイドバーの「直近の応答時間」を今回の値で更新（面接デモ要件）。
    render_timing(timing_placeholder, ans)


def _record_error(message: str) -> None:
    """エラーを表示しつつ履歴にも残す。

    履歴に残すのは、Streamlit の再実行で表示が消えると利用者が
    「何が起きたか」を追えなくなるため。
    """
    st.error(message)
    st.session_state.messages.append(
        {"role": "assistant", "kind": "error", "content": message}
    )
    logger.error("利用者向けエラー表示: %s", message)


if __name__ == "__main__":
    # streamlit run はスクリプトを __main__ として実行するため、ここが入口になる。
    main()
