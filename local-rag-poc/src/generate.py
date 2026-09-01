"""Ollama 呼び出し・出典整形モジュール（指示文書 §10 Phase 4）。

検索結果（retrieve.py の Hit）をコンテキストとして Ollama に渡し、
出典付きの回答（Answer 辞書）を返す。

このモジュールの設計方針（なぜこうしたか）:
- 拒否判定（「資料内に該当なし」）はプロンプト任せにせず**コード側の閾値**で行う。
  軽量モデルはプロンプトの拒否指示を無視して推測で答える事例が報告されている
  ため（指示文書 §10 Phase 4 注記）。全ヒットが閾値未満なら LLM を呼ばない。
- 出典（sources）は LLM の出力からではなく**コードが実際の Hit から構築**する。
  モデルが本文中に書いた出典行は捏造の可能性があるため除去する。
- <think> タグ除去は API パラメータ（think=False）と正規表現の**二重防御**。
"""

import argparse
import logging
import re
import sys
import time
from typing import TypedDict

import requests

from src import config
from src.retrieve import CorpusNotIngestedError, Hit, Retriever, get_retriever

logger = logging.getLogger(__name__)


class Answer(TypedDict):
    """回答1件（モジュール間コントラクトで固定の形状）。"""

    answer: str  # 表示用最終テキスト（出典ブロックは含まない）
    refused: bool  # 拒否なら True。このとき answer == config.REFUSAL_MESSAGE
    sources: list[dict]  # [{"file": str, "page": int}] 重複除去済み・登場順
    hits: list[Hit]  # 使用した検索ヒット（UI の出典展開用）
    elapsed_sec: float  # 検索開始〜回答完了の合計秒
    retrieval_sec: float  # うち検索（embedding + rerank）秒
    generation_sec: float  # うち LLM 生成秒（LLM を呼ばない拒否時は 0.0）
    model: str  # 実際に使用した Ollama モデル名


# ---------------------------------------------------------------------------
# 利用者向けエラーメッセージ（指示文書 §11: 対処法を必ず添える）
# ---------------------------------------------------------------------------
_CONNECT_ERROR_MSG = (
    "Ollamaに接続できません → `ollama serve` が起動しているか、"
    f"OLLAMA_HOST の設定（現在: {config.OLLAMA_HOST}）を確認してください"
)
_TIMEOUT_ERROR_MSG = (
    f"Ollama の応答が {config.OLLAMA_TIMEOUT_SEC} 秒以内に返りませんでした "
    f"→ 撤退基準（{config.OLLAMA_TIMEOUT_SEC}秒/問）を超過しています（指示文書 §7）。"
    "より軽量なモデル（例: qwen3:4b）への切り替えや質問の簡略化を検討してください"
)


def _model_not_found_msg(model: str) -> str:
    return (
        f"モデル {model} が Ollama に見つかりません "
        f"→ `ollama pull {model}` を実行してから再試行してください"
    )


# ---------------------------------------------------------------------------
# LLM 出力の検証・整形用の正規表現
# ---------------------------------------------------------------------------
# <think>...</think> ブロックの除去。API に think=False を渡していてもなお
# 正規表現でも除去するのは、古い Ollama が think パラメータ未対応の場合に
# qwen3 が思考タグを本文へそのまま出力するため（二重防御）。
# DOTALL で改行またぎ、非貪欲マッチで複数ブロックにも対応する。
_THINK_BLOCK_RE = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
# 対応の崩れた片割れタグ（開き/閉じ単独）はタグ文字列だけを除去する。
# 開きタグ以降を全て消すと、閉じ忘れ時に本文まで失われるため。
_THINK_TAG_RE = re.compile(r"</?think>", re.IGNORECASE)

