"""取り込み・チャンク分割・ベクトル化モジュール。

data/corpus 配下（再帰）の PDF / .txt / .md を読み込み、
ページ単位でテキスト抽出 → ruri-v3 トークナイザ基準のスライディングウィンドウ分割
→ sentence-transformers で埋め込み → ChromaDB（cosine）へ格納する。

単体実行: `python -m src.ingest`
"""

import logging
import sys
import time
import unicodedata
from pathlib import Path

from src import config

logger = logging.getLogger(__name__)

# 取り込み対象の拡張子は config.TARGET_EXTENSIONS を参照する（評価スクリプトの
# プレースホルダ検出と判定基準がずれないよう、二重定義を避けて一元管理）。

# ---------------------------------------------------------------------------
# PDF テキスト「崩壊」判定のしきい値。
# config.py は確定済み（変更禁止）でここに定数が無いため、モジュール内の
# 名前付き定数として定義する（マジックナンバーの直書き回避）。
# ---------------------------------------------------------------------------
# U+FFFD（文字化けの置換文字）がこの割合を超えるページは抽出失敗とみなす。
# 経験的に正常な日本語PDFではほぼ 0 になるため、少量でも異常のシグナルになる。
REPLACEMENT_CHAR_RATIO_THRESHOLD = 0.05
# "(cid:NN)" は CID フォントのデコード失敗時に pypdf が出す典型パターン。
# 数回出ただけで本文の可読性が失われるため、少数でもフォールバック対象とする。
CID_PATTERN_COUNT_THRESHOLD = 3
# テキストファイルの文字コード候補。corpus は Windows 環境（仕様書 §3）で
# 作られる可能性が高く、UTF-8 で読めない場合は CP932 を試す。
# "utf-8" ではなく "utf-8-sig" にするのは、メモ帳等が付ける UTF-8 BOM
# （U+FEFF）を除去して先頭チャンクへの混入を防ぐため（utf-8-sig は
# BOM 無しの UTF-8 もそのまま正しく読める）。
TEXT_ENCODING_CANDIDATES = ("utf-8-sig", "cp932")
# ChromaDB への一括 add の上限（バージョンにより上限クエリ API が無いことが
# あるため、安全側のフォールバック値。get_max_batch_size があればそちらを優先）。
CHROMA_ADD_BATCH_FALLBACK = 1000


# ---------------------------------------------------------------------------
# テキスト抽出
# ---------------------------------------------------------------------------
def _is_degraded_text(text: str) -> str | None:
    """抽出テキストが空・崩壊していれば理由文字列を返す（正常なら None）。

    「崩壊」の代表例は、埋め込みフォントのマッピング欠落による
    置換文字（U+FFFD）だらけの出力や "(cid:NN)" の羅列。
    これらは埋め込み・検索の対象にしても精度を下げるだけなので、
    レイアウト解析ベースの pdfplumber での再抽出トリガーにする。
    """
    stripped = text.strip()
    if not stripped:
        return "抽出テキストが空"
    replacement_ratio = stripped.count("�") / len(stripped)
    if replacement_ratio >= REPLACEMENT_CHAR_RATIO_THRESHOLD:
        return f"置換文字(U+FFFD)比率 {replacement_ratio:.1%} で文字化けと判定"
    if stripped.count("(cid:") >= CID_PATTERN_COUNT_THRESHOLD:
        return "CIDフォントのデコード失敗パターン '(cid:' を多数検出"
    return None


def _extract_pdf_with_pypdf(path: Path) -> list[tuple[int, str]]:
    """pypdf でページ単位抽出。戻り値は [(1始まりページ番号, テキスト)]。

    出典表示（仕様書 §1: ファイル名＋ページ番号を必ず添える）のため、
    ページ番号は抽出時点で確定させてメタデータまで持ち回る。
    """
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages: list[tuple[int, str]] = []
    for i, page in enumerate(reader.pages, start=1):
        # ページ単位の抽出失敗は「崩壊」と同列に扱い、後段のフォールバック
        # 判定に委ねる（1ページの失敗でファイル全体を落とさないため）。
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # noqa: BLE001
            logger.warning("%s p.%d: pypdf 抽出でエラー（%s）。空ページ扱いにします", path.name, i, exc)
            text = ""
        pages.append((i, text))
    return pages


