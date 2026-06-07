# THINK YOU LAB — GitHub Repository Conventions (SSOT)

> 全 repo 共通規約。新規 repo 作成時・first push 前に従う。
> 2026-05-31 制定（archived `lab-os` の "SSOT for AI agent configs" の役割を継承）。
> 2026-06-07 refresh: mother-cleanup（lab-infra→6 抽出）+ アクティブ 21 / archived 5 の現実に group 分類・lineage を整合。

## 命名
- すべて **lowercase-kebab-case**
- `lab-` = 内部 infra / tooling（例: `lab-infra`, `lab-infra-n8n`, `lab-inbox-bot`, `lab-public`）
- `tyl-` = 製品サーフェス（例: `tyl-monorepo`）
- `claude-` / `codex-` = **kit-prefix 例外**（ツール固有の dev-kit。`claude-lab-config`, `claude-lab-skills`, `codex-toolkit`）。`lab-`/`tyl-` 規則からの意図的逸脱として許可。
- upstream OSS と衝突する名前を避ける（`n8n` → `lab-infra-n8n`）
- デフォルトテンプレ名を放置しない（`nextjs-boilerplate` → `tyl-monorepo`）

## ブランチ / マージ
- default branch = **`main`**
- merge method = **squash-only**（merge commit / rebase 無効）
- `delete_branch_on_merge = true`
- 必須 status check を持つ repo を rename する前に、workflow trigger の `branches:` を確認（`[main]` を含める）

## メタデータ（first push 前に必須）
- description（意味のある 1 行）
- topics ≥ 3
- homepage = デプロイ URL または空（**自分の GitHub URL は禁止**）
- social preview（1280×640 PNG, web UI のみ）

## ライセンス
- software → **MIT**
- 文章 / 記事 → **CC-BY-4.0**
- 混在 → dual-license（`denken-os` が reference）
- private repo は license 任意

## セキュリティ
- `default_workflow_permissions = read`
- Actions PR 自己承認 `can_approve_pull_request_reviews` = **false**（許可は allowlist + 正当化）
- secret scanning + push protection（public repo）
- Dependabot alerts ON
- 必須 status check（CodeQL / ci / Build / Secret Check 等）で品質ゲート
- solo 運用のため required review 数は 0（自分の PR を block しない）。`enforce_admins` は emergency hotfix 用に false 維持
- 週次監査: `.github` repo の `weekly-governance-audit` が active repo の repo list / Dependabot alerts / workflow hardening / branch protection / security settings を監査する
- `weekly-governance-audit` は `ORG_GOVERNANCE_AUDIT_TOKEN` があればそれを使い、未設定時は `GITHUB_TOKEN` で到達可能な範囲を監査する。active repo が21件未満しか見えない場合は権限不足として失敗させる
- `lab-infra` は repo-local AGENTS により Codex 変更禁止のため、監査対象には含めるが mutable failure からは除外する

## 依存自動化（Renovate 一本・SSOT）
- dependency bot は **Renovate のみ**。各 repo の `renovate.json` は中央 preset を継承: `{ "extends": ["local>thinkyou0714/.github"] }`。
- 中央 preset = `thinkyou0714/.github` の `default.json`（依存ポリシーの唯一の編集点）。grouping / 安全 automerge(patch + 非major dev-deps) / JST 週次 / `vulnerabilityAlerts` を含む。**Next.js・React・Stripe・Supabase は automerge 禁止**（payment/data/framework critical）。
- **Dependabot version-update は廃止**（`dependabot.yml` は置かない）。二重 bot は同一依存に二重 PR を出し CI を壊す（`pull_request_exists_for_latest_version`）ため禁止。
- Dependabot の **security alerts + automated-security-fixes は backstop として ON 維持**（Renovate `vulnerabilityAlerts` と二重の安全網）。
- repo 固有 override は `extends` 配列に追記（例: `github-flow-kit` は `helpers:pinGitHubActionDigests` 併用）。
- GitHub Actions の version bump は Renovate の `github-actions` group が automerge で追従（Node20→24 deprecation も自動追従）。
- governance CI が依存設定の存在を検査する場合は `renovate.json` を assert すること（`dependabot.yml` ではない）。