# 拒否文言の検出。REFUSAL_MESSAGE の完全一致だけでなく緩い表現も拾うのは、
# 軽量モデルが「情報は見つかりませんでした」等と助詞を変えて出力する事例への
# 対策（フォーマット指示無視への防御。指示文書 §10 Phase 4 注記）。
# ただし本文のどこかに一致しただけでは拒否化せず、適用は _is_refusal_output()
# の「拒否文言が支配的な出力」に限定する（部分回答の誤拒否化防止）。
_LOOSE_REFUSAL_RE = re.compile(r"該当する情報.{0,5}見つかりません")
# 拒否文言（REFUSAL_MESSAGE・緩い表現）を除いた残余がこの文字数以下なら
# 「実質拒否のみの出力」として REFUSAL_MESSAGE へ正規化する。20 文字は
# 「申し訳ありませんが、」等の前置き・締めの定型句（10文字前後）は許容しつつ、
# 1文の実質的な回答（部分回答の前半。短くても30文字超になりやすい）を
# 誤って拒否化しない目安。迷ったら「拒否化しない」側に倒す（正当な回答と
# 出典を失う害の方が、冗長な拒否文がそのまま表示される害より大きい）。
_REFUSAL_RESIDUE_MAX_CHARS = 20

# モデルが末尾に列挙した出典行の検出用。
# 箇条書き記号・番号のプレフィックス（例 "- " "・" "[1] " "1) "）。
_BULLET_PREFIX_RE = re.compile(r"^\s*(?:[-*・●■]|\[?\d{1,2}\]?[.)．：:]?)\s*")
# 「出典:」等のヘッダだけの行（完全一致）。
_SOURCE_HEADER_ONLY_RE = re.compile(
    r"^[（(【\[]?\s*(?:出典|参照|参考(?:文献|資料)?|引用(?:元)?|Sources?|References?)"
    r"\s*[】\])）]?\s*[:：]?\s*$",
    re.IGNORECASE,
)
# 行頭の「出典: 」等のヘッダプレフィックス（後ろに列挙が続く形）。
_SOURCE_HEADER_PREFIX_RE = re.compile(
    r"^[（(【\[]?\s*(?:出典|参照|参考(?:文献|資料)?|引用(?:元)?|Sources?|References?)"
    r"\s*[】\])）]?\s*[:：]\s*",
    re.IGNORECASE,
)
# コーパスの対象拡張子（.pdf/.txt/.md、コントラクト ingest 節）を含むファイル名。
_FILE_NAME_RE = re.compile(r"[^\s、,：:]+\.(?:pdf|txt|md)\b", re.IGNORECASE)
# ページ番号表記（「p.3」「p3」「3ページ」の表記ゆれを許容）。
_PAGE_REF_RE = re.compile(r"(?:p\.?\s*\d+|\d+\s*ページ)", re.IGNORECASE)
# 列挙行の区切り・装飾として現れる記号類（残余判定の前に取り除く）。
_SOURCE_PUNCT_RE = re.compile(r"[\s,、，;；:：・/／()（）\[\]【】\-–—―。．.｡]+")
# ファイル名・ページ・記号を除いた残りがこの文字数以下なら列挙行とみなす
# （「等」「他」程度の残りは許容する）。
_SOURCE_RESIDUE_MAX_CHARS = 2


def _strip_think_blocks(text: str) -> str:
    """<think> ブロックと片割れタグを除去する。"""
    text = _THINK_BLOCK_RE.sub("", text)
    return _THINK_TAG_RE.sub("", text)


def _is_refusal_output(cleaned: str) -> bool:
    """整形後テキストが実質「拒否のみ」の出力かどうかを判定する。

    REFUSAL_MESSAGE の完全一致に加え、拒否文言（完全形・緩い表現）を除いた
    残余がごく短い「支配的一致」も拒否として正規化対象にする。一方、前半が
    正当な回答で末尾に「Bについては該当する情報が見つかりませんでした」と
    添えるような部分回答は残余が長くなるため本文として残す（緩い一致だけで
    丸ごと拒否化すると、正しい回答と出典まで失われるため）。
    """
    if cleaned == config.REFUSAL_MESSAGE:
        return True
    residue = cleaned.replace(config.REFUSAL_MESSAGE, "")
    residue = _LOOSE_REFUSAL_RE.sub("", residue)
    if residue == cleaned:
        # 拒否文言がどこにも含まれていない → 通常の回答。
        return False
    return len(residue.strip()) <= _REFUSAL_RESIDUE_MAX_CHARS