def _extract_pdf_with_pdfplumber(path: Path) -> list[tuple[int, str]]:
    """pdfplumber でページ単位抽出（pypdf が空/崩壊を返した場合のフォールバック）。

    pdfplumber は文字座標からレイアウトを再構成するため、pypdf が苦手とする
    表組み・特殊フォントの PDF でもテキストを拾えることがある（仕様書 §4）。
    """
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError(
            "pdfplumber がインストールされていません → "
            "`pip install -r requirements.txt` を実行してください"
        ) from exc

    pages: list[tuple[int, str]] = []
    with pdfplumber.open(str(path)) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages.append((i, text))
    return pages


def _extract_pdf(path: Path) -> list[tuple[int, str]]:
    """PDF からページ単位でテキストを抽出する。

    まず高速な pypdf を試し、空ページ・崩壊ページが1つでもあれば
    ファイル単位で pdfplumber に切り替える（コントラクト指定）。
    ページ単位の混在にしないのは、同一ファイル内で抽出器が変わると
    ページ間の表記ゆれが生じ、チャンク品質の切り分けが難しくなるため。
    """
    pages = _extract_pdf_with_pypdf(path)
    degraded_reasons = []
    for page_no, text in pages:
        reason = _is_degraded_text(text)
        if reason:
            degraded_reasons.append(f"p.{page_no}: {reason}")
    if degraded_reasons:
        logger.info(
            "%s: pypdf の抽出結果に問題があるため pdfplumber へフォールバックします（%s）",
            path.name,
            " / ".join(degraded_reasons[:3]) + ("" if len(degraded_reasons) <= 3 else f" 他{len(degraded_reasons) - 3}件"),
        )
        pages = _extract_pdf_with_pdfplumber(path)
    return pages


def _extract_text_file(path: Path) -> list[tuple[int, str]]:
    """テキスト/Markdown を読み込む。ページ概念が無いため p.1 固定（コントラクト）。"""
    last_error: Exception | None = None
    for encoding in TEXT_ENCODING_CANDIDATES:
        try:
            text = path.read_text(encoding=encoding)
            return [(1, text)]
        except UnicodeDecodeError as exc:
            last_error = exc
    raise RuntimeError(
        f"文字コードを判別できません（{'/'.join(TEXT_ENCODING_CANDIDATES)} を試行）→ "
        f"UTF-8 で保存し直してください: {path.name}"
    ) from last_error


def _extract_file(path: Path) -> list[tuple[int, str]]:
    """拡張子に応じてページ単位のテキストを抽出する。"""
    if path.suffix.lower() == ".pdf":
        return _extract_pdf(path)
    return _extract_text_file(path)


# ---------------------------------------------------------------------------
# テキスト正規化
# ---------------------------------------------------------------------------
def normalize_text(text: str) -> str:
    """NFKC 正規化＋連続空白の圧縮を行う（stdlib のみに依存）。

    文書側（ingest のチャンク化）とクエリ側（retrieve.search）の両方が
    この同じ関数を通ることで表記を揃える。片側だけ正規化すると、
    全角英数字・全角記号（例:「ＡＢＣ規格」）を含む質問で文書側と
    表記がずれ、埋め込み類似度が不当に下がるため。
    改行過多・連続空白の圧縮は埋め込みトークンの浪費を防ぐ目的もある。
    """
    return " ".join(unicodedata.normalize("NFKC", text).split())


# ---------------------------------------------------------------------------
# チャンク分割
# ---------------------------------------------------------------------------
# decode 後のチャンクに「元テキストに無い U+FFFD」を検出済みかどうか。
# トークン境界での多バイト文字分断は全チャンクで同様に起き得るため、
# 警告はプロセスあたり1回に抑えてログを埋めない（軽量チェック）。
_warned_token_boundary_mojibake = False


