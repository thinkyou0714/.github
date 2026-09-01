"""ゴールデンセット評価スクリプト（指示文書 §10 Phase 6 / §6 受入基準）。

golden_set.yaml の質問を実際の検索・生成パイプラインに流し、以下を測定する。

- Recall@5      : 期待した出典ファイルが検索上位 TOP_K_RERANK 件に入った率。
                  page 指定がある問については file+page 一致率も参考値として別集計
- 拒否率        : 「資料に記載がない」質問に対して正しく拒否できた率
- 平均応答時間  : 1問あたりの合計・検索・生成の内訳

結果は eval/results/ に明細 CSV とサマリ CSV で出力し、受入基準
（Recall@5 >= 80%、拒否 4/5 以上、応答時間 CPU 60秒以内）との照合結果を
標準出力に表示する。

実行方法（リポジトリルートで）:
    python -m eval.run_eval
"""

import csv
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# `python -m eval.run_eval` 以外の起動方法（IDE から直接実行等）でも
# `from src import config` が壊れないよう、先にプロジェクトルートを通す。
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import yaml  # noqa: E402

from src import config, generate  # noqa: E402
from src.retrieve import CorpusNotIngestedError, Retriever  # noqa: E402

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 受入基準（指示文書 §6）。実行時の調整パラメータではなく「合否の定義」なので
# config.py（確定済み・変更禁止）ではなく評価スクリプト側に名前付き定数で持つ。
# ---------------------------------------------------------------------------
ACCEPT_RECALL_AT_5 = 0.80  # §6-4: 正解文書が Top-5 に入る率 80% 以上
ACCEPT_REFUSAL_RATIO = 4 / 5  # §6-5: 「資料に無い」5問中4問以上で拒否
ACCEPT_ELAPSED_SEC_CPU = 60.0  # §6-6: CPU-only で 1問 60秒以内
ACCEPT_ELAPSED_SEC_GPU = 15.0  # §6-6: GPU 有りなら 15秒以内

# ingest.py の取り込み対象と同じ拡張子。プレースホルダ検出（expected の file が
# corpus に実在するか）を ingest と同じ基準で行うためにここでも定義する。
CORPUS_EXTS = {".pdf", ".txt", ".md"}


# ---------------------------------------------------------------------------
# golden_set.yaml の読み込みと検証
# ---------------------------------------------------------------------------
def load_golden_set(path: Path) -> tuple[list[dict], list[dict]]:
    """ゴールデンセットを読み込み、(answerable, unanswerable) を返す。

    形式不備は実行を続けても無意味な結果しか出ないため、対処法つきで即座に
    エラーにする（握りつぶさない。指示文書 §11）。
    """
    if not path.exists():
        raise FileNotFoundError(
            f"ゴールデンセットが見つかりません: {path} → eval/golden_set.yaml を"
            "作成してください（リポジトリのテンプレートを参照）"
        )
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(
            f"{path} の形式が不正です → トップレベルに answerable / unanswerable "
            "の2キーを持つ YAML にしてください"
        )

    answerable = data.get("answerable") or []
    unanswerable = data.get("unanswerable") or []

    for item in answerable:
        if not item.get("id") or not item.get("question"):
            raise ValueError(
                f"answerable の項目に id または question がありません: {item} "
                "→ golden_set.yaml を修正してください"
            )
        sources = item.get("expected_sources") or []
        if not sources or not all(s.get("file") for s in sources):
            raise ValueError(
                f"answerable の項目 {item.get('id')} に expected_sources（file 必須）"
                "がありません → golden_set.yaml を修正してください"
            )
    for item in unanswerable:
        if not item.get("id") or not item.get("question"):
            raise ValueError(
                f"unanswerable の項目に id または question がありません: {item} "
                "→ golden_set.yaml を修正してください"
            )
    return answerable, unanswerable


def corpus_file_names() -> set[str]:
    """corpus 内の取り込み対象ファイル名（パスを除いた名前のみ）を集める。

    Hit の file はファイル名のみ（コントラクト）なので、判定側も名前で揃える。
    """
    if not config.CORPUS_DIR.exists():
        return set()
    return {
        p.name
        for p in config.CORPUS_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in CORPUS_EXTS
    }