def _is_source_line(line: str, hit_files: set[str]) -> bool:
    """行がモデルの書いた出典列挙行かどうかを判定する。

    「ファイル名 p.ページ」を含むだけで削ると、本文中の正当な言及
    （例:「詳細は manual.pdf p.3 を参照」）まで消してしまう。そこで
    ファイル名・ページ表記・区切り記号を取り除いた**残りがほぼ空**の
    行だけを「純粋な列挙行」として除去対象にする。
    """
    s = _BULLET_PREFIX_RE.sub("", line.strip())
    if not s:
        return False
    if _SOURCE_HEADER_ONLY_RE.match(s):
        return True
    # ファイル名にもページにも触れていない行は本文とみなす。
    if not _FILE_NAME_RE.search(s) and not _PAGE_REF_RE.search(s):
        return False
    s = _SOURCE_HEADER_PREFIX_RE.sub("", s)
    s = _FILE_NAME_RE.sub("", s)
    # 拡張子を省いてファイル名を書くモデルもいるため、実際のヒットの
    # ファイル名（拡張子抜き）も残余判定から除く。
    for fname in hit_files:
        s = s.replace(fname, "")
        stem = fname.rsplit(".", 1)[0]
        if stem:
            s = s.replace(stem, "")
    s = _PAGE_REF_RE.sub("", s)
    s = _SOURCE_PUNCT_RE.sub("", s)
    return len(s) <= _SOURCE_RESIDUE_MAX_CHARS


def _strip_trailing_source_lines(text: str, hits: list[Hit]) -> str:
    """モデルが末尾に列挙した出典行を除去する。

    出典はコードが Hit から構築して別途表示するため、モデル出力側の列挙は
    重複かつ捏造の温床になる。**末尾からのみ**削るのは、本文中で正当に
    ページへ言及している行（例:「詳細は manual.pdf p.3 を参照」）まで
    誤って消さないため。非出典行に当たった時点で打ち切る。
    """
    hit_files = {h["file"] for h in hits}
    lines = text.rstrip().splitlines()
    while lines:
        last = lines[-1].strip()
        if not last:
            lines.pop()
            continue
        if _is_source_line(last, hit_files):
            lines.pop()
            continue
        break
    return "\n".join(lines).strip()


def _build_sources(hits: list[Hit]) -> list[dict]:
    """出典リストを実際の Hit から構築する（重複除去・登場順維持）。

    LLM 出力から出典を抽出しないのは、モデルが存在しないファイル名・
    ページを捏造するリスクを構造的に排除するため（指示文書 §1: 説明責任）。
    """
    seen: set[tuple[str, int]] = set()
    sources: list[dict] = []
    for hit in hits:
        key = (hit["file"], hit["page"])
        if key not in seen:
            seen.add(key)
            sources.append({"file": hit["file"], "page": hit["page"]})
    return sources


# ---------------------------------------------------------------------------
# プロンプト構築（指示文書 §10 Phase 4 の4制約を必ず含める）
# ---------------------------------------------------------------------------
def _build_system_prompt() -> str:
    # 制約3（末尾に出典列挙）はコード側で除去・再構築するにもかかわらず
    # プロンプトにも入れる。指示文書 §10 Phase 4 が4制約すべての明記を
    # 要求していることに加え、出典を意識させることでコンテキスト外の
    # 情報を混ぜにくくする効果を狙うため。
    return (
        "あなたは社内資料に基づいて質問に答えるアシスタントです。"
        "以下のルールを必ず守ってください。\n"
        "1. 与えられたコンテキストのみを根拠に回答すること。\n"
        f"2. コンテキストに該当する情報がない場合は、必ず「{config.REFUSAL_MESSAGE}」"
        "とだけ返すこと。\n"
        "3. 回答の末尾に、参照した「ファイル名 p.ページ番号」を列挙すること。\n"
        "4. 推測や一般論による補完は禁止。コンテキストに書かれていないことを"
        "書いてはならない。"
    )