## 削除済リポジトリ系譜（supersession） — 旧 archived 5 件は **2026-06-07 に削除**（系譜のみ保存）
| 削除 repo（旧 archived） | superseded by | archived→削除 |
|---|---|---|
| `lab-os` | `claude-lab-config`（AI agent config SSOT を継承） | 2026-05 → 2026-06-07 |
| `obsidian-knowledge-ops` | `obsidian-vault` | 2026-05 → 2026-06-07 |
| `n8n-gmail-vault` | `lab-infra-n8n`（n8n SSOT）+ `tyl-monorepo`（製品） | 2026-05 → 2026-06-07 |
| `skills-registry` | `github-flow-kit` | 2026-05 → 2026-06-07 |
| `lab-n8n-workflows` | `tyl-monorepo`（製品 SSOT）+ `lab-infra-n8n`（n8n SSOT） | 2026-06-01 → 2026-06-07 |

> 旧 archived 5 件は supersession 完了済のため 2026-06-07 に削除（mirror backup 取得済）。本表が系譜の SSOT。以後 active は 21 件のみ。

## 抽出系譜（mother-cleanup, 2026-06）
`lab-infra`（everything-monorepo）から **履歴を保存したまま** 6 repo を抽出（各抽出元には `MOVED.md` tombstone が残る、重複なし）。再 merge は意図に反するため禁止。
| 抽出先 | 旧 path (in lab-infra) | 区分 |
|---|---|---|
| `lab-infra-n8n` | `n8n-unified/`（+ `tools/n8n-ci/`） | infra-private（n8n SSOT） |
| `lab-apps-internal` | `apps/`（autoclaw, signal-core, labctl, ollama-proxy, sva 等） | infra-private |
| `codex-hub` | `apps/codex-hub/` | infra-private |
| `lab-lms` | `lms/` | product-private |
| `lab-skills-private` | `lab-skills/` | infra-private（business-sensitive） |
| `lab-inbox-bot` | `apps/lab-slack-bot/`（lineage: `archive/mother-lab-slack-bot` branch） | infra-private |

## グループ分類（active 21 / archived 0 = 21）— 2026-06-07 現在の SSOT
**active = 21**（旧 archived 5 件は 2026-06-07 削除。機械可読版は `.github/repos.json`、`weekly-governance-audit` はそれを参照）:
- **flagship-OSS**（public, MIT, 5）: `ccmux`, `github-flow-kit`, `codex-toolkit`, `denken-os`, `claude-lab-skills`
- **content / docs**（public, 5）: `public-docs`, `zenn-content`, `lab-public`, `thinkyou0714`(profile), `.github`(org health)
- **product-private**（2）: `tyl-monorepo`, `lab-lms`
- **infra-private**（9）: `lab-infra`(everything-monorepo shell + 公開ミラー), `lab-infra-n8n`(n8n SSOT), `lab-apps-internal`, `codex-hub`, `claude-lab-config`, `lab-skills-private`, `obsidian-vault`, `lab-inbox-bot`, `private-members`

**archived = 0**（旧 archived 5 件は 2026-06-07 削除済。系譜は上の「削除済リポジトリ系譜」表を参照）

### public / private skill 境界（重要）
- `claude-lab-skills`（public, MIT, tech-agnostic）と `lab-skills-private`（private, business-sensitive）は **意図的な公開/非公開 split**。`lab-data-auth-ops` / `lab-strategy-design` の pack 名は両方に存在するが**中身は別物**（public=汎用、private=事業固有）。混在禁止（CLAUDE.md hard rule）。
- `github-flow-kit`（public SSOT）の skill は `claude-lab-config`（private consumer）にも置かれる = OSS-authored-publicly / consumed-locally pattern（事故コピーではない）。