def warn_if_placeholder(answerable: list[dict], corpus_files: set[str]) -> bool:
    """expected の file が corpus に無い場合に警告する。

    golden_set.yaml はプレースホルダ（corpus 題材が未確定のためのテンプレート、
    指示文書 §13-2）で出荷されるため、差し替え忘れのまま評価すると Recall@5 が
    常に 0 になる。それを「精度が低い」と誤読しないよう、明確に警告する。
    戻り値: プレースホルダのままと判断したら True。
    """
    expected = {
        s["file"] for item in answerable for s in item.get("expected_sources", [])
    }
    missing = sorted(expected - corpus_files)
    if not missing:
        return False

    all_missing = len(missing) == len(expected)
    banner = "=" * 70
    print(banner)
    if all_missing:
        print("【警告】golden_set.yaml はプレースホルダのままの可能性があります。")
        print("expected_sources に書かれたファイルが corpus に1つも存在しません。")
    else:
        print("【警告】golden_set.yaml の一部の expected_sources が corpus にありません。")
    print(f"  corpus ディレクトリ : {config.CORPUS_DIR}")
    print(f"  見つからないファイル: {', '.join(missing)}")
    print("  → corpus 確定後に golden_set.yaml を実ファイル名・実ページ番号へ")
    print("    差し替えてください（差し替えないと Recall@5 は正しく測れません）。")
    print("  → 現職・過去職の業務文書由来の質問は使用禁止です（指示文書 §2）。")
    print(banner)
    logger.warning("expected_sources のうち %d 件が corpus に存在しません", len(missing))
    return all_missing


# ---------------------------------------------------------------------------
# 判定ヘルパ
# ---------------------------------------------------------------------------
def judge_recall(hits: list[dict], expected_sources: list[dict]) -> tuple[bool, bool, bool]:
    """検索ヒットと期待出典を突き合わせる。

    戻り値: (file一致したか, file+page一致したか, page指定を持つ問か)
    Recall@5 の本判定は file 一致（コントラクト）。page はチャンク分割の都合で
    前後ページに揺れやすいため、file+page は参考値としてのみ扱う。
    """
    has_page = any("page" in s and s["page"] is not None for s in expected_sources)
    file_hit = False
    page_hit = False
    for s in expected_sources:
        for h in hits:
            if h["file"] != s["file"]:
                continue
            file_hit = True
            if s.get("page") is not None and h["page"] == s["page"]:
                page_hit = True
    return file_hit, page_hit, has_page


def _fmt(value: float | None, digits: int = 3) -> str:
    """CSV・画面出力用。未測定（None）は空欄にして「0だった」と誤読させない。"""
    return "" if value is None else f"{value:.{digits}f}"


def _avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