def _build_user_prompt(query: str, hits: list[Hit]) -> str:
    # コンテキストは「[番号] (ファイル名 p.ページ)\n本文」形式で番号付けする
    # （コントラクト指定）。番号を付けるのは、モデルがどの断片を根拠に
    # したかを扱いやすくするため。
    blocks = []
    for i, hit in enumerate(hits, start=1):
        blocks.append(f"[{i}] ({hit['file']} p.{hit['page']})\n{hit['text']}")
    context = "\n\n".join(blocks)
    return f"# コンテキスト\n{context}\n\n# 質問\n{query}"


# ---------------------------------------------------------------------------
# Ollama 呼び出し
# ---------------------------------------------------------------------------
# /api/tags は軽量な一覧取得 API のため、生成用の OLLAMA_TIMEOUT_SEC（既定
# 180秒）を流用しない。流用するとホスト無応答時に、生成前のモデル解決だけで
# 撤退基準（180秒/問。指示文書 §7）相当の時間をブロックし得るため、短い
# 専用タイムアウトで打ち切る。
_TAGS_TIMEOUT_SEC = 5

# モデル解決結果（host＋希望モデル → 実際に使うモデル）のプロセス内キャッシュ。
# answer() のたびに /api/tags を往復させないため。**成功時のみ**キャッシュ
# するのは、失敗時（Ollama 未起動・モデル未pull 等）の判定を固定化すると、
# 利用者が `ollama serve` / `ollama pull` で復旧した後も古い結果のまま
# 動き続けてしまうため（失敗は毎回確認し直す）。
_MODEL_RESOLUTION_CACHE: dict[tuple[str, str], str] = {}


def _resolve_model_via_tags(base_url: str) -> str:
    """使用モデルを決定する。/api/tags で存在確認し、無ければフォールバック。

    config.resolve_ollama_model() は GPU 有無だけで決めるため、実際に
    そのモデルが pull 済みかは分からない。存在しないモデルで /api/chat を
    叩いて 404 になる前に、取得済みモデル一覧と突き合わせて自動で
    フォールバックする（デモ中に手詰まりにならないための保険）。
    """
    desired = config.resolve_ollama_model()
    cache_key = (base_url, desired)
    if cache_key in _MODEL_RESOLUTION_CACHE:
        return _MODEL_RESOLUTION_CACHE[cache_key]
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=_TAGS_TIMEOUT_SEC)
        resp.raise_for_status()
        models = resp.json().get("models", [])
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(_CONNECT_ERROR_MSG) from exc
    except Exception as exc:
        # 一覧取得の失敗（読み取りタイムアウト含む）は致命ではない（chat 側の
        # 404 / タイムアウト処理で正しい案内ができる）ため、警告して予定
        # モデルのまま続行する。失敗結果はキャッシュしない（復旧後に再確認）。
        logger.warning(
            "/api/tags の確認に失敗したため、モデル %s をそのまま使用します（%s）",
            desired,
            exc,
        )
        return desired

    available: set[str] = set()
    for m in models:
        for key in ("name", "model"):
            name = m.get(key)
            if name:
                available.add(name)

    def _present(model_name: str) -> bool:
        # タグ省略時（例 "qwen3"）は Ollama 側で ":latest" 扱いになるため、
        # その表記ゆれも一致とみなす。
        if model_name in available:
            return True
        return ":" not in model_name and f"{model_name}:latest" in available

    if _present(desired):
        _MODEL_RESOLUTION_CACHE[cache_key] = desired
        return desired
    fallback = config.OLLAMA_FALLBACK_MODEL
    if _present(fallback):
        logger.warning(
            "モデル %s が Ollama に見つからないため %s へフォールバックします "
            "（%s を使うには `ollama pull %s` を実行してください）",
            desired,
            fallback,
            desired,
            desired,
        )
        # フォールバック確定も「一覧と突き合わせて解決できた」成功として
        # キャッシュする（以後の質問ごとの /api/tags 往復を省く）。
        _MODEL_RESOLUTION_CACHE[cache_key] = fallback
        return fallback
    # どちらも無い場合は予定モデルのまま進め、chat 側の 404 で pull を案内する。
    logger.warning(
        "モデル %s / %s のいずれも Ollama に見つかりません → "
        "`ollama pull %s` を実行してください（このまま呼び出しを試みます）",
        desired,
        fallback,
        desired,
    )
    return desired


