"""2段検索モジュール（1段目: 埋め込み検索 → 2段目: 再ランク）。

日本語の埋め込みモデルだけでは細かい言い回しの違いで順位が揺れるため、
1段目（ruri-v3 + ChromaDB）で広めに候補を取り（Top-50）、2段目の
CrossEncoder（bge-reranker-v2-m3）でクエリとチャンクを直接突き合わせて
絞り込む（Top-5）2段構成にしている（指示文書 §1・§5）。

単体実行: python -m src.retrieve "質問文"
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from typing import TypedDict

# 依存パッケージ未導入のまま実行した利用者に、素の ImportError ではなく
# 復旧手順を示すため、ここでまとめて捕捉する（§11: 対処法つきで表示）。
try:
    import numpy as np
    import torch
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import CrossEncoder, SentenceTransformer
except ImportError as exc:  # pragma: no cover - 環境不備時のみ
    raise ImportError(
        f"依存パッケージが見つかりません（{exc.name}）"
        "→ venv を有効化し `pip install -r requirements.txt` を実行してください"
    ) from exc

from src import config

logger = logging.getLogger(__name__)

# CLI 表示でチャンク本文を先頭何文字まで見せるか。
# 検索精度に影響しない純粋な表示都合の値のため config ではなくここに置く
# （config は調整対象のパラメータのみを集約する方針）。
_CLI_TEXT_PREVIEW_CHARS = 80

# コーパス未投入時の案内文。CLI と例外メッセージで共通に使う。
_INGEST_GUIDANCE = (
    "検索対象のコーパスがまだ投入されていません "
    "→ 先に `python -m src.ingest` を実行してください"
)


class Hit(TypedDict):
    """検索ヒット1件（モジュール間コントラクトで固定の形状）。"""

    chunk_id: str  # 例 "manual.pdf:p3:c2"
    file: str  # ファイル名のみ（パスではない）
    page: int  # 1始まり。テキストファイルは 1 固定
    score: float  # bge-reranker の sigmoid 後スコア（0〜1）
    embed_score: float  # 1段目の cosine 類似度（1.0 - cosine距離）
    text: str  # プレフィックスを除いた素のチャンク本文


class CorpusNotIngestedError(RuntimeError):
    """コーパス未投入（コレクションが無い/空）を表す例外。

    呼び出し側（generate.py / app.py）が「エラー」ではなく「先に ingest を」
    という案内に変換できるよう、専用の型で区別する。
    """


class Retriever:
    """2段検索を実行するクラス。

    埋め込みモデルと reranker のロードは数十秒かかることがあるため、
    インスタンス生成時に一度だけロードして保持する（UI 側は
    st.cache_resource でこのインスタンスを使い回す想定）。
    """

    def __init__(self) -> None:
        device = config.embedding_device()
        logger.info("モデルロード開始（device=%s）", device)

        # --- 1段目: 埋め込みモデル（ruri-v3） ---
        t0 = time.perf_counter()
        try:
            self._embedder = SentenceTransformer(config.EMBED_MODEL_NAME, device=device)
        except Exception as exc:
            raise RuntimeError(
                f"埋め込みモデル {config.EMBED_MODEL_NAME} のロードに失敗しました "
                "→ 初回はモデルのダウンロードにネットワーク接続が必要です。"
                "接続を確認して再実行してください（2回目以降はローカルキャッシュで動作します）"
            ) from exc
        embed_load_sec = time.perf_counter() - t0
        logger.info(
            "埋め込みモデル %s ロード完了（%.1f秒）",
            config.EMBED_MODEL_NAME,
            embed_load_sec,
        )

        # --- 2段目: reranker（bge-reranker-v2-m3） ---
        # 拒否判定（generate.py の RERANK_SCORE_THRESHOLD）が「0〜1 のスコア」
        # 前提のため、活性化関数に sigmoid を明示指定する。
        t0 = time.perf_counter()
        try:
            try:
                self._reranker = CrossEncoder(
                    config.RERANK_MODEL_NAME,
                    device=device,
                    activation_fn=torch.nn.Sigmoid(),
                )
            except TypeError:
                # 旧版 sentence-transformers は引数名が異なる。1ラベルの
                # reranker には既定で sigmoid が適用される仕様のため、
                # 既定構築へフォールバックする（search() 側でも範囲を検証）。
                self._reranker = CrossEncoder(config.RERANK_MODEL_NAME, device=device)
        except Exception as exc:
            raise RuntimeError(
                f"再ランクモデル {config.RERANK_MODEL_NAME} のロードに失敗しました "
                "→ 初回はモデルのダウンロードにネットワーク接続が必要です。"
                "接続を確認して再実行してください（2回目以降はローカルキャッシュで動作します）"
            ) from exc
        rerank_load_sec = time.perf_counter() - t0
        logger.info(
            "再ランクモデル %s ロード完了（%.1f秒）",
            config.RERANK_MODEL_NAME,
            rerank_load_sec,
        )

        # --- ベクタDB（ChromaDB ローカル永続化） ---
        # anonymized_telemetry を切るのは、機内モードでも動作すること（指示文書
        # §2）が要件で、外部への通信要素を残さないため。
        self._client = chromadb.PersistentClient(
            path=str(config.CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )

    def _get_collection(self):
        """コレクションを取得する。未作成なら案内つき例外を送出する。

        ingest.py は再実行時にコレクションを削除して作り直すため、ここで
        ハンドルを保持し続けると（UI 起動中に再インジェストした場合など）
        古いコレクションを指したままになる。取得は軽い操作なので、
        検索のたびに取り直して常に最新を見る。
        """
        try:
            return self._client.get_collection(config.CHROMA_COLLECTION_NAME)
        except Exception as exc:
            # chromadb はバージョンにより送出する例外型が異なる（ValueError /
            # NotFoundError 等）ため、型ではなく「取得できない＝未投入」として扱う。
            raise CorpusNotIngestedError(_INGEST_GUIDANCE) from exc

    def search(
        self,
        query: str,
        top_k_embed: int | None = None,
        top_k_rerank: int | None = None,
    ) -> list[Hit]:
        """2段検索を実行し、rerank スコア降順の Hit リストを返す。

        Args:
            query: 質問文（プレフィックスなしの素のテキストを渡す）。
            top_k_embed: 1段目の候補件数（省略時 config.TOP_K_EMBED）。
            top_k_rerank: 最終返却件数（省略時 config.TOP_K_RERANK）。
        """
        if not query or not query.strip():
            raise ValueError("質問文が空です → 検索したい質問文を指定してください")

        k_embed = top_k_embed if top_k_embed is not None else config.TOP_K_EMBED
        k_rerank = top_k_rerank if top_k_rerank is not None else config.TOP_K_RERANK

        collection = self._get_collection()
        total_chunks = collection.count()
        if total_chunks == 0:
            # コレクションだけ存在して中身が空のケース（ingest 途中失敗など）
            raise CorpusNotIngestedError(_INGEST_GUIDANCE)

        t_start = time.perf_counter()

        # --- 1段目: 埋め込み検索 ---
        # ruri-v3 はプレフィックス方式で学習されており、クエリ側に
        # EMBED_QUERY_PREFIX を付けないと精度が大きく落ちる（config 参照）。
        query_vec = self._embedder.encode(
            config.EMBED_QUERY_PREFIX + query,
            convert_to_numpy=True,
        )
        t_embed = time.perf_counter()

        # 登録チャンク数より多く要求すると chromadb が警告/エラーを出す
        # バージョンがあるため、実在数で頭打ちにする。
        n_results = min(k_embed, total_chunks)
        result = collection.query(
            query_embeddings=[query_vec.tolist()],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        t_query = time.perf_counter()

        ids = result["ids"][0]
        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]

        if not ids:
            logger.info("1段目の候補が 0 件でした（query=%r）", query)
            return []

        # --- 2段目: CrossEncoder による再評価 ---
        # reranker はクエリと文書を直接突き合わせるモデルであり、ruri-v3 用の
        # プレフィックスを付けると学習時と異なる入力になるため、素のテキスト
        # 同士のペアを渡す（コントラクト指定）。
        pairs = [(query, doc) for doc in documents]
        raw_scores = self._reranker.predict(pairs, show_progress_bar=False)
        scores = np.asarray(raw_scores, dtype=np.float64)

        # sigmoid が適用されていれば必ず 0〜1 に収まる。範囲外の値があれば
        # 生ロジットが返ってきている（旧版フォールバック時など）ので、閾値
        # 判定の前提を守るためにここで sigmoid を適用する。sigmoid は単調
        # 増加なので順位は変わらない。
        if scores.size and (scores.min() < 0.0 or scores.max() > 1.0):
            logger.warning(
                "reranker が生ロジットを返したため sigmoid を適用します"
                "（min=%.3f, max=%.3f）",
                scores.min(),
                scores.max(),
            )
            with np.errstate(over="ignore"):  # 大きな負ロジットの exp あふれは 0 に収束するだけ
                scores = 1.0 / (1.0 + np.exp(-scores))

        order = np.argsort(-scores)[:k_rerank]
        hits: list[Hit] = []
        for idx in order:
            meta = metadatas[idx] or {}
            hits.append(
                Hit(
                    chunk_id=str(ids[idx]),
                    file=str(meta.get("file", "")),
                    page=int(meta.get("page", 1)),
                    score=float(scores[idx]),
                    # chroma の distance は cosine 距離（hnsw:space=cosine）なので
                    # 類似度へは 1.0 - distance で変換する（コントラクト指定）。
                    embed_score=float(1.0 - distances[idx]),
                    text=str(documents[idx]),
                )
            )
        t_end = time.perf_counter()

        logger.info(
            "検索完了: 候補 %d 件 → 上位 %d 件（埋め込み %.2f秒 / DB検索 %.2f秒 / "
            "再ランク %.2f秒 / 合計 %.2f秒）",
            len(ids),
            len(hits),
            t_embed - t_start,
            t_query - t_embed,
            t_end - t_query,
            t_end - t_start,
        )
        return hits


# ---------------------------------------------------------------------------
# モジュールレベルの便宜関数
# ---------------------------------------------------------------------------
# モデルロードが重いため、モジュール内でシングルトンを使い回す。
# UI（Streamlit）は st.cache_resource で独自にインスタンス管理するので、
# こちらは CLI・評価スクリプトなどの単発利用向け。
_default_retriever: Retriever | None = None


def get_retriever() -> Retriever:
    """シングルトンの Retriever を返す（初回呼び出し時にロード）。"""
    global _default_retriever
    if _default_retriever is None:
        _default_retriever = Retriever()
    return _default_retriever


def search(
    query: str,
    top_k_embed: int | None = None,
    top_k_rerank: int | None = None,
) -> list[Hit]:
    """Retriever.search のモジュールレベル版（シングルトン利用）。"""
    return get_retriever().search(
        query, top_k_embed=top_k_embed, top_k_rerank=top_k_rerank
    )


# ---------------------------------------------------------------------------
# CLI（§11: 各モジュールは単体実行可能にする）
# ---------------------------------------------------------------------------
def _format_hit(rank: int, hit: Hit) -> str:
    """CLI 用にヒット1件を整形する。"""
    preview = hit["text"].replace("\n", " ")
    if len(preview) > _CLI_TEXT_PREVIEW_CHARS:
        preview = preview[:_CLI_TEXT_PREVIEW_CHARS] + "…"
    return (
        f"[{rank}] score={hit['score']:.3f} embed={hit['embed_score']:.3f} | "
        f"{hit['file']} p.{hit['page']} | {hit['chunk_id']}\n"
        f"    {preview}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m src.retrieve",
        description="2段検索（embedding → rerank）を CLI で試す",
    )
    parser.add_argument("query", help="検索する質問文")
    parser.add_argument(
        "--top-k-embed",
        type=int,
        default=None,
        help=f"1段目の候補件数（既定: {config.TOP_K_EMBED}）",
    )
    parser.add_argument(
        "--top-k-rerank",
        type=int,
        default=None,
        help=f"最終返却件数（既定: {config.TOP_K_RERANK}）",
    )
    args = parser.parse_args(argv)

    # モデルロード時間・検索所要時間を利用者にも見せたいので INFO で出す
    # （応答時間は面接デモの説明材料になるため）。
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    t_start = time.perf_counter()
    try:
        hits = search(
            args.query,
            top_k_embed=args.top_k_embed,
            top_k_rerank=args.top_k_rerank,
        )
    except CorpusNotIngestedError as exc:
        print(f"[エラー] {exc}")
        return 1
    except (ValueError, RuntimeError) as exc:
        # モデルロード失敗・空クエリなど。対処法はメッセージ側に含めてある。
        print(f"[エラー] {exc}")
        return 1
    elapsed = time.perf_counter() - t_start

    if not hits:
        print("検索結果が 0 件でした（コーパスの内容と質問が噛み合っていない可能性があります）")
        return 0

    print(f'\n=== 検索結果: "{args.query}"（上位 {len(hits)} 件 / 合計 {elapsed:.1f}秒）===')
    for rank, hit in enumerate(hits, start=1):
        print(_format_hit(rank, hit))
    # 拒否判定の閾値を併記しておくと、CLI だけでも「この質問は該当なし扱いに
    # なるか」を確認でき、パラメータ調整（§7 の3回ルール）の判断材料になる。
    print(
        f"\n参考: 拒否判定の閾値 RERANK_SCORE_THRESHOLD = "
        f"{config.RERANK_SCORE_THRESHOLD}（全件がこれ未満なら generate 側で拒否）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