# ---------------------------------------------------------------------------
# 評価本体
# ---------------------------------------------------------------------------
def run_eval() -> int:
    started = time.perf_counter()
    answerable, unanswerable = load_golden_set(config.GOLDEN_SET_PATH)
    logger.info(
        "ゴールデンセット読み込み完了: answerable=%d問 / unanswerable=%d問",
        len(answerable),
        len(unanswerable),
    )

    corpus_files = corpus_file_names()
    placeholder = warn_if_placeholder(answerable, corpus_files)

    # モデルロードは数十秒かかるため1回だけ行い、全質問で使い回す。
    retriever = Retriever()

    # Ollama 停止・タイムアウト等で生成が失敗した場合、残りの質問で同じ失敗を
    # （最大180秒×残問数）繰り返しても得るものが無いため、以降は生成をスキップ
    # して検索のみ（Recall@5 のみ）で評価を続行する。
    generation_available = True
    generation_error: str | None = None

    rows: list[dict] = []
    failed_ids: list[str] = []

    recall_hits = 0
    page_hits = 0
    page_total = 0
    refusal_correct = 0
    refusal_evaluated = 0
    elapsed_list: list[float] = []
    retrieval_list: list[float] = []
    generation_list: list[float] = []
    model_used: str | None = None

    def ask(qid: str, question: str) -> tuple[list[dict], dict | None]:
        """1問を実行する。戻り値: (検索ヒット, Answer または None)。

        生成が使えない（Ollama 停止等）場合は検索のみにフォールバックする。
        """
        nonlocal generation_available, generation_error, model_used
        if generation_available:
            try:
                ans = generate.answer(question, retriever=retriever)
                model_used = ans["model"]
                return ans["hits"], ans
            except CorpusNotIngestedError:
                raise  # コーパス未投入は続行不能なので上位で案内して終了する
            except RuntimeError as exc:
                # generate.py 側の例外メッセージに利用者向け対処法が含まれている
                logger.error("LLM 生成に失敗（id=%s）: %s", qid, exc)
                logger.warning(
                    "以降の質問は LLM 生成をスキップし、検索のみで評価を続行します"
                    "（拒否率・応答時間は測定不可になります）"
                )
                generation_available = False
                generation_error = str(exc)
                failed_ids.append(qid)
        hits = retriever.search(question)
        return hits, None

    # ---- answerable: Recall@5 ＋ 応答時間 ----
    for item in answerable:
        qid, question = item["id"], item["question"]
        hits, ans = ask(qid, question)
        file_hit, page_hit, has_page = judge_recall(hits, item["expected_sources"])

        recall_hits += int(file_hit)
        if has_page:
            page_total += 1
            page_hits += int(page_hit)

        refused = ans["refused"] if ans else None
        elapsed = ans["elapsed_sec"] if ans else None
        if ans:
            elapsed_list.append(ans["elapsed_sec"])
            retrieval_list.append(ans["retrieval_sec"])
            generation_list.append(ans["generation_sec"])

        logger.info(
            "[%s] hit=%s refused=%s elapsed=%s", qid, file_hit, refused,
            _fmt(elapsed, 1) or "-",
        )
        rows.append(
            {
                "id": qid,
                "type": "answerable",
                "question": question,
                "hit": file_hit,
                "refused": "" if refused is None else refused,
                "top_files": ";".join(h["file"] for h in hits),
                "top_pages": ";".join(str(h["page"]) for h in hits),
                "best_score": _fmt(hits[0]["score"], 4) if hits else "",
                "elapsed_sec": _fmt(elapsed, 2),
            }
        )

    # ---- unanswerable: 拒否できたか ----
    for item in unanswerable:
        qid, question = item["id"], item["question"]
        hits, ans = ask(qid, question)

        refused = ans["refused"] if ans else None
        elapsed = ans["elapsed_sec"] if ans else None
        if ans:
            refusal_evaluated += 1
            refusal_correct += int(ans["refused"])
            elapsed_list.append(ans["elapsed_sec"])
            retrieval_list.append(ans["retrieval_sec"])
            generation_list.append(ans["generation_sec"])

        logger.info(
            "[%s] refused=%s elapsed=%s", qid,
            refused if refused is not None else "測定不可", _fmt(elapsed, 1) or "-",
        )
        rows.append(
            {
                "id": qid,
                "type": "unanswerable",
                "question": question,
                "hit": "",  # 拒否が正解の問に Recall は無い
                "refused": "" if refused is None else refused,
                "top_files": ";".join(h["file"] for h in hits),
                "top_pages": ";".join(str(h["page"]) for h in hits),
                "best_score": _fmt(hits[0]["score"], 4) if hits else "",
                "elapsed_sec": _fmt(elapsed, 2),
            }
        )

    # ---- 集計 ----
    recall = recall_hits / len(answerable) if answerable else None
    recall_fp = page_hits / page_total if page_total else None
    refusal_acc = (
        refusal_correct / refusal_evaluated if refusal_evaluated else None
    )
    avg_elapsed = _avg(elapsed_list)
    max_elapsed = max(elapsed_list) if elapsed_list else None

    gpu = config.has_gpu()
    elapsed_limit = ACCEPT_ELAPSED_SEC_GPU if gpu else ACCEPT_ELAPSED_SEC_CPU
    if model_used is None:
        # 1問も生成できなかった場合でも「どのモデルで測るはずだったか」は残す
        model_used = config.resolve_ollama_model() + "（未実行）"

    # ---- 受入基準との照合（指示文書 §6） ----
    def verdict(ok: bool | None) -> str:
        return "測定不可" if ok is None else ("OK" if ok else "NG")

    ok_recall = None if recall is None else recall >= ACCEPT_RECALL_AT_5
    # 全問を生成まで評価できたときだけ合否を出す（部分測定での合格判定は誤解の元）
    ok_refusal = (
        refusal_correct / len(unanswerable) >= ACCEPT_REFUSAL_RATIO
        if unanswerable and refusal_evaluated == len(unanswerable)
        else None
    )
    ok_elapsed = None if avg_elapsed is None else avg_elapsed <= elapsed_limit

    # ---- CSV 出力 ----
    # タイムスタンプでファイル名を分け、パラメータ調整の試行（指示文書 §7 の
    # 3回ルール）ごとの結果を上書きせず比較できるようにする。
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    config.EVAL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    detail_path = config.EVAL_RESULTS_DIR / f"eval_{stamp}.csv"
    summary_path = config.EVAL_RESULTS_DIR / f"eval_{stamp}_summary.csv"

    detail_fields = [
        "id", "type", "question", "hit", "refused",
        "top_files", "top_pages", "best_score", "elapsed_sec",
    ]
    # Windows の Excel でそのまま開けるよう BOM 付き UTF-8 にする
    # （面接デモ環境が Windows 11 のため。指示文書 §3）
    with detail_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=detail_fields)
        writer.writeheader()
        writer.writerows(rows)

    summary_rows = [
        ("timestamp", stamp),
        ("golden_set", str(config.GOLDEN_SET_PATH)),
        ("placeholder_warning", placeholder),
        ("n_answerable", len(answerable)),
        ("n_unanswerable", len(unanswerable)),
        ("recall_at_5", _fmt(recall)),
        ("recall_hits", f"{recall_hits}/{len(answerable)}"),
        ("recall_file_page_ref", _fmt(recall_fp)),  # 参考値（page 指定問のみ）
        ("refusal_accuracy", _fmt(refusal_acc)),
        ("refusal_correct", f"{refusal_correct}/{len(unanswerable)}"),
        ("avg_elapsed_sec", _fmt(avg_elapsed, 2)),
        ("max_elapsed_sec", _fmt(max_elapsed, 2)),
        ("avg_retrieval_sec", _fmt(_avg(retrieval_list), 2)),
        ("avg_generation_sec", _fmt(_avg(generation_list), 2)),
        ("model", model_used),
        ("gpu", gpu),
        ("embed_model", config.EMBED_MODEL_NAME),
        ("rerank_model", config.RERANK_MODEL_NAME),
        ("top_k_embed", config.TOP_K_EMBED),
        ("top_k_rerank", config.TOP_K_RERANK),
        ("rerank_score_threshold", config.RERANK_SCORE_THRESHOLD),
        ("chunk_size_tokens", config.CHUNK_SIZE_TOKENS),
        ("chunk_overlap_tokens", config.CHUNK_OVERLAP_TOKENS),
        ("accept_recall_at_5", verdict(ok_recall)),
        ("accept_refusal", verdict(ok_refusal)),
        ("accept_elapsed", verdict(ok_elapsed)),
    ]
    with summary_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerows(summary_rows)

    total_sec = time.perf_counter() - started
    logger.info(
        "評価完了: %d問 / 所要 %.1f秒 / 生成失敗 %s",
        len(rows), total_sec, failed_ids or "なし",
    )

    # ---- サマリを標準出力へ ----
    line = "-" * 70
    print()
    print(line)
    print("評価結果サマリ")
    print(line)
    print(f"  Recall@5（file一致）      : {_fmt(recall)}  ({recall_hits}/{len(answerable)})")
    if recall_fp is not None:
        print(f"  file+page 一致率（参考）  : {_fmt(recall_fp)}  ({page_hits}/{page_total})")
    if refusal_acc is not None:
        print(f"  拒否率（unanswerable）    : {_fmt(refusal_acc)}  ({refusal_correct}/{refusal_evaluated})")
    else:
        print("  拒否率（unanswerable）    : 測定不可（LLM 生成が実行できませんでした）")
    if avg_elapsed is not None:
        print(f"  平均応答時間              : {avg_elapsed:.1f}秒（検索 {_avg(retrieval_list):.1f}秒 / 生成 {_avg(generation_list):.1f}秒）")
        print(f"  最大応答時間              : {max_elapsed:.1f}秒")
    else:
        print("  平均応答時間              : 測定不可（LLM 生成が実行できませんでした）")
    print(f"  使用モデル                : {model_used}（GPU: {'あり' if gpu else 'なし'}）")
    print(line)
    print("受入基準との照合（指示文書 §6）")
    print(line)
    print(f"  [{verdict(ok_recall):>4}] Recall@5 >= {ACCEPT_RECALL_AT_5:.0%}")
    print(f"  [{verdict(ok_refusal):>4}] 拒否 {len(unanswerable)}問中 {int(len(unanswerable) * ACCEPT_REFUSAL_RATIO)}問以上")
    print(f"  [{verdict(ok_elapsed):>4}] 平均応答時間 <= {elapsed_limit:.0f}秒（{'GPU' if gpu else 'CPU-only'} 基準）")
    print(line)
    if generation_error:
        print("※ LLM 生成が途中で失敗したため、一部指標が測定できていません。")
        print(f"   原因: {generation_error}")
    if placeholder:
        print("※ golden_set.yaml がプレースホルダのままのため、上記の数値は")
        print("   実コーパスでの精度を表しません。corpus 確定後に差し替えてください。")
    print(f"明細 CSV : {detail_path}")
    print(f"サマリCSV: {summary_path}")

    # 受入基準を1つでも満たさない（または測れない）場合は非0で返し、
    # スクリプト連携（make eval 等）で失敗を検知できるようにする。
    all_ok = all(v is True for v in (ok_recall, ok_refusal, ok_elapsed))
    return 0 if all_ok else 1


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        return run_eval()
    except CorpusNotIngestedError as exc:
        # retrieve.py 側のメッセージに「先に ingest を」の案内が含まれている
        print(f"エラー: {exc}")
        return 1
    except (FileNotFoundError, ValueError) as exc:
        print(f"エラー: {exc}")
        return 1
    except RuntimeError as exc:
        # モデルロード失敗等。各モジュールが対処法つきメッセージを添えている
        print(f"エラー: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