def _call_ollama(model: str, system_prompt: str, user_prompt: str) -> str:
    """Ollama /api/chat を呼び、応答本文（生テキスト）を返す。"""
    base_url = config.OLLAMA_HOST.rstrip("/")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        # ストリーミングにしないのは、応答全体に対して <think> 除去・
        # 出典行除去などの検証・整形を行ってから表示するため。
        "stream": False,
        # qwen3 の思考モードを無効化（1段目の防御。古い Ollama では
        # 無視されるため、応答側でも正規表現で除去する）。
        "think": False,
        "options": {
            "temperature": config.OLLAMA_TEMPERATURE,
            "num_ctx": config.OLLAMA_NUM_CTX,
        },
    }
    try:
        resp = requests.post(
            f"{base_url}/api/chat", json=payload, timeout=config.OLLAMA_TIMEOUT_SEC
        )
    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(_CONNECT_ERROR_MSG) from exc
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(_TIMEOUT_ERROR_MSG) from exc

    if resp.status_code == 404:
        raise RuntimeError(_model_not_found_msg(model))
    if resp.status_code != 200:
        # Ollama はエラー詳細を JSON の "error" に入れて返すため転記する。
        try:
            detail = resp.json().get("error", resp.text)
        except ValueError:
            detail = resp.text
        raise RuntimeError(
            f"Ollama がエラーを返しました（HTTP {resp.status_code}: {detail}）"
            " → `ollama serve` のログを確認してください"
        )

    try:
        content = resp.json()["message"]["content"]
    except (ValueError, KeyError, TypeError) as exc:
        raise RuntimeError(
            "Ollama の応答形式が想定と異なります → Ollama のバージョンが古い"
            "可能性があります。`ollama --version` を確認し、更新を検討してください"
        ) from exc
    return content