def _load_tokenizer():
    """ruri-v3 のトークナイザをロードする。

    チャンクのトークン数を「埋め込みモデルが実際に消費する単位」で数える
    ため、汎用トークナイザではなく埋め込みモデル自身のものを使う
    （config.py のチャンク設定コメントと同じ理由）。
    """
    try:
        from transformers import AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "transformers がインストールされていません → "
            "`pip install -r requirements.txt` を実行してください"
        ) from exc
    try:
        return AutoTokenizer.from_pretrained(config.EMBED_MODEL_NAME)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            f"埋め込みモデル {config.EMBED_MODEL_NAME} のトークナイザを取得できません → "
            "初回はネットワーク接続が必要です（モデルの初回ダウンロード、仕様書 §2）。"
            f"接続を確認して再実行してください（詳細: {exc}）"
        ) from exc


def _split_page_into_chunks(tokenizer, text: str) -> list[str]:
    """1ページ分のテキストをスライディングウィンドウでチャンク分割する。

    ページ境界をまたがない（コントラクト指定）のは、出典として
    「ファイル名＋ページ番号」を一意に提示する要件（仕様書 §6-3）を
    チャンク単位で成立させるため。
    """
    # 文書側の正規化。クエリ側（retrieve.search）と同一関数で表記を揃える。
    normalized = normalize_text(text)
    if not normalized:
        return []

    # 特殊トークン（[CLS]等）は埋め込み時にモデル側が付与するため、
    # チャンク長の勘定には含めない。
    token_ids = tokenizer(normalized, add_special_tokens=False)["input_ids"]

    step = config.CHUNK_SIZE_TOKENS - config.CHUNK_OVERLAP_TOKENS
    if step <= 0:
        raise RuntimeError(
            "CHUNK_OVERLAP_TOKENS が CHUNK_SIZE_TOKENS 以上になっています → "
            ".env の CHUNK_SIZE_TOKENS / CHUNK_OVERLAP_TOKENS を見直してください"
        )

    global _warned_token_boundary_mojibake

    chunks: list[str] = []
    start = 0
    total = len(token_ids)
    while start < total:
        end = start + config.CHUNK_SIZE_TOKENS
        # 末尾の新規トークンがオーバーラップ分以下しか残らない場合、次の
        # ウィンドウは直前チャンクとほぼ同文の重複チャンクになる。かといって
        # 生成をやめるとページ末尾のトークンが索引から漏れるため、残りを
        # 現在のチャンクへ吸収する（最大 CHUNK_SIZE+OVERLAP トークンとなるが、
        # ruri-v3 の系列長上限 8192 に対して十分小さい）。これで
        # 「取り零しゼロ」と「ほぼ重複チャンクの排除」を両立する。
        if total - end <= config.CHUNK_OVERLAP_TOKENS:
            end = total
        window = token_ids[start:end]
        chunk_text = tokenizer.decode(window, skip_special_tokens=True).strip()
        if chunk_text:
            # トークン ID 列を機械的な位置でスライスしているため、バイト
            # レベル BPE / byte-fallback を含むトークナイザでは多バイト文字
            # （日本語）が境界で分断され、decode 結果に置換文字 U+FFFD が
            # 混入し得る。元ページテキストに無い U+FFFD の出現をその検出
            # 手段として警告する（検索精度・表示品質の劣化シグナル）。
            if (
                not _warned_token_boundary_mojibake
                and "�" in chunk_text
                and "�" not in normalized
            ):
                logger.warning(
                    "decode 後のチャンクに元テキストに無い置換文字(U+FFFD)を検出しました。"
                    "トークン境界で多バイト文字が分断されている可能性があります"
                    "（チャンク境界付近の検索精度・表示品質に影響し得ます）"
                )
                _warned_token_boundary_mojibake = True
            chunks.append(chunk_text)
        if end >= total:
            break
        start += step
    return chunks