# ---------------------------------------------------------------------------
# 本体
# ---------------------------------------------------------------------------
def answer(
    query: str,
    retriever: Retriever | None = None,
    top_k_embed: int | None = None,
    top_k_rerank: int | None = None,
    score_threshold: float | None = None,
) -> Answer:
    """質問に対して検索＋生成を行い、Answer 辞書を返す。

    retriever 引数は UI（Streamlit）からロード済みインスタンスを渡すための
    もの。None なら内部のシングルトンを使う（CLI・評価スクリプト向け）。

    top_k_embed / top_k_rerank / score_threshold は呼び出し単位の上書き
    （None なら config の既定値）。UI のスライダー値をこの引数で受けるのは、
    config モジュール属性の実行時書き換えだとプロセス（全ブラウザセッション）
    で共有されてしまい、あるセッションの変更が他セッションの検索挙動を
    暗黙に変えるため（呼び出し引数ならその1回の回答にしか影響しない）。
    """
    # モデルロード（初回のみ数十秒）は応答時間の指標にならないため、
    # 計測開始前に済ませる（elapsed_sec は「検索開始〜回答完了」）。
    if retriever is None:
        retriever = get_retriever()

    threshold = (
        score_threshold if score_threshold is not None else config.RERANK_SCORE_THRESHOLD
    )

    t_start = time.perf_counter()

    # --- 検索（embedding → rerank） ---
    hits = retriever.search(query, top_k_embed=top_k_embed, top_k_rerank=top_k_rerank)
    retrieval_sec = time.perf_counter() - t_start
    best_score = max((h["score"] for h in hits), default=0.0)
    logger.info(
        "検索完了: %d件ヒット（%.2f秒、最高スコア %.3f）",
        len(hits),
        retrieval_sec,
        best_score,
    )

    # --- 拒否判定（コード側） ---
    # 全ヒットが閾値未満なら LLM を呼ばずに拒否する。プロンプトの拒否指示に
    # 頼らないのは、軽量モデルが指示を無視して推測で答える事例への対策
    # （指示文書 §10 Phase 4 注記）。LLM を呼ばない分、応答も速くなる。
    if not hits or best_score < threshold:
        logger.info(
            "全ヒットのスコアが閾値 %.2f 未満のため LLM を呼ばず拒否します",
            threshold,
        )
        return Answer(
            answer=config.REFUSAL_MESSAGE,
            refused=True,
            sources=[],
            # 拒否時もヒットは返す（UI で「なぜ拒否されたか」をスコア付きで
            # 確認できるようにするため。コントラクト指定）。
            hits=hits,
            elapsed_sec=time.perf_counter() - t_start,
            retrieval_sec=retrieval_sec,
            # LLM は未呼び出しだが、UI サイドバーのモデル名表示のために
            # 「呼ぶとしたら使うモデル」を入れておく。
            generation_sec=0.0,
            model=config.resolve_ollama_model(),
        )

    # --- 生成（Ollama /api/chat） ---
    t_gen = time.perf_counter()
    base_url = config.OLLAMA_HOST.rstrip("/")
    model = _resolve_model_via_tags(base_url)
    raw = _call_ollama(model, _build_system_prompt(), _build_user_prompt(query, hits))
    generation_sec = time.perf_counter() - t_gen
    logger.info("生成完了: モデル %s（%.2f秒）", model, generation_sec)

    # --- コード側の検証・整形（指示文書 §10 Phase 4 必須） ---
    cleaned = _strip_think_blocks(raw)
    cleaned = _strip_trailing_source_lines(cleaned, hits)

    # 閾値は超えたがコンテキストに答えが無く、モデル自身が拒否文言を返した
    # ケース。文言ゆれごと REFUSAL_MESSAGE の一字一句へ正規化するのは、
    # 評価スクリプトの拒否判定と UI 表示を安定させるため。正規化の適用は
    # 「出力が実質拒否のみ」（完全一致・支配的一致）の場合に限定し、
    # 部分回答は本文として残す（_is_refusal_output 参照）。
    if not cleaned or _is_refusal_output(cleaned):
        if cleaned and cleaned != config.REFUSAL_MESSAGE:
            logger.info("モデル出力に拒否文言を検出したため正規化しました")
        elif not cleaned:
            # 整形後に空になるのは思考タグのみ等の異常出力。推測で埋める
            # より拒否扱いにする方が安全（指示文書 §1: ハルシネーション対策）。
            logger.warning("モデル出力が整形後に空になったため拒否として扱います")
        return Answer(
            answer=config.REFUSAL_MESSAGE,
            refused=True,
            sources=[],
            hits=hits,
            elapsed_sec=time.perf_counter() - t_start,
            retrieval_sec=retrieval_sec,
            generation_sec=generation_sec,
            model=model,
        )

    return Answer(
        answer=cleaned,
        refused=False,
        # 出典はモデル出力ではなく実際の Hit から構築する（捏造出典対策）。
        sources=_build_sources(hits),
        hits=hits,
        elapsed_sec=time.perf_counter() - t_start,
        retrieval_sec=retrieval_sec,
        generation_sec=generation_sec,
        model=model,
    )


# ---------------------------------------------------------------------------
# CLI（§11: 各モジュールは単体実行可能にする）
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m src.generate",
        description="検索＋生成を CLI で試す（回答・出典・所要時間を表示）",
    )
    parser.add_argument("query", help="質問文")
    args = parser.parse_args(argv)

    # 所要時間・件数などの経過ログも利用者に見せる（応答時間の内訳は
    # 面接デモの説明材料になるため INFO で表示）。
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    try:
        result = answer(args.query)
    except CorpusNotIngestedError as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"エラー: {exc}", file=sys.stderr)
        return 1

    print("\n=== 回答 ===")
    print(result["answer"])
    print("\n=== 出典 ===")
    if result["sources"]:
        for src in result["sources"]:
            print(f"- {src['file']} p.{src['page']}")
    else:
        print("（なし）")
    print("\n=== 所要時間 ===")
    print(
        f"合計 {result['elapsed_sec']:.1f}秒 "
        f"（検索 {result['retrieval_sec']:.1f}秒 / 生成 {result['generation_sec']:.1f}秒）"
        f" | モデル: {result['model']} | 拒否: {result['refused']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