# ---------------------------------------------------------------------------
# 埋め込みと格納
# ---------------------------------------------------------------------------
def _load_embedder():
    """sentence-transformers の埋め込みモデルをロードする。"""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "sentence-transformers がインストールされていません → "
            "`pip install -r requirements.txt` を実行してください"
        ) from exc
    device = config.embedding_device()
    logger.info("埋め込みモデル %s をロードします（device=%s）", config.EMBED_MODEL_NAME, device)
    try:
        return SentenceTransformer(config.EMBED_MODEL_NAME, device=device)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            f"埋め込みモデル {config.EMBED_MODEL_NAME} をロードできません → "
            "初回はネットワーク接続が必要です。2回目以降はローカルキャッシュで動作します"
            f"（詳細: {exc}）"
        ) from exc


def _recreate_collection():
    """ChromaDB のコレクションを削除して作り直す。

    再実行時に差分更新ではなく全再構築とするのは、PoC では
    「corpus とベクタDB の内容が確実に一致していること」を
    増分ロジックの正しさより優先するため（コントラクト指定）。
    削除→更新漏れによる古いチャンクの残留は、出典付き回答の
    信頼性（仕様書 §1）を直接損なうリスクになる。
    """
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError as exc:
        raise RuntimeError(
            "chromadb がインストールされていません → "
            "`pip install -r requirements.txt` を実行してください"
        ) from exc

    config.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    # anonymized_telemetry を切るのは retrieve.py / app.py と同じ理由:
    # 機内モードでも動作すること（仕様書 §2）が要件で、外部への通信要素を
    # 残さないため。加えて chromadb は同一パスに対して異なる設定の
    # クライアント生成を ValueError で拒否するため、3モジュールで設定を
    # 統一しておかないと同一プロセス内での併用（UI からの再インジェスト等）
    # が実行時エラーになる。
    client = chromadb.PersistentClient(
        path=str(config.CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    try:
        client.delete_collection(config.CHROMA_COLLECTION_NAME)
        logger.info("既存コレクション '%s' を削除しました（全再構築のため）", config.CHROMA_COLLECTION_NAME)
    except Exception as exc:  # noqa: BLE001
        # 「存在しない」（初回実行など）は正常系だが、存在するのに削除に
        # 失敗した場合（DBロック・破損等）を同じログで流すと原因を誤誘導し、
        # 直後の create_collection が対処法なしの chromadb 例外で落ちる。
        # chromadb はバージョンにより例外型が異なる（NotFoundError /
        # ValueError 等）ため、型名とメッセージの両方で判別する。
        message = str(exc).lower()
        is_missing = (
            type(exc).__name__ == "NotFoundError"
            or "does not exist" in message
            or "not found" in message
        )
        if is_missing:
            logger.info("既存コレクション '%s' は存在しないため新規作成します", config.CHROMA_COLLECTION_NAME)
        else:
            raise RuntimeError(
                f"既存コレクション '{config.CHROMA_COLLECTION_NAME}' を削除できません → "
                "UI 等の他プロセスを終了して再実行してください。"
                "解消しない場合は data/chroma を削除してから再実行してください"
                f"（詳細: {exc}）"
            ) from exc
    # ruri-v3 は cosine 類似度前提で学習されているため、HNSW の距離空間も
    # cosine を明示する（既定の L2 のままだとスコアの解釈が変わってしまう）。
    try:
        collection = client.create_collection(
            name=config.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    except Exception as exc:  # noqa: BLE001
        # DB 破損・削除の不完全な残留などで作成に失敗した場合も、利用者が
        # 復旧手順を判断できるよう対処法つきに変換する（仕様書 §11）。
        raise RuntimeError(
            f"コレクション '{config.CHROMA_COLLECTION_NAME}' を作成できません → "
            "data/chroma を削除してから `python -m src.ingest` を再実行してください"
            f"（詳細: {exc}）"
        ) from exc
    return client, collection


def _chroma_add_batch_size(client) -> int:
    """ChromaDB の1回の add 上限。API があれば実値、無ければ安全側の既定値。"""
    try:
        return min(int(client.get_max_batch_size()), CHROMA_ADD_BATCH_FALLBACK)
    except Exception:  # noqa: BLE001
        return CHROMA_ADD_BATCH_FALLBACK


# ---------------------------------------------------------------------------
# メイン処理
# ---------------------------------------------------------------------------
def run_ingest(corpus_dir: Path | None = None) -> dict:
    """corpus を取り込み、ChromaDB へ格納する。

    戻り値（コントラクト固定形状）:
    {"files_ok": int, "files_failed": list[str], "pages": int,
     "chunks": int, "elapsed_sec": float}
    """
    started = time.perf_counter()
    corpus_dir = Path(corpus_dir) if corpus_dir is not None else config.CORPUS_DIR

    if not corpus_dir.is_dir():
        raise RuntimeError(
            f"corpus ディレクトリが見つかりません: {corpus_dir} → "
            "ディレクトリを作成し、取り込み対象の PDF / .txt / .md を配置してください"
            "（現職・過去職の業務文書は配置禁止です。data/corpus/README.md 参照）"
        )

    # ソートするのは、再実行時に chunk_id・格納順が安定し、
    # 評価結果（Recall@5）の再現性を確保するため。
    files = sorted(
        p for p in corpus_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in config.TARGET_EXTENSIONS
    )

    result = {
        "files_ok": 0,
        "files_failed": [],
        "pages": 0,
        "chunks": 0,
        "elapsed_sec": 0.0,
    }

    if not files:
        logger.warning(
            "取り込み対象ファイルがありません: %s → PDF / .txt / .md を配置して再実行してください",
            corpus_dir,
        )
        result["elapsed_sec"] = round(time.perf_counter() - started, 2)
        return result

    logger.info("取り込み開始: %d ファイル（%s）", len(files), corpus_dir)

    tokenizer = _load_tokenizer()

    # chunk_id・メタデータの file は「ファイル名のみ」（コントラクトの Hit 形状）。
    # サブディレクトリ間で同名ファイルがあると ID が衝突し、出典表示も
    # 区別できなくなるため、後勝ちにせず失敗ファイルとして明示する。
    seen_names: set[str] = set()

    all_texts: list[str] = []       # documents 用（プレフィックス無しの素テキスト）
    all_ids: list[str] = []
    all_metadatas: list[dict] = []

    for path in files:
        if path.name in seen_names:
            logger.error(
                "同名ファイルが複数あるためスキップ: %s → ファイル名を一意に変更してください",
                path,
            )
            result["files_failed"].append(path.name)
            continue
        seen_names.add(path.name)

        try:
            pages = _extract_file(path)
        except Exception as exc:  # noqa: BLE001
            # 1ファイルの失敗で全体を止めない（他ファイルの取り込みを優先）。
            # ただし握りつぶさず、ファイル名と対処法をログに必ず残す（仕様書 §11）。
            logger.error("抽出失敗: %s（%s）", path.name, exc)
            result["files_failed"].append(path.name)
            continue

        file_chunks = 0
        file_pages = 0
        for page_no, page_text in pages:
            chunks = _split_page_into_chunks(tokenizer, page_text)
            if not chunks:
                # 白紙ページ・図のみのページは正常にあり得るため失敗扱いにしない。
                logger.debug("%s p.%d: テキストが無いためスキップ", path.name, page_no)
                continue
            file_pages += 1
            for chunk_index, chunk_text in enumerate(chunks):
                all_texts.append(chunk_text)
                # chunk_id はコントラクト形式 "<file>:p<page>:c<index>"。
                all_ids.append(f"{path.name}:p{page_no}:c{chunk_index}")
                all_metadatas.append(
                    {"file": path.name, "page": page_no, "chunk_index": chunk_index}
                )
            file_chunks += len(chunks)

        if file_chunks == 0:
            # 全ページ空 = 実質取り込めていない（スキャンPDF等）。成功扱いに
            # すると「検索に出てこない」原因が見えなくなるため失敗として報告する。
            logger.error(
                "テキストを1文字も抽出できませんでした: %s → スキャン画像PDFの可能性があります"
                "（本PoCは画像読解の対象外、仕様書 §5）",
                path.name,
            )
            result["files_failed"].append(path.name)
            continue

        result["files_ok"] += 1
        result["pages"] += file_pages
        result["chunks"] += file_chunks
        logger.info("抽出完了: %s（%d ページ / %d チャンク）", path.name, file_pages, file_chunks)

    if not all_texts:
        logger.warning("有効なチャンクが1件もないため、ベクタDBは更新しません")
        result["elapsed_sec"] = round(time.perf_counter() - started, 2)
        return result

    # --- 埋め込み ---
    embedder = _load_embedder()
    logger.info("埋め込み開始: %d チャンク（batch_size=%d）", len(all_texts), config.EMBED_BATCH_SIZE)
    embed_started = time.perf_counter()
    # ruri-v3 はプレフィックス方式で学習されており、文書側には
    # EMBED_DOC_PREFIX を付けないと検索精度が大きく落ちる（config.py 参照）。
    # ただし documents（表示・rerank 入力に使う本文）にはプレフィックスを
    # 含めないため、埋め込み入力だけ別リストにする。
    embed_inputs = [config.EMBED_DOC_PREFIX + text for text in all_texts]
    embeddings = embedder.encode(
        embed_inputs,
        batch_size=config.EMBED_BATCH_SIZE,
        show_progress_bar=True,
        convert_to_numpy=True,
    )
    logger.info("埋め込み完了: %.1f 秒", time.perf_counter() - embed_started)

    # --- 格納 ---
    client, collection = _recreate_collection()
    add_batch = _chroma_add_batch_size(client)
    store_started = time.perf_counter()
    for i in range(0, len(all_texts), add_batch):
        collection.add(
            ids=all_ids[i : i + add_batch],
            documents=all_texts[i : i + add_batch],
            embeddings=embeddings[i : i + add_batch].tolist(),
            metadatas=all_metadatas[i : i + add_batch],
        )
    logger.info(
        "ChromaDB 格納完了: %d 件 → %s（%.1f 秒）",
        collection.count(),
        config.CHROMA_DIR,
        time.perf_counter() - store_started,
    )

    result["elapsed_sec"] = round(time.perf_counter() - started, 2)

    # 仕様書 §11: 処理件数・所要時間・失敗ファイル名を必ずログに出す。
    logger.info(
        "取り込み完了: 成功 %d ファイル / 失敗 %d ファイル / %d ページ / %d チャンク / %.1f 秒",
        result["files_ok"],
        len(result["files_failed"]),
        result["pages"],
        result["chunks"],
        result["elapsed_sec"],
    )
    if result["files_failed"]:
        logger.warning("失敗ファイル: %s", ", ".join(result["files_failed"]))

    return result


def main() -> int:
    """CLI エントリポイント（`python -m src.ingest`）。"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        result = run_ingest()
    except RuntimeError as exc:
        # 対処法込みのメッセージを標準エラーへ。スタックトレースを出さないのは
        # 利用者（面接デモの再現者）が読むべき情報を1行に絞るため。
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    print("=== 取り込み結果 ===")
    print(f"成功ファイル数 : {result['files_ok']}")
    print(f"失敗ファイル数 : {len(result['files_failed'])}")
    if result["files_failed"]:
        print(f"失敗ファイル   : {', '.join(result['files_failed'])}")
    print(f"ページ数       : {result['pages']}")
    print(f"チャンク数     : {result['chunks']}")
    print(f"所要時間       : {result['elapsed_sec']} 秒")
    # 失敗があっても部分成功なら 0 を返す（ログで気付ける）。全滅時のみ異常終了。
    if result["files_ok"] == 0 and result["files_failed"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
