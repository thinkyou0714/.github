# 個人開発者 GitHub ベストプラクティス 100（BEST-PRACTICES）

> 個人開発者（solo maintainer）として GitHub を運用するためのベストプラクティス 100 項目の SSOT。
> 各項目に、規範（一般に通用するプラクティス）と、このアカウント（thinkyou0714）での**採用状況・根拠・次の一手**を紐付けた「規範 × 監査」チェックリスト。
> 初版 2026-07-13（10 カテゴリ × 10 項目。マルチエージェントで起草し、全項目を repo 実ファイル・governance 記録と突き合わせて検証）。
> 規約の実装は [`CONVENTIONS.md`](CONVENTIONS.md)、改善候補の管理は [`IMPROVEMENT-BACKLOG.md`](IMPROVEMENT-BACKLOG.md)、日付つき実測は `AUDIT-*.md` / [`governance/`](governance/) を参照。

**凡例**: ✅ 採用済（実ファイル / 検証記録に根拠あり）· ⚠️ 部分的（不整合・未展開あり）· ❌ 未採用。
「現状」のうち他 repo・アカウント設定に関する記述は、本 repo の governance 文書が記録する内容の引用（記録日付つき）。

**運用ルール**:
- 常に 100 項目を維持する（追加したい規範があれば、価値の低い項目と番号ごと差し替える）
- ステータス昇格（❌/⚠️ → ✅）には必ず根拠（ファイル / 検証記録）を書く。降格も同様
- 「次の一手」を実施したら本ファイルと `IMPROVEMENT-BACKLOG.md` の Done 記録を同一 PR で更新する

## サマリ

| カテゴリ | ✅ | ⚠️ | ❌ |
|---|--:|--:|--:|
| C1. リポジトリ設計・構造・メタデータ（BP-001〜010） | 6 | 4 | 0 |
| C2. ブランチ・コミット運用（BP-011〜020） | 6 | 4 | 0 |
| C3. Issue・PR 運用（BP-021〜030） | 8 | 2 | 0 |
| C4. GitHub Actions・CI（BP-031〜040） | 5 | 5 | 0 |
| C5. セキュリティ（アカウント・リポ設定）（BP-041〜050） | 1 | 7 | 2 |
| C6. 依存管理・サプライチェーン（BP-051〜060） | 7 | 2 | 1 |
| C7. ドキュメント・コミュニティヘルス（BP-061〜070） | 4 | 4 | 2 |
| C8. リリース・バージョニング（BP-071〜080） | 0 | 5 | 5 |
| C9. AI エージェント協働開発（BP-081〜090） | 3 | 6 | 1 |
| C10. 運用・ガバナンス継続（BP-091〜100） | 9 | 1 | 0 |
| **合計（2026-07-13 時点）** | **49** | **40** | **11** |

## C1. リポジトリ設計・構造・メタデータ（BP-001〜BP-010）

#### BP-001 ✅ lowercase-kebab-case 命名と prefix 体系の規約化
- **規範**: 全 repo を lowercase-kebab-case で命名し、用途別 prefix（内部 infra / 製品 / ツール kit）の体系を規約として明文化する。upstream OSS と衝突する名前やテンプレ由来のデフォルト名は first push 前に排除し、例外は逸脱理由ごと規約に記録する。
- **理由**: 名前だけで repo の役割・分類が判別でき、検索・監査・自動化の前提が安定する。
- **現状**: ✅ 採用済 — CONVENTIONS.md 命名節: lowercase-kebab-case 必須、lab-=内部 infra / tyl-=製品 / claude-・codex-=kit-prefix 例外（意図的逸脱として明文化）、upstream 衝突回避（n8n → lab-infra-n8n）、デフォルトテンプレ名放置禁止（nextjs-boilerplate → tyl-monorepo）。repos.json（2026-07-08）の active 28 repo 名は全て kebab-case 準拠。

#### BP-002 ⚠️ 1 repo = 1 責務と SSOT 宣言
- **規範**: 各 repo に単一の責務を持たせ、ドメインごとに「どの repo が SSOT か」を1箇所で宣言する。境界の曖昧さや記述の矛盾は発見次第、宣言側を更新して解消する。
- **理由**: 同じ資産が複数 repo に散ると、どれが正か判別できず編集・自動化が事故る。
- **現状**: ⚠️ 部分的 — repos.json は28件全てに purpose 1行を付与、ARCHITECTURE.md に「SSOTs: n8n = lab-infra-n8n · product = tyl-monorepo · dev-kits = claude-lab-config / codex-toolkit」。ただし lab-os と claude-lab-config の境界記述が矛盾: CONVENTIONS.md 2026-07-08 節は「owner-confirmed "keep both"」、repos.json の lab-os purpose は「canonical status vs claude-lab-config is a pending owner decision」。
- **次の一手**: lab-os（repo）と claude-lab-config（runtime component）の canonical 境界の決定を CONVENTIONS.md に一本化し、repos.json の lab-os purpose 文言を「keep both」決定に同期させる。

#### BP-003 ⚠️ monorepo からの履歴保存抽出と tombstone
- **規範**: monorepo から repo を切り出すときは git 履歴を保存したまま抽出し、抽出元の旧 path に移設先を指す tombstone（MOVED.md）を統一書式で残す。抽出後の再 merge 禁止も明文化する。
- **理由**: 履歴と旧 path からの導線が残らないと blame・過去調査・リンクが断絶し、二重管理が再発する。
- **現状**: ⚠️ 部分的 — CONVENTIONS.md 抽出系譜節（mother-cleanup, 2026-06）: lab-infra から履歴を保存したまま6 repo 抽出、「各抽出元には MOVED.md tombstone が残る、重複なし」「再 merge は意図に反するため禁止」と記録。一方 IMPROVEMENT-BACKLOG.md（2026-06-07）に「lab-infra の旧 n8n-unified/ path への tombstone 追加」（P2.2）と「mother-cleanup 抽出の tombstone 品質が不均一」（P1.65）が未消化で残存。
- **次の一手**: lab-infra の旧 n8n-unified/ 位置に lab-infra-n8n を指す tombstone を追加し、抽出6件の MOVED.md を「extracted from lab-infra/<path> + 移設日 + 移設先リンク」の統一書式に揃える（backlog P2.2/P1.65 消化）。

#### BP-004 ✅ アーカイブ・削除の supersession 系譜記録
- **規範**: repo をアーカイブ・削除する前に「superseded by どれか」「いつ archived → 削除したか」を系譜表として governance SSOT に残し、削除時は mirror backup を取る。名前を再利用して repo を再作成した場合も系譜を追記する。
- **理由**: 削除後も後継への導線と復元手段が残り、名前の再利用や過去参照で迷子にならない。
- **現状**: ✅ 採用済 — CONVENTIONS.md「削除済リポジトリ系譜（supersession）」表: 旧 archived 5件の superseded by・archived→削除日付（2026-05/06-01 → 2026-06-07）・「mirror backup 取得済」を記録。repos.json にも deleted_2026_06_07 配列として機械可読で保持。lab-os / skills-registry / lab-research の再作成（2026-07-05 ほか）も CONVENTIONS.md 2026-07-08 reconciliation 節で系譜更新済。

#### BP-005 ⚠️ description・topics(≥3)・homepage の first-push 前整備
- **規範**: description（意味のある1行）・topics 3個以上・homepage（デプロイ URL または空。自分の GitHub URL は禁止）を first push 前に整備し、規約として強制する。topics は語彙を正準化してアカウント内で揺らさない。
- **理由**: 発見性と一覧性が repo 作成直後から担保され、後追い整備のコストと放置を防ぐ。
- **現状**: ⚠️ 部分的 — CONVENTIONS.md メタデータ節に「first push 前に必須」として description / topics ≥ 3 / homepage（自分の GitHub URL は禁止）を規定。ただし IMPROVEMENT-BACKLOG.md（2026-06-07）に未消化項目として、thinkyou0714・lab-public の homepage=github.com/thinkyou0714（規約違反）、topics 語彙 drift（solo-dev / solo-developer）と private-members・obsidian-vault の generic topics、lab-infra description の抽出前内容の陳腐化が記録されている。
- **次の一手**: homepage 違反2 repo を是正し、topics の正準語彙を CONVENTIONS.md に定義して全 active repo に適用、lab-infra description を抽出後の実態（infra shell）に書き直す（backlog P1.65/P1.1 消化）。

#### BP-006 ✅ special .github repo によるデフォルトファイル集約
- **規範**: アカウント直下に special .github repo を置き、CONTRIBUTING・CODE_OF_CONDUCT・SECURITY・SUPPORT・FUNDING・Issue/PR テンプレを全 repo のフォールバックとして集約する。個別 repo は要件が異なる場合のみ同名ファイルで上書きする。
- **理由**: community health files を repo ごとに複製せず1箇所で保守でき、新規 repo も作成即座に全ファイルの恩恵を受ける。
- **現状**: ✅ 採用済 — 本リポジトリ自体が実装。README.md がフォールバック機構・提供ファイル一覧・上書きルールを明記し、CONTRIBUTING.md / CODE_OF_CONDUCT.md / SECURITY.md / SUPPORT.md / FUNDING.yml / .github/ISSUE_TEMPLATE/{bug_report,feature_request,question,config}.yml / PULL_REQUEST_TEMPLATE.md が実在。AUDIT-2026-07.md（2026-07-03）の採点も「org-inherited COC/SECURITY/CONTRIBUTING」を全 repo の Community-health 点として計上。

#### BP-007 ⚠️ プロフィール README repo の維持と pinned repos の整列
- **規範**: ユーザー名と同名の repo にプロフィール README を置き、代表作・現行プロジェクトをアカウントの顔として定期棚卸しする。pinned repos は repo のグループ分類（flagship 等）と一致させる。
- **理由**: 来訪者（採用・OSS ユーザー）への最初の導線であり、陳腐化すると全 repo の信頼度を下げる。
- **現状**: ⚠️ 部分的 — repos.json に thinkyou0714（public, content-docs, purpose "Profile README"）を登録。IMPROVEMENT-BACKLOG.md「Done in the 2026-07 pass」に「Refreshed the account profile README (thinkyou0714 #17): skill count 4→6, added fugu/codex-toolkit/claude-lab-skills, Zenn published」と更新実績を記録。ただし同 backlog に pinned repos を flagship-OSS 分類（ccmux, github-flow-kit, codex-toolkit, denken-os, claude-lab-skills, public-docs）に揃える項目と、profile repo の7 branches 整理（P2.2）が未消化で残存。
- **次の一手**: profile の pinned 6枠を flagship-oss group と一致させ、profile repo に残る7 branches（自動 commit / 放置編集の疑い）を調査して main に集約する。

#### BP-008 ✅ 機械可読リポジトリ台帳（repos.json）の SSOT 化
- **規範**: 全 repo の name・visibility・group・purpose・削除系譜を機械可読の台帳（repos.json 等）として version 管理し、監査・自動化は必ず台帳を読む。台帳の値を自動化側に hardcode する二重管理（magic number）を作らない。
- **理由**: repo 数が増えるほど prose の一覧は腐るため、自動化が読める構造化 SSOT がガバナンスの土台になる。
- **現状**: ✅ 採用済 — repos.json（generated 2026-07-08）: total/active_count=28、28件全てに group・visibility・purpose、deleted_2026_06_07 系譜付き。weekly-governance-audit.yml は閾値を渡さず、scripts/audit-github-governance.ps1 が repos.json の active_count を読んで閾値化（SSOT 読取失敗は hard error — 2026-07-13 修正）。stale-branch-gc.yml も列挙 repo 数を active_count と突合。ci.yml が active_count/total/archived_count の内部整合を PR ごとに assert。

#### BP-009 ✅ repo map（ARCHITECTURE）の鮮度維持
- **規範**: 機械可読台帳とは別に人間向けの repo map（ARCHITECTURE.md）を1枚維持し、repo の増減・改名・再作成のたびに台帳と同期して更新する。可能なら台帳から自動生成して drift を検査する。
- **理由**: 一覧地図が古いと、新規セッションの AI エージェントや将来の自分が誤った全体像を前提に作業してしまう。
- **現状**: ✅ 採用済 — ARCHITECTURE.md は 2026-07-13 に repos.json（28 repo）から再生成済（lab-os / skills-registry 再作成の注記つき）。ヘッダに機械検査用マーカー `<!-- repos.json active_count: 28 -->` を持ち、ci.yml「Verify ARCHITECTURE.md matches repos.json」が repos.json 変更時の追従漏れを CI fail で強制する。

#### BP-010 ✅ public・private の分割基準の明文化
- **規範**: 公開してよい汎用資産と事業固有資産を repo レベルで分割し、境界（何が public で何が private か）と混在禁止を規約に明文化する。同名の資産が両側に存在する場合は「中身は別物」であることまで記録する。
- **理由**: 公開/非公開の境界が暗黙だと、business-sensitive な内容の誤公開という不可逆の事故につながる。
- **現状**: ✅ 採用済 — CONVENTIONS.md「public / private skill 境界(重要)」節: claude-lab-skills（public, MIT, tech-agnostic）と lab-skills-private（private, business-sensitive）は意図的 split、同名 pack でも「中身は別物(public=汎用、private=事業固有)。混在禁止(CLAUDE.md hard rule)」。ARCHITECTURE.md も content split（public-docs 無償 / private-members 有償）と OSS-authored-publicly / consumed-locally pattern を記録。repos.json は28件全てに visibility と group を付与。


## C2. ブランチ・コミット運用（BP-011〜BP-020）

#### BP-011 ✅ default branch は main に統一
- **規範**: 全 repo の default branch を main に統一する。master 等の残存参照（README・CI trigger・スクリプト）も併せて是正する。
- **理由**: default branch 名の揺れは workflow trigger・自動化スクリプト・ドキュメントの分岐を生み、solo でも認知コストと事故点を増やすため。
- **現状**: ✅ 採用済 — CONVENTIONS.md「ブランチ / マージ」節に「default branch = main」を明記。IMPROVEMENT-BACKLOG.md の Done 節に「Fixed public-docs README (master → main)」と記録（2026-06-07）。stale-branch-gc.yml も default_branch を API 取得（fallback main）で main 前提を運用に組込済。

#### BP-012 ⚠️ solo でも main 直 push せず PR 経由
- **規範**: solo 開発でも main へ直 push せず、branch → PR → merge の経路に統一する。required review は 0 でよいが、PR という単位・CI ゲート・issue 連携の記録は省略しない。
- **理由**: PR 経由は CI 実行・変更理由の記録・issue 自動 close（Closes #N）を構造的に保証し、solo 特有の「動くが説明できない履歴」を防ぐため。
- **現状**: ⚠️ 部分的 — CONTRIBUTING.md Quick start に「Fork → branch → PR — main への直接 push は避ける」、PULL_REQUEST_TEMPLATE.md（Summary/Why/Closes #N/Test plan）完備。一方、本 repo の git log には PR 番号なしの main 直 push が多数（fb730cd, 9fa00b2, dc6dd59 等 2026-06 の governance 系 commit）。branch protection も self-merge 許可・PR 必須化なしと記録（IMPROVEMENT-BACKLOG.md 2026-07 Done 節「self-merge allowed」）。
- **次の一手**: public repo の ruleset に「require a pull request before merging」（approvals 0 のまま）を追加し、governance 系変更も PR 経由へ移行。weekly-governance-audit に main への direct push 検知を追加。

#### BP-013 ✅ merge method は squash-only
- **規範**: merge method は squash-only に固定し、merge commit と rebase merge をリポ設定で無効化する。main 上の 1 commit = 1 PR を保つ。
- **理由**: squash-only は WIP commit のノイズを消し、履歴を PR 単位で読める・bisect できる・revert できる形に保つため。
- **現状**: ✅ 採用済 — CONVENTIONS.md「ブランチ / マージ」節「merge method = squash-only（merge commit / rebase 無効）」。IMPROVEMENT-BACKLOG.md Done 節に「Enforced squash-only + delete_branch_on_merge across all repos (free settings API)」と記録（2026-06-07）。本 repo の git log も (#N) 付き squash commit で構成。

#### BP-014 ✅ delete_branch_on_merge を有効化
- **規範**: delete_branch_on_merge = true を全 repo で有効化し、merge 済 branch を自動削除する。
- **理由**: merge 済 branch の自動削除は branch 一覧を「生きている作業」だけに保ち、続かない手動掃除への依存を排除するため。
- **現状**: ✅ 採用済 — CONVENTIONS.md「ブランチ / マージ」節「delete_branch_on_merge = true」。IMPROVEMENT-BACKLOG.md Done 節に全 repo 適用を記録（2026-06-07）。security-baseline-2026-06-07.md Notes は private repo の補償統制として squash-only + delete_branch_on_merge を明記。stale-branch-gc.yml も「not caught by delete_branch_on_merge」な未 merge branch の backstop と自己定義。

#### BP-015 ⚠️ linear history 維持・force-push 禁止（取り消しは revert）
- **規範**: main は linear history を維持し、force-push と branch 削除を protection でブロックする。公開済み履歴の取り消しは git revert で行い、履歴改変はしない。
- **理由**: push 済み履歴の改変は clone・PR・CI・permalink の参照を壊す不可逆事故の筆頭であり、revert なら記録を残して安全に戻せるため。
- **現状**: ⚠️ 部分的 — IMPROVEMENT-BACKLOG.md 2026-07 Done 節に「全 14 public repo へ light solo-friendly protection（linear history, block force-push/deletion, strict status checks, self-merge allowed）適用」と記録。AUDIT-2026-07.md R3: private 8 repo は「403 Upgrade to GitHub Pro」で deferred（Free プラン、2026-07-03）。governance/claude-code-convention.md は agent の permissions.deny に git push --force* / git reset --hard* を明示。ただし revert-first の明文規則は CONVENTIONS.md に無い。。なお「main の取り消しは revert のみ・force-push 禁止」は 2026-07-13 に CONVENTIONS.md ブランチ/マージ節へ明文化済
- **次の一手**: weekly-governance-audit に branch-protection presence check（backlog 記載項目）を追加し、private 8 repo は GitHub Pro 移行時に同一 protection を適用する。

#### BP-016 ✅ Conventional Commits
- **規範**: commit message と PR タイトルは Conventional Commits（type(scope): subject）に統一する。
- **理由**: 型付き履歴は grep・changelog 生成・semantic versioning 判定を機械化でき、solo でも将来の自分への最良のログになるため。
- **現状**: ✅ 採用済 — CONTRIBUTING.md に書式（<type>(<scope>): <subject>）と feat/fix/docs/style/refactor/perf/test/chore/ci の type 表を規定、「タイトルは Conventional Commits 形式」も明記。PULL_REQUEST_TEMPLATE.md checklist に「Conventional commit message」。本 repo の直近 git log 25 件すべて type(scope): 形式で準拠。

#### BP-017 ✅ コミット粒度 = 1 論理変更
- **規範**: 1 commit / 1 PR = 1 論理変更に保つ。機能追加と refactor を混ぜず、無関係な変更は分割して出す。
- **理由**: 単一関心の変更は差分レビュー・git bisect・revert の単位としてそのまま機能し、混在 commit は取り消し不能な塊になるため。
- **現状**: ✅ 採用済 — CONTRIBUTING.md PR ガイドライン「小さく、レビューしやすく — 1 PR = 1 concern（機能追加と refactor は分ける）」。CONVENTIONS.md の squash-only 方針により main 上で 1 commit = 1 PR = 1 concern が構造的に成立。本 repo の git log も単一関心 commit で構成。

#### BP-018 ✅ ブランチ命名規約（人間用 + AI agent namespace）
- **規範**: 作業 branch は feature/<slug>・fix/<slug> 等の型付き命名にし、AI agent が切る branch は claude/・codex/ の専用 namespace に隔離する。
- **理由**: 命名規約は branch の由来（人間/agent）と目的を一目で判別可能にし、自動 GC・監査での機械的な対象選別を成立させるため。
- **現状**: ✅ 採用済 — agent namespace は運用実態あり: stale-branch-gc.yml の default prefixes「codex/,claude/」、IMPROVEMENT-BACKLOG.md Done 節「Pruned 123 abandoned agent branches (codex/*, claude/*)」（2026-06-07）、本作業 branch も claude/ prefix。人間用の型付き命名（feature/<slug>・fix/<slug>）と「merge 済 branch は 7 日以内に削除」の lifecycle も 2026-07-13 に CONVENTIONS.md ブランチ/マージ節へ成文化済。

#### BP-019 ⚠️ 短命ブランチのトランクベース運用
- **規範**: branch は短命に保ち、小さく作って早く merge するトランクベースで運用する。PR を open のまま滞留させない。
- **理由**: 長命 branch は main との乖離・conflict・「どれが正か」の混乱を蓄積し、solo では放置がそのまま技術的負債になるため。
- **現状**: ⚠️ 部分的 — 支える仕組みは整備済（CONVENTIONS.md の squash-only + delete_branch_on_merge、stale-branch-gc.yml）。しかし AUDIT-2026-07.md §2 に「most canonical clones sit on a feature branch, not main ... mirrors the ~50 open PRs」、deferred 節に stale branch 残数（agmsg 30 / lab-infra 22 / tyl-monorepo 15 / ccmux 11）と記録（2026-07-03）。IMPROVEMENT-BACKLOG.md「One-time PR-cleanup pass: drive stale PRs to a terminal state」も未消化。
- **次の一手**: backlog「One-time PR-cleanup pass」を実行し滞留 ~50 open PR を merged/closed に triage。branch max-age（例: 30 日）を命名規約と併せて成文化し、weekly-governance-audit で残数を継続監視。

#### BP-020 ⚠️ stale branch の定期 GC（dry-run→apply の 2 段階）
- **規範**: merge されず放置された branch は定期 GC で掃除する。schedule 実行は dry-run report のみとし、削除は明示的な apply 実行に限る 2 段階で運用する。
- **理由**: branch 自動削除は誤爆が不可逆なため、report→人間確認→apply の 2 段階が安全性と掃除の継続性を両立するため。
- **現状**: ⚠️ 部分的 — .github/workflows/stale-branch-gc.yml: 週次 schedule は report-only（job summary 出力）、削除は workflow_dispatch の apply=true のみ、permissions: contents: read、open PR がある branch を除外、30 日閾値・prefixes codex/,claude/。IMPROVEMENT-BACKLOG.md Done 節に 123 branch prune（restore manifest 保存）と記録（2026-06-07）。ただし同 2026-07 Done 節は「Still deferred: ... stale-branch GC」と記録し、AUDIT-2026-07.md も agmsg 30 / lab-infra 22 等の残債を deferred と明記 — apply 運用が追いついていない。。workflow 自体は 2026-07-13 に安全強化済: apply=true は PAT 必須（fail-fast）、open PR 列挙をページネーション付き API に変更（31 件目以降の PR の branch 誤削除リスクを解消）、未マージ commit を持つ branch は自動削除対象外、削除行に SHA を記録（restore manifest）
- **次の一手**: 直近の dry-run job summary を確認し、workflow_dispatch apply=true で残 stale branch（agmsg 30 / lab-infra 22 / tyl-monorepo 15 / ccmux 11 と記録）を掃除する。


## C3. Issue・PR 運用（BP-021〜BP-030）

#### BP-021 ✅ Issue Forms (YAML) で必須項目を構造化
- **規範**: Issue テンプレートは Markdown ではなく Issue Forms (YAML) で定義し、再現手順・期待挙動・バージョン等の必須項目に validations.required を設定せよ。自由記述任せにせず、triage に必要な情報を入力段階で構造化する。
- **理由**: 必須項目の構造化が「情報不足で triage 不能な Issue」との往復を入口で排除し、solo の限られた時間を守るため。
- **現状**: ✅ 採用済 — .github/ISSUE_TEMPLATE/bug_report.yml（What happened? / Steps to reproduce / Expected behavior / Version の4項目に validations.required: true、Logs は render: shell）、feature_request.yml（Use case / Proposed solution 必須）、question.yml（summary / repository / context / type 必須）。README.md「1. Default community health files」の通り .github 特別リポジトリ機構で全 repo のフォールバックとして機能。（テンプレ群は 2026-07-13 に仕様準拠の .github/ISSUE_TEMPLATE/ へ移動 — default issue templates は同ディレクトリ配下必須）

#### BP-022 ✅ blank_issues_enabled: false + contact_links で起票導線を制御
- **規範**: ISSUE_TEMPLATE/config.yml で blank_issues_enabled: false を設定し、テンプレートを経ない空 Issue を塞げ。質問は Discussions へ、脆弱性は private reporting へ contact_links で誘導する。
- **理由**: 空 Issue の遮断と導線の明示が、非構造 Issue の triage コストと脆弱性の公開 Issue 化事故を同時に防ぐため。
- **現状**: ✅ 採用済 — .github/ISSUE_TEMPLATE/config.yml の blank_issues_enabled: false + contact_links 2件。contact_links の行き先は 2026-07-13 に実在の導線へ修正済（Question or discussion → SUPPORT.md、Security vulnerability report → SECURITY.md）。SUPPORT.md「Routing order」（docs → 既存 Issue 検索 → Discussions → テンプレ起票）と導線が整合。テンプレ群は同日、default issue templates の仕様（.github/ISSUE_TEMPLATE 配下必須）に合わせ root から移動済。

#### BP-023 ⚠️ ラベル体系を一元定義し全 repo に同期
- **規範**: ラベルの名前・用途・色を一箇所で定義し、全 repo に同期せよ。Issue テンプレートや bot が付与するラベルは、その定義済み体系から引く。
- **理由**: repo ごとにラベルが揺れると横断検索・フィルタ・自動化（automerge 条件等）が機能せず、repo 数の多い個人ほど破綻するため。
- **現状**: ⚠️ 部分的 — 付与側は存在: ISSUE_TEMPLATE/*.yml が bug / enhancement / question を自動付与、default.json（Renovate 中央 preset）が dependencies / security / vulnerability / framework-major / stripe-critical / supabase-critical を付与。しかし規約 SSOT の CONVENTIONS.md にラベル体系の節がなく（命名 / ブランチ / メタデータ / ライセンス / セキュリティ / 依存自動化のみ）、28 repo（repos.json）へのラベル定義同期・存在検証の機構もない。
- **次の一手**: CONVENTIONS.md にラベル体系（名前・色・用途、テンプレ/Renovate が参照するラベルの完全列挙）を追記し、weekly-governance-audit（scripts/audit-github-governance.ps1）に各 active repo でのラベル存在 assert を追加する（または github-label-sync 等で配布）。

#### BP-024 ✅ PR と Issue を Closes #N で必ず連携
- **規範**: Issue を解決する PR には必ず Closes/Fixes/Resolves #N を書き、merge 時に Issue を自動 close させよ。対応 Issue がない場合も「no issue」と明示し、リンク漏れを許さない。
- **理由**: リンク漏れは「実装済みなのに open のままの stale issue」を蓄積させ、backlog を信頼できない台帳に変えるため。
- **現状**: ✅ 採用済 — PULL_REQUEST_TEMPLATE.md「Linked issues」節が理由まで明記（"Skipping this is how the backlog accumulates stale 'already done but still open' issues"、1 issue につき 1 keyword、Closes # プレースホルダ）+ Checklist に「**Linked the issue(s) this resolves with `Closes #N`** (or "no issue")」。CONTRIBUTING.md の commit footer 例も「Closes #123」。

#### BP-025 ✅ PR テンプレートに Test plan と Risk 欄
- **規範**: PR テンプレートに Test plan（どう検証したかの checklist）と Risk（Low/Medium/High + 壊れ得る箇所）の欄を置き、毎 PR で埋めよ。solo でも将来の自分と AI agent への引き継ぎ記録として書く。
- **理由**: 検証方法とリスクの明文化が、レビュアー不在の solo における唯一の品質ゲート記録となり、障害時の切り分けと revert 判断を速くするため。
- **現状**: ✅ 採用済 — PULL_REQUEST_TEMPLATE.md の「## Test plan」（checkbox 形式）と「## Risk」（"Low / Medium / High — and what could break?"）。CONTRIBUTING.md PR ガイドライン「Test plan を含める — どう動作確認したか箇条書きで」とも整合。

#### BP-026 ✅ Draft PR の活用
- **規範**: 完成前の変更は Draft PR で開き、CI を回しながら WIP であることを機械可読に明示せよ。ready 化するまで merge 対象として扱わない。
- **理由**: Draft 状態が「CI は回したいが merge はまだ」という solo 開発の常態を API/UI 上で判別可能にし、事故 merge や自動化の誤爆を防ぐため。
- **現状**: ✅ 採用済 — CONTRIBUTING.md PR ガイドライン「Draft PR OK — early feedback が欲しい場合は draft で出す」。実運用の記録として IMPROVEMENT-BACKLOG.md（2026-06-07）が codex-hub PR #11（CSP 強化）を open draft として記録している。

#### BP-027 ✅ セルフレビュー（solo でも PR diff を通読）
- **規範**: solo でも merge 前に自分の PR の Files changed を全行通読せよ。AI agent 生成の PR は特に、意図しない変更・秘密情報・無関係 diff の混入を人間の目で確認してから merge する。
- **理由**: required review 0 の solo 運用ではセルフレビューが merge 前の最後の人間チェックであり、これを省くと bot/agent の出力がノーチェックで main に入るため。
- **現状**: ✅ 採用済 — PULL_REQUEST_TEMPLATE.md の Checklist に「**Self-reviewed the full diff**（Files changed を通読した — AI agent 生成 PR は特に）」を追加、CONTRIBUTING.md の PR ガイドラインにも「セルフレビュー必須」を明記（いずれも 2026-07-13）。required review 0 の solo 運用（CONVENTIONS.md セキュリティ節）における merge 前最終ゲートとして文書で固定。

#### BP-028 ✅ 小さい PR（1 PR = 1 concern）
- **規範**: 1 PR には 1 つの関心事だけを入れよ。機能追加と refactor、依存更新と挙動変更は別 PR に分ける。
- **理由**: 小さい PR はセルフレビュー・revert・bisect の単位を成立させ、squash merge 履歴を意味のある changelog にするため。
- **現状**: ✅ 採用済 — CONTRIBUTING.md PR ガイドライン「小さく、レビューしやすく — 1 PR = 1 concern (機能追加と refactor は分ける)」。default.json も依存更新を関心事単位の PR に分離（github-actions group、Next.js framework group、Supabase group 等）しており方針と整合。

#### BP-029 ⚠️ open PR を terminal state（merge/close）へ定期駆動
- **規範**: open PR を溜め込まず、定期的に merge か close の terminal state へ駆動せよ。決められないなら close して Issue に理由を残し、branch と backlog を実態に一致させる。
- **理由**: PR が open のままだと delete_branch_on_merge も stale-branch GC も効かず（open PR の head branch は GC 対象外）、branch 一覧と backlog が実態を映さなくなるため。
- **現状**: ⚠️ 部分的 — bot PR は default.json（platformAutomerge: true、patch/非major devDeps の automerge、prConcurrentLimit: 5）で terminal state へ自動駆動済。一方 AUDIT-2026-07.md（2026-07-03 生成）は「~50 open PRs」を記録し、IMPROVEMENT-BACKLOG.md（2026-06-07）の「One-time PR-cleanup pass: drive stale PRs to a terminal state」（P1.1、tyl-monorepo/ccmux/lab-lms/codex-hub/claude-lab-config 対象）は未実施のまま。stale-branch-gc.yml は open PR の head branch を明示的にスキップする実装（prheads を grep で除外）で、PR 放置がそのまま branch 放置に直結する。
- **次の一手**: backlog 記載の PR-cleanup pass（tyl-monorepo / ccmux / lab-lms / codex-hub / claude-lab-config の open PR triage）を実施し、weekly-governance-audit に「open PR 数・最古 open PR の経過日数」の報告と閾値 assert を追加して定期駆動化する。

#### BP-030 ✅ Issue 起票前の重複検索を required checkbox で強制
- **規範**: Issue を立てる前に既存 Issue/Discussions と docs を検索させ、その実施を Issue Forms の required checkbox で宣言させよ。自分が自 repo に起票する場合も同じ規律に従う。
- **理由**: 重複 Issue は triage と close 往復の純粋なコストであり、起票フォーム側で検索を強制するのが最も安い防止点のため。
- **現状**: ✅ 採用済 — question.yml の Pre-submit checklist（既存 issue/discussions 検索・README/docs 確認が required: true）に加え、2026-07-13 に bug_report.yml / feature_request.yml へも「I searched existing issues/discussions for duplicates.」の required checkbox を追加し 3 テンプレで統一。CONTRIBUTING.md「Issues を先に確認」、SUPPORT.md Routing order とも整合。


## C4. GitHub Actions・CI（BP-031〜BP-040）

#### BP-031 ✅ workflow token の最小権限（top-level permissions: contents: read）
- **規範**: すべての workflow に top-level で permissions: contents: read を明示し、write が必要な場合のみ job 単位で必要最小の scope を付与する。
- **理由**: GITHUB_TOKEN の既定権限を read に絞れば、悪意ある action や script injection が成立しても被害を読み取りのみに封じ込められる。
- **現状**: ✅ 採用済 — .github/workflows の全 workflow が top-level `permissions: contents: read` を宣言。唯一の write は weekly-governance-audit の keepalive job における job-level `actions: write`（規範どおりの job 単位最小付与、2026-07-13 追加）。scripts/audit-github-governance.ps1 の Test-TopLevelReadPermissions が top-level の write 付与を fail 判定して週次で全 repo を検査（`permissions: {}` / `read-all` 等の正当な短縮形も 2026-07-13 から許容）。security-baseline-2026-06-07.md に「All repos: default_workflow_permissions=read」と記録（2026-06-07）。

#### BP-032 ✅ concurrency 制御と cancel-in-progress
- **規範**: workflow に concurrency（group = workflow×ref）を設定し、CI 系は cancel-in-progress: true で旧 run を打ち切る。削除等の破壊的 job は cancel-in-progress: false + 固定 group で直列化する。
- **理由**: 連続 push で無駄な run が積み上がるのを防ぎ、個人開発の限られた Actions 無料枠と feedback 速度を守る。
- **現状**: ✅ 採用済 — 全 workflow が concurrency を宣言: CI 系は `group: ${{ github.workflow }}-${{ github.ref }}` + `cancel-in-progress: true`、削除系の stale-branch-gc.yml は意図どおり固定 group + `cancel-in-progress: false`。この意図的例外を missingHardening と誤判定して自リポの週次監査を fail させ得た scripts/audit-github-governance.ps1 の判定は、2026-07-13 に「非空 group + 明示的 cancel-in-progress（true/false）」へ修正済。

#### BP-033 ✅ 全 job への timeout-minutes 明示
- **規範**: すべての job に timeout-minutes を明示する。既定の360分に依存せず、通常所要時間の数倍程度を上限とする。
- **理由**: hang した run が既定6時間分の Actions 分数を浪費し、concurrency group 内の後続 run を塞ぐ事故を防ぐ。
- **現状**: ✅ 採用済 — 全 job に timeout-minutes を明示（2026-07-13 追加分含む）: ci 10 / dependency-review 10 / secrets-scan 10 / weekly-governance-audit 20 + keepalive 5 / stale-branch-gc 30。

#### BP-034 ⚠️ action の digest（commit SHA）ピン留め
- **規範**: サードパーティ action は mutable tag（@v4 等）ではなく commit SHA digest で参照し、更新追従は Renovate の helpers:pinGitHubActionDigests に任せる。
- **理由**: tag は force-push で差し替え可能であり、digest 固定だけが action のサプライチェーン改竄（tag 移動攻撃）を構造的に防ぐ。
- **現状**: ⚠️ 部分的 — default.json L5 が中央 Renovate preset として `helpers:pinGitHubActionDigests` を extends し、renovate.json の `"local>thinkyou0714/.github"` 継承で全 repo に配布。security-baseline-2026-06-07.md L11 に「SHA-pinning: central Renovate preset extends helpers:pinGitHubActionDigests (account-wide)」と記録（2026-06-07）。しかし当 repo の workflow 実体は actions/checkout@v6・actions/upload-artifact@v4・actions/dependency-review-action@v4・gitleaks/gitleaks-action@v2 と全て tag 参照のままで preset と実態が乖離。IMPROVEMENT-BACKLOG.md にも「Make weekly-governance-audit assert SHA-pinning」(P1.47) が未了で残る（2026-06-07）。
- **次の一手**: Renovate の pin PR を merge（来ていなければ手動で digest + version コメント形式に固定）し、weekly-governance-audit に「uses: が SHA 参照であること」の assert を追加する。

#### BP-035 ⚠️ actionlint による workflow lint
- **規範**: workflow YAML を actionlint で CI 検査し、構文・expression・permissions・shell の誤りを PR 時点で落とす。
- **理由**: workflow の誤りは merge 後の実行時にしか露見せず、修正 push の往復コストが個人開発では特に高くつく。
- **現状**: ⚠️ 部分的 — 当 repo の ci.yml は PyYAML の yaml.safe_load による syntax 検査のみ（L38-49）で actionlint 未導入。IMPROVEMENT-BACKLOG.md CI/CD 節（2026-06-07）に「github-flow-kit already runs actionlint」と記録がある一方、「Add actionlint to central CI and run it on every repo's workflows」(P1.65) は未了 backlog のまま。
- **次の一手**: .github の ci.yml に actionlint job を追加し、reusable workflow 化して全 active repo の PR で workflow lint を走らせる（backlog P1.65 の実施）。

#### BP-036 ⚠️ 共通 CI の reusable workflow 集約とバージョン参照
- **規範**: 複数 repo で使う CI は on: workflow_call の reusable workflow として1箇所に集約し、消費側には release tag / SHA で参照させる。@main 参照は許さない。
- **理由**: CI ロジックの編集点を1つにしつつ参照を版で固定しないと、中央の編集ミス1つが全消費 repo の CI を同時に壊す。
- **現状**: ⚠️ 部分的 — dependency-review.yml L6-8 と secrets-scan.yml L8-10 が workflow_call を公開し、コメントで `uses: thinkyou0714/.github/...@<tag|sha>` 参照を指示。しかし IMPROVEMENT-BACKLOG.md（2026-06-07）に「Tag and release the .github reusable workflows so consumers can pin a version」(P1.65) と「Pin reusable-workflow refs to SHA/release tag instead of @main」(P1.1、lab-apps-internal / lab-skills-private が消費側と記録) が未了で残り、pin 先となる versioned release がまだ存在しない。
- **次の一手**: reusable workflow の v1 release/tag を .github に切り、消費 repo（lab-apps-internal, lab-skills-private 等）の uses: を @main から tag または SHA 参照に更新する。

#### BP-037 ⚠️ trigger の branches フィルタに default branch を必ず含める
- **規範**: push / pull_request trigger の branches: には default branch（main）を必ず含める。branch や repo を rename する前に workflow trigger の branches: を点検する。
- **理由**: branches フィルタから main が漏れると required status check が永遠に pending のままになり、PR が merge 不能になる。
- **現状**: ⚠️ 部分的 — ci.yml・dependency-review.yml・secrets-scan.yml はいずれも `branches: [main]` を明示。CONVENTIONS.md ブランチ/マージ節に「必須 status check を持つ repo を rename する前に、workflow trigger の branches: を確認（[main] を含める）」の規約あり。ただし機械的検査は IMPROVEMENT-BACKLOG.md「Lint that required-check workflows include 'main' in branch triggers」(P1.65、2026-06-07) のまま未実装で、他 repo の遵守は未検証。
- **次の一手**: audit-github-governance.ps1 に「required check を担う workflow の branches: が main を含む」検査を追加し、週次監査で全 repo を検証する（backlog P1.65 の実施）。

#### BP-038 ✅ schedule のオフピーク分散と workflow_dispatch 併設
- **規範**: schedule の cron は毎時0分・UTC 正時を避けて分をずらし、必ず workflow_dispatch を併設して手動再実行とデバッグの経路を確保する。
- **理由**: GitHub の schedule は正時に負荷が集中して遅延・スキップが起きやすく、dispatch の無い scheduled workflow は失敗しても次周期まで再実行できない。
- **現状**: ✅ 採用済 — schedule を持つ2 workflow とも準拠: weekly-governance-audit.yml は cron "17 19 * * 0" + workflow_dispatch、stale-branch-gc.yml は cron "37 0 * * 1"（コメントで JST 朝を明示）+ inputs 付き workflow_dispatch（apply / days / prefixes で dry-run と本削除を切替）。両者とも分 offset（17分・37分）で正時を回避。

#### BP-039 ⚠️ pull_request_target 等の危険トリガー回避
- **規範**: pull_request_target や workflow_run で untrusted な PR head を checkout しない。fork 由来コードには secret も write token も渡さず、原則 pull_request trigger で足りる設計にする。
- **理由**: pull_request_target + PR head checkout は fork の任意コードに secret と write 権限を与える RCE 級のサプライチェーン穴になる。
- **現状**: ⚠️ 部分的 — 当 repo の全5 workflow は pull_request / push / schedule / workflow_dispatch / workflow_call のみで、pull_request_target・workflow_run は不使用（repo 全体の grep で該当なし）。ただし account 全体は IMPROVEMENT-BACKLOG.md「Audit Dangerous-Workflow triggers (pull_request_target / workflow_run) across repos」(P2.2、2026-06-07、対象 denken-os / tyl-monorepo / lab-infra / ccmux) が未了で未検証のまま。
- **次の一手**: backlog の Dangerous-Workflow 監査を実施し、audit-github-governance.ps1 に pull_request_target / workflow_run + PR head checkout パターンの検出を追加する。

#### BP-040 ✅ CI-blind repo ゼロ（全 active repo に最低1つの CI）
- **規範**: すべての active repo に最低1つの CI workflow（最低でも lint やデータ整合性 validate）を置き、push しても何も検証されない repo を作らない。
- **理由**: CI が1つも無い repo は壊れたことに気づく仕組み自体が無く、破損の発見が遅れるほど修復コストが跳ね上がる。
- **現状**: ✅ 採用済 — AUDIT-2026-07.md §1 が CI-less を lab-research / skills-registry の2件のみと特定し、R5 で「Minimal validate workflow」追加を記録（2026-07-03）。IMPROVEMENT-BACKLOG.md 2026-07 Done 節に「skills-registry #1 (+new validate CI), lab-research #2 (+new validate CI) … previously had no CI — now gated by a non-fragile JSON/YAML data-integrity check」と記録（2026-07）。repos.json の両 repo の purpose にも「(validate CI); recreated」と明記（2026-07-08 生成）。


## C5. セキュリティ（アカウント・リポ設定）（BP-041〜BP-050）

#### BP-041 ❌ アカウント認証の 2FA / passkey 必須化
- **規範**: GitHub アカウントに 2FA を必ず有効化し、phishing 耐性のある passkey / security key を優先因子にせよ。recovery code はオフラインに保管せよ。
- **理由**: アカウント乗っ取りは全 repo・全 Actions secrets の同時侵害を意味し、solo では検知者も復旧者も自分しかいないため。
- **現状**: ❌ 未採用 — リポ内 grep で 2FA / passkey / MFA / 二要素への言及ゼロ。governance/security-baseline-2026-06-07.md の検証対象も repo 設定（token / actions / secret-scan / dependabot / self-approve）のみで、アカウント認証の検証記録はどのファイルにも存在しない。
- **次の一手**: アカウント設定で 2FA + passkey の有効状態を確認し、governance/ の security baseline に「account auth」節を検証日付つきで追加する（recovery code のオフライン保管も明記）。

#### BP-042 ⚠️ public 全 repo で secret scanning + push protection
- **規範**: すべての public repo で secret scanning と push protection を有効化せよ。「有効にしたはず」で終わらせず、flag を API で実測確認せよ。
- **理由**: public repo は credential leak の主要面であり、push protection は secret が履歴に到達する前に止められる唯一の無料ネイティブ統制のため。
- **現状**: ⚠️ 部分的 — CONVENTIONS.md セキュリティ節に「secret scanning + push protection（public repo）」を規約化。security-baseline-2026-06-07.md に全 public repo で secret scanning enabled と記録（2026-06-07 検証、ただし表に push protection の列なし）。scripts/audit-github-governance.ps1 は publicSecretScanning / publicPushProtection の両方を public repo の pass 条件として週次 assert。一方 IMPROVEMENT-BACKLOG.md の 2026-07 addendum に「Enable secret scanning + push protection on all public repos, verify the flag」（fugu 等の新規 public repo）が open のまま残存。
- **次の一手**: weekly-governance-audit を workflow_dispatch で実行し、2026-07 追加分を含む public 14 repo の secret_scanning / push_protection flag を実測、OFF は即時有効化して日付つき baseline に反映する。

#### BP-043 ⚠️ private repo の代償統制としての gitleaks full-history CI
- **規範**: Free プランで secret scanning が効かない private repo には、gitleaks 等の CI スキャンを代償統制として必須化せよ。checkout は fetch-depth: 0 で全履歴を対象にせよ。
- **理由**: private repo こそ本物の credential を扱いがちで、diff のみのスキャンでは過去 commit に埋まった secret を見逃すため。
- **現状**: ⚠️ 部分的 — .github/workflows/secrets-scan.yml が gitleaks-action@v2 を fetch-depth: 0 で回す reusable workflow（workflow_call 公開、README.md の自動化表に「full history」明記）。scripts/audit-github-governance.ps1 は secrets-scan workflow の存在を全 active repo の pass 条件に含む。一方 IMPROVEMENT-BACKLOG.md（2026-06-07 起票）に「Standardize a gitleaks CI gate via the central reusable workflow」（全 active repo への wiring）と「Audit obsidian-vault history for committed secret-residue」が open のまま。
- **次の一手**: 全 private repo の CI に中央 reusable secrets-scan（thinkyou0714/.github）を tag/SHA pin で接続し、obsidian-vault・旧 archived 系の履歴 secret 残渣監査を完了する。

#### BP-044 ✅ Dependabot security alerts を backstop として全 repo ON
- **規範**: Dependabot の security alerts は全 repo で ON に保て。依存更新 bot を Renovate 等に一本化しても、alerts は独立した脆弱性検知の backstop として維持せよ。
- **理由**: 更新 bot の設定ミスや停止時にも既知 CVE の通知だけは途切れない二重の安全網になるため。
- **現状**: ✅ 採用済 — CONVENTIONS.md セキュリティ節「Dependabot alerts ON」+ 依存自動化節「security alerts + automated-security-fixes は backstop として ON 維持」（Renovate vulnerabilityAlerts と二重の安全網と明記）。security-baseline-2026-06-07.md に全 21 repo で dependabot on と記録（2026-06-07 検証）。scripts/audit-github-governance.ps1 が全 active repo の open Dependabot alerts = 0 を週次 pass 条件として実測（API 取得失敗も fail 扱いで alerts OFF を検知可能）。

#### BP-045 ⚠️ branch protection はプラン制約を文書化した上で public 優先適用
- **規範**: default branch に branch protection / ruleset を適用せよ。プラン制約で適用不能な repo には代償統制（squash-only・force-push 禁止・self-approve OFF 等）を敷き、判断根拠を文書化して「未設定」と「設定不能」を区別せよ。
- **理由**: solo でも force-push や branch 削除の事故は起き、守れない理由を記録しないと監査時に意図的な受容かただの放置か判別できなくなるため。
- **現状**: ⚠️ 部分的 — AUDIT-2026-07.md R3 と IMPROVEMENT-BACKLOG.md Done 節（2026-07 pass）に「public 14 repo へ light protection（linear history / force-push・削除 block / strict status checks / self-merge 可）適用、private 8 repo は 403 Upgrade to GitHub Pro で deferred」と記録（2026-07-03）。security-baseline-2026-06-07.md Notes に Free tier 制約と代償統制（squash-only + delete_branch_on_merge + self-approve OFF）を文書化、CONVENTIONS.md に solo 向け required review 0 / enforce_admins false の判断も明文化。ただし baseline（2026-06-07）の public branch-prot「yes」と AUDIT-2026-07 の「0/27」が矛盾し、drift を週次検知した記録なし。（baseline の矛盾には 2026-07-13 に訂正注記を追記済）
- **次の一手**: branch protection の現況を gh api で再検証して正誤を確定し、weekly-governance-audit の assert を全 active repo に効かせる。GitHub Pro 移行時に private 8 repo へ同一の light protection を適用。

#### BP-046 ⚠️ Actions 権限の最小化（default read + allowed selected）
- **規範**: 全 repo で Actions の default_workflow_permissions を read に固定し、allowed_actions は selected（allowlist）に絞れ。write が必要な workflow / job だけ個別に permissions を宣言せよ。
- **理由**: 侵害された third-party action や script injection が GITHUB_TOKEN 経由で repo を書き換える blast radius を、設定一発で最小化できるため。
- **現状**: ⚠️ 部分的 — CONVENTIONS.md セキュリティ節「default_workflow_permissions = read」。security-baseline-2026-06-07.md に全 21 repo で token=read / actions=selected と記録（2026-06-07 検証）。このリポの全 5 workflow（ci / secrets-scan / dependency-review / weekly-governance-audit / stale-branch-gc）は permissions: contents: read を宣言し、scripts/audit-github-governance.ps1 が workflow レベルの read-only permissions を週次 assert。一方 allowed_actions=selected は CONVENTIONS 未規約化、repo 設定レベルの drift check は IMPROVEMENT-BACKLOG「Add account-wide default_workflow_permissions=read drift check to security audit」として open、2026-07 追加の 7 repo は baseline 未検証。
- **次の一手**: allowed_actions=selected を CONVENTIONS.md セキュリティ節に明文化し、audit script に repo 設定レベル（default_workflow_permissions / allowed_actions）の GET + drift check を追加して現行 28 repo を再検証する。

#### BP-047 ⚠️ Actions からの PR self-approve 無効化
- **規範**: Actions の can_approve_pull_request_reviews は false に固定せよ。solo 運用で required review を 0 にするなら、これが automation の自己承認・自動 merge を防ぐ最後のゲートになる。
- **理由**: 人間レビュー 0 の solo では、bot / workflow が PR を承認できる設定は品質・セキュリティゲートの完全な無効化に直結するため。
- **現状**: ⚠️ 部分的 — CONVENTIONS.md セキュリティ節「Actions PR 自己承認 can_approve_pull_request_reviews = false（許可は allowlist + 正当化）」を規約化。security-baseline-2026-06-07.md に全 21 repo で PR self-approve OFF (secure)・can_approve=true の未 allowlist repo 0 件と記録（2026-06-07 検証）。ただし weekly audit は本設定を assert しておらず（IMPROVEMENT-BACKLOG「Make weekly-governance-audit assert SHA-pinning, secret-scanning, and PR-approve toggle」が open）、2026-07 追加の 7 repo は未検証。
- **次の一手**: can_approve_pull_request_reviews=false の assert を scripts/audit-github-governance.ps1 に追加し、2026-07 追加の 7 repo を含む全 28 repo で再検証して baseline を更新する。

#### BP-048 ❌ automation token は fine-grained PAT + 期限 + ローテーション
- **規範**: automation 用 token には classic PAT でなく fine-grained PAT を使い、対象 repo と権限を最小スコープに絞り、明示的な expiry と定期ローテーションを設定せよ。
- **理由**: 無期限・広域スコープの classic PAT は漏洩一発でアカウント全体を侵害する high-value target になるため。
- **現状**: ❌ 未採用 — .github/workflows/weekly-governance-audit.yml と stale-branch-gc.yml が ORG_GOVERNANCE_AUDIT_TOKEN を使用。IMPROVEMENT-BACKLOG.md「Scope down and set rotation for ORG_GOVERNANCE_AUDIT_TOKEN」（P1.8 / risk:med、2026-06-07 起票）に「classic PAT with org-wide read — a high-value target。fine-grained PAT（metadata+administration:read、監査対象 repo 限定）へ置換し explicit expiry を設定」と記録され open のまま。期限・ローテーション記録もリポ内に存在しない。
- **次の一手**: ORG_GOVERNANCE_AUDIT_TOKEN を監査対象 repo 限定・metadata+administration:read の fine-grained PAT に置換し、明示 expiry を設定、発行日と次回ローテーション日を governance/ に記録する。

#### BP-049 ⚠️ API key ごとの消費先台帳 + rotation runbook
- **規範**: 外部 API key ごとに全消費先（Actions secrets・ホスティング env・ローカル環境）の台帳と rotation 手順を runbook として維持せよ。漏洩・失効時に迷いなく一巡できる状態を保て。
- **理由**: 同一 key が複数 repo・複数ホスティングに散在する solo 環境では、台帳なしのローテーションは必ずどこかを silent に壊すため。
- **現状**: ⚠️ 部分的 — governance/anthropic-key-rotation.md（audit 2026-06-07）が ANTHROPIC_API_KEY の全消費先台帳（Actions secrets 3 repo + Vercel / ホスト runtime 3 面 + ローカル consumer）と rotation 手順・revoke 前検証手順を runbook 化。ただし同 doc に tyl-monorepo / lab-infra の secrets が「observed invalid → rotate」と記録され、IMPROVEMENT-BACKLOG.md の「Audit and rotate ANTHROPIC_API_KEY across all consumers, standardize one secret name」も open のまま（Done 節に記載なし）。Slack / Stripe 等の他 key 族の台帳は未整備（backlog に個別項目のみ）。
- **次の一手**: runbook どおり ANTHROPIC_API_KEY のローテーションを一巡実行して完了日を doc に追記し、Slack / Stripe / Supabase 等の他 key 族にも同形式の消費先台帳を拡張する。

#### BP-050 ⚠️ セキュリティ設定は assert でなく verify（日付つき baseline）
- **規範**: セキュリティ設定は規約に書くだけで満足せず、実際の API 値を定期的に実測して日付つき baseline として commit せよ。「〜のはず（assert）」と「実測済（verify）」を常に区別せよ。
- **理由**: 設定は repo 追加・rename・UI 操作で静かに drift するため、実測記録がないと規約と現実の乖離を誰も検知できない。
- **現状**: ⚠️ 部分的 — governance/security-baseline-2026-06-07.md が「CONVENTIONS.md security section was asserted but never verified before this pass」と明記し、gh_repo_security_audit 等の実測結果を日付つきで commit（2026-06-07、21 repo）。AUDIT-2026-07.md も 27 repo の日付つき採点を記録（2026-07-03）し、weekly-governance-audit.yml + scripts/audit-github-governance.ps1 が週次で再実測。ただし baseline は 21 repo 時点のままで repos.json の active_count=28 に未追随、branch protection の記載は AUDIT-2026-07 の「0/27」と矛盾。AUDIT-2026-07 自身が「re-run the audit … to re-baseline」と指示するが更新版 baseline は未 commit。。branch protection の記載矛盾は 2026-07-13 に security-baseline へ訂正注記済
- **次の一手**: 2026-07 の PR 群反映後にアカウント監査を再実行し、28 repo 対応の日付つき baseline を commit して branch protection の記載矛盾を解消する（repos.json 変更時の再 baseline をルール化）。


## C6. 依存管理・サプライチェーン（BP-051〜BP-060）

#### BP-051 ✅ Dependency bot は1本に統一（二重 bot 禁止）
- **規範**: 依存更新 bot は Renovate なら Renovate と1本に統一し、Dependabot version-update（dependabot.yml）は併用しない。二重 bot は同一依存に二重 PR を生み CI を汚染するため、security alerts のみ backstop として残す。
- **理由**: 二重 bot は同一依存への競合 PR（pull_request_exists_for_latest_version 等）で CI とレビュー帯域を浪費し、依存ポリシーの SSOT を崩すため。
- **現状**: ✅ 採用済 — CONVENTIONS.md「依存自動化（Renovate 一本・SSOT）」節が Renovate-only・dependabot.yml 禁止・Dependabot security alerts の backstop 維持を規定（2026-06-07 refresh）。この repo は renovate.json あり / dependabot.yml なし。scripts/audit-github-governance.ps1 の判定は 2026-07-13 に「renovate.json が存在し、かつ dependabot.yml が存在しない」の Renovate-only assert へ修正済（従来の OR 判定は CONVENTIONS の「renovate.json を assert すること」と不整合だった）。

#### BP-052 ✅ 中央共有 preset を依存ポリシーの単一編集点にする
- **規範**: Renovate 設定は owner/.github の中央 preset（config:recommended ベース）に集約し、各 repo の renovate.json は extends ["local><owner>/.github"] の1行継承にする。repo 固有の逸脱は extends への追記として明示する。
- **理由**: N repo × 個別設定は必ずドリフトするため、依存ポリシーの編集点を1箇所にして全 repo へ一括反映できるようにする。
- **現状**: ✅ 採用済 — default.json が中央 preset（extends: config:recommended, helpers:pinGitHubActionDigests, :semanticCommits, :timezone(Asia/Tokyo), schedule:weekly）。この repo の renovate.json は {"extends": ["local>thinkyou0714/.github"]} の1行継承。CONVENTIONS.md 依存自動化節が「中央 preset = default.json（依存ポリシーの唯一の編集点）」「repo 固有 override は extends 配列に追記（github-flow-kit の例）」と規定（2026-06-07）。

#### BP-053 ✅ minimumReleaseAge で新規リリースにクールダウンを設ける
- **規範**: 公開直後のパッケージ版を即取り込まず、minimumReleaseAge（例: 3 days）で数日のクールダウンを置く。マルウェア版はこの窓の間に検知・unpublish されることが多い。
- **理由**: アカウント乗っ取り経由の悪性リリースは公開後数時間〜数日で検知・撤回されるため、遅延取り込みが最も安価なサプライチェーン防御になる。
- **現状**: ✅ 採用済 — default.json に "minimumReleaseAge": "3 days"（commit 3db4651「chore(renovate): add minimumReleaseAge (3 days) supply-chain delay」）。schedule:weekly + :timezone(Asia/Tokyo) で取り込み頻度自体も抑制。中央 preset 経由で全 repo に適用される。

#### BP-054 ✅ automerge は低リスク更新に限定し、critical 依存は禁止する
- **規範**: 無人 automerge は patch / pin / digest と非 major の devDependencies に限定する。決済（Stripe 等）・データ層（DB クライアント等）・中核 framework（Next.js/React 等）は更新種別を問わず automerge を明示的に禁止し、専用ラベルで手動レビューに回す。
- **理由**: 無差別 automerge は破壊的変更や悪性版を無審査で本番に入れ、特に課金・データ破壊に直結する依存では patch でも事業インシデントになり得るため。
- **現状**: ✅ 採用済 — default.json packageRules に allow 側：「Auto-merge patch + pin + digest updates」「Auto-merge non-major devDependencies」「Auto-merge minor updates for type/lint tooling（@types/*, eslint, @typescript-eslint/*）」。deny 側：「Never auto-merge Next.js framework」（label: framework-major）「Never auto-merge Stripe (payment-critical)」（stripe-critical）「Never auto-merge Supabase (data-critical)」（supabase-critical）。CONVENTIONS.md も「安全 automerge(patch + 非major dev-deps)」「Next.js・React・Stripe・Supabase は automerge 禁止」と明文化（2026-06-07）。

#### BP-055 ✅ grouping と rate limit で依存 PR のノイズを制御する
- **規範**: 関連依存は groupName で1 PR にまとめ、prConcurrentLimit / prHourlyLimit と週次 schedule で PR 流量に上限を設ける。依存 PR がレビュー帯域を食い潰す状態を作らない。
- **理由**: 1人のレビュー帯域は有限であり、依存 PR の洪水は「読まずにマージする」習慣を生んでサプライチェーン防御を実質無効化するため。
- **現状**: ✅ 採用済 — default.json に prConcurrentLimit: 5、prHourlyLimit: 2、schedule:weekly、rebaseWhen: behind-base-branch。grouping は「github-actions」（全 Actions 更新を1 PR）「Next.js framework」「Supabase」の3グループ。CONVENTIONS.md 依存自動化節も grouping / JST 週次を preset の構成要素として明記（2026-06-07）。

#### BP-056 ⚠️ lockfile を必ずコミットし lockFileMaintenance で定期更新する
- **規範**: 依存を持つ repo は lockfile（package-lock.json 等）を必ずコミットし、CI とエージェント環境では npm ci 等の lockfile 厳守 install を使う。推移的依存の鮮度は lockFileMaintenance で定期的に一括更新する。
- **理由**: lockfile なしの install は実行のたびに異なる依存木を解決し、再現性とサプライチェーン検証（何が入ったか）の両方を失うため。
- **現状**: ⚠️ 部分的 — default.json に lockFileMaintenance（enabled, 毎月1日 before 9am, automerge）あり。一方で lockfile コミット必須の明文規約が CONVENTIONS.md に無く、docs/claude-code-web-readiness.md の bootstrap.sh は package-lock.json 欠如時に npm install へ fallback する設計（lockfile 無し repo の存在を許容）。audit-github-governance.ps1 にも lockfile 存在の assert なし。
- **次の一手**: CONVENTIONS.md に「依存を持つ repo は lockfile コミット必須」を明文化し、weekly-governance-audit（audit-github-governance.ps1）に package.json があるのに lockfile が無い repo を検出する assert を追加する。

#### BP-057 ⚠️ 依存は最小主義で選ぶ（zero-dependency 志向）
- **規範**: 依存を足す前に「標準ライブラリや自作数十行で済まないか」を問い、特に配布物（CLI・ライブラリ）は zero-dependency を志向する。依存1つが持ち込む推移的依存と更新・監査コストまで含めて採否を判断する。
- **理由**: 依存が少ないほどサプライチェーン攻撃面・更新 PR・breaking change 対応が線形に減り、solo の保守可能性が上がる。
- **現状**: ⚠️ 部分的 — 実践例は flagship に複数: repos.json の fugu「Zero-dependency TypeScript client + CLI」、agmsg「Bash+SQLite, no daemon」（2026-07-08）。ただし CONVENTIONS.md に依存追加の判断基準（最小主義）の明文規定はなく、product 系（Next.js/Supabase/Stripe スタック）との使い分け基準も未文書化。
- **次の一手**: CONVENTIONS.md 依存自動化節に「依存追加は最小主義（採用前に stdlib/自作で済むか検討、配布物は zero-dep 志向）」を明文化する。

#### BP-058 ✅ vulnerabilityAlerts と dependency review で脆弱性経路を二重化する
- **規範**: Renovate の vulnerabilityAlerts で脆弱性起点の更新 PR を schedule 外で優先起票させ、PR には dependency-review-action（fail-on-severity 設定）を掛けて既知脆弱性依存の混入を CI で遮断する。プラットフォーム側の security alerts も backstop として有効に保つ。
- **理由**: 週次 schedule 待ちでは公開済み脆弱性の露出窓が長く、検知（alert）と流入防止（review gate）は別のリスクを塞ぐため両方必要。
- **現状**: ✅ 採用済 — default.json に vulnerabilityAlerts { enabled: true, labels: [security, vulnerability] }。.github/workflows/dependency-review.yml は dependency-review-action を fail-on-severity: high で実行し workflow_call で他 repo からも reusable。CONVENTIONS.md は「Dependabot の security alerts + automated-security-fixes は backstop として ON 維持（Renovate vulnerabilityAlerts と二重の安全網）」と規定。security-baseline-2026-06-07.md は全 21 active repo で Dependabot alerts on を実測記録（2026-06-07）。。dependency-review は personal アカウントでは public repo 限定（private は GHAS 不可で動作しない）である旨を 2026-07-13 に CONVENTIONS.md と監査 pass 条件へ反映済

#### BP-059 ✅ 無人 install では lifecycle scripts を実行しない（--ignore-scripts）
- **規範**: CI やクラウドエージェントなど無人環境の依存 install は --ignore-scripts（npm）等で postinstall / prepare の実行を止める。lifecycle scripts が必要な repo だけ例外を明示して外す。
- **理由**: install-time scripts は悪性パッケージの主要な実行ベクタであり、無人セッションでは実行を観察・中断する人間がいないため既定で遮断すべき。
- **現状**: ✅ 採用済 — docs/claude-code-web-readiness.md の bootstrap.sh テンプレが npm ci / npm install に --ignore-scripts を付与し「dependency lifecycle scripts を無人実行させない supply-chain hardening。必要な repo のみ外す」と明記。IMPROVEMENT-BACKLOG.md の 2026-07 Done 節に、このテンプレを 22 repo へ PR 適用済（CI green、除外3件は理由明記）と記録されている（2026-07）。

#### BP-060 ❌ ランタイムを .nvmrc / engines でピンする
- **規範**: Node 等のランタイムは .nvmrc と package.json の engines でバージョンをピンし、ローカル・CI・クラウドエージェントが同一ランタイムでビルドする状態を保証する。
- **理由**: 実行環境が複数ランタイム版を持つ場合（例: クラウドサンドボックスの Node 20/21/22）、ピンが無いと環境ごとに異なる版で解決され再現性が壊れるため。
- **現状**: ❌ 未採用 — IMPROVEMENT-BACKLOG.md の Web-readiness 節に「Add .nvmrc / pin engines.node on Node repos（fugu, ccmux, denken-os, lab-lms, tyl-monorepo）· P2.2」が未了のまま残り、2026-07 Done 節に含まれない。CONVENTIONS.md にもランタイムピンの規定なし。docs/claude-code-web-readiness.md 自体が「Cloud has Node 20/21/22; pin the one this repo builds on」と非決定性を指摘している。
- **次の一手**: Node を使う repo（fugu, ccmux, denken-os, lab-lms, tyl-monorepo）へ .nvmrc + engines.node を追加する PR を出し、CONVENTIONS.md の新規 repo 要件（first push 前チェック）にランタイムピンを追記する。


## C7. ドキュメント・コミュニティヘルス（BP-061〜BP-070）

#### BP-061 ⚠️ README を repo の玄関として設計する
- **規範**: README は repo の玄関として what（何か）/ why（なぜ作った）/ quickstart（最短の使い方）を最初の 1 画面で答える構成にする。CI・license・release の badge 行を添え、鮮度と信頼性を一目で伝える。
- **理由**: 訪問者と将来の自分は README だけで「使うか・閉じるか」を数十秒で判断するため、玄関の質が repo の価値伝達を決める。
- **現状**: ⚠️ 部分的 — この repo の README.md は 3 役割（default community health fallback / ガバナンス SSOT / 自動化）とファイル表で what/why を明示する一方、badge 行なし。アカウント全体では AUDIT-2026-07.md §1 が score lever に「README depth on 4 stubs」を挙げ（2026-07-03）、IMPROVEMENT-BACKLOG.md に「Add CI/license/release badge rows to bare flagship READMEs」（codex-toolkit, codex-hub, denken-os）「Expand the 4 stub READMEs」（lab-public, thinkyou0714, lab-skills-private, obsidian-vault）「Add a Quick Start / usage block to policy-oriented READMEs」が未消化として記録されている（2026-06-07 / 2026-07 追補）。
- **次の一手**: backlog の 3 件を実行する — 4 つの stub README に purpose + quickstart を追記し、flagship OSS の README に CI/license/release badge 行を追加、policy 系 README に usage 節を足す。

#### BP-062 ⚠️ public repo は LICENSE 必須・ポリシーを明文化する
- **規範**: public repo には必ず LICENSE ファイルを置き、アカウントとしての選定ポリシー（software=MIT / 文章・記事=CC-BY-4.0 / 混在=dual-license 等）を 1 箇所に明文化する。private repo も UNLICENSED / proprietary を明示し「未指定」状態を残さない。
- **理由**: LICENSE のない public コードは法的には all rights reserved となり、利用も貢献もできない死蔵物になる。
- **現状**: ⚠️ 部分的 — LICENSE（MIT, この repo）が存在し、CONVENTIONS.md ライセンス節が「software → MIT / 文章・記事 → CC-BY-4.0 / 混在 → dual-license（denken-os が reference）」とポリシーを明文化。AUDIT-2026-07.md R4 に「1 public repo（engineer-tenshoku-navi）lacks a LICENSE → MIT LICENSE added」と是正記録あり（2026-07-03）。一方 CONVENTIONS.md は「private repo は license 任意」のままで、IMPROVEMENT-BACKLOG.md の「Add a proprietary/`UNLICENSED` notice to private product repos」（tyl-monorepo, lab-lms, lab-apps-internal, lab-inbox-bot, P1.1）が未消化（2026-07 追補）。
- **次の一手**: private product 4 repo に UNLICENSED 明示（package.json の license field + README 冒頭注記）を追加し、CONVENTIONS.md ライセンス節の「private は任意」を「UNLICENSED 明示」に改定する。

#### BP-063 ✅ CONTRIBUTING.md で貢献手順を契約化する
- **規範**: CONTRIBUTING.md で貢献の入口（既存 issue 確認 → 大きな変更は Discussion → fork/branch/PR）、commit 規約、code style を明文化する。solo でも未来の contributor と自分自身への契約として書く。
- **理由**: 貢献手順が暗黙だと PR の粒度と品質がばらつき、レビューコストが solo maintainer の可処分時間を直撃する。
- **現状**: ✅ 採用済 — CONTRIBUTING.md（全 repo 共通 fallback と冒頭に明記、repo 固有版が優先とも記載）に Quick start 5 手順、PR ガイドライン（1 PR = 1 concern / Conventional Commits タイトル / Description には Why / test plan 必須 / draft PR 可）、commit type 一覧表（feat〜ci の 9 種）、言語別 code style（ESLint+Prettier / ruff / shellcheck）、CODE_OF_CONDUCT へのリンクを記載。

#### BP-064 ✅ CODE_OF_CONDUCT と private 通報経路を用意する
- **規範**: CODE_OF_CONDUCT.md を置き、標準文書（Contributor Covenant 等）の採用宣言と private な通報経路・enforcement 権限を明示する。自作の規範文よりも広く通用する標準を参照する。
- **理由**: 行動規範と通報先の事前明示だけが、トラブルを公開の場から私的経路へ逃がしエスカレーションを防ぐ仕組みになる。
- **現状**: ✅ 採用済 — CODE_OF_CONDUCT.md が Contributor Covenant v2.1 準拠を宣言し、Reporting 節で「public issue に詳細を書かない」こと、X DM（@thinkyou0714）または詳細を含めない Discussion 経由で confidential channel を要求する private 通報経路、Enforcement 節で maintainer の削除権限を明記。CONTRIBUTING.md からもリンクされ、README.md の fallback 表に掲載。

#### BP-065 ✅ SECURITY.md に private 報告経路と応答 SLA を明記する
- **規範**: SECURITY.md で「public issue で報告しない」ことを明確に禁じ、GitHub の private vulnerability reporting への具体的手順と応答 SLA（受領確認・状況更新・修正リリースの目安日数）を明記する。
- **理由**: 応答期限の明示がないと報告者は無反応と判断して full disclosure に走りやすく、脆弱性が公開の場に露出する。
- **現状**: ✅ 採用済 — SECURITY.md に「Do not open a public issue」、Security タブからの private vulnerability reporting 3 手順、報告に含める項目リスト、SLA（acknowledge 48 hours / status update 7 days / fix 30 days）、coordinated disclosure と報告者クレジット方針を明記。fallback policy であること・repo 固有版が優先することも Scope 節に記載。.github/ISSUE_TEMPLATE/config.yml の contact link も private reporting へ誘導。

#### BP-066 ✅ SUPPORT.md でサポート導線を routing する
- **規範**: SUPPORT.md で問い合わせの routing order（docs 確認 → 既存 issue/discussion 検索 → Discussions → issue template）を段階として定義し、質問が bug tracker へ流入するのを防ぐ。商用サポートの有無も明記する。
- **理由**: routing が定義されていないと質問が issue に混入し、solo maintainer の triage コストが際限なく膨らむ。
- **現状**: ✅ 採用済 — SUPPORT.md に「Routing order」節（1. README/docs → 2. 既存 issue/discussion 検索 → 3. Discussions → 4. issue template の 4 段）、bug/feature/security の経路分離、「Commercial support — Not currently offered」の明記、外部窓口（X / Zenn / Website）を記載。.github/ISSUE_TEMPLATE/config.yml は blank_issues_enabled: false + contact_links で Discussions へ誘導し routing を機械的に補強。

#### BP-067 ⚠️ FUNDING.yml は機能するリンクだけ公開する
- **規範**: 継続開発する OSS には FUNDING.yml で支援経路を提示する。ただし未承認・未開設の channel を載せず、実際に遷移して支援できるリンクだけを有効化する。
- **理由**: sponsor button は個人 OSS のほぼ唯一の受動的支援経路であり、押しても機能しないリンクはかえって信頼を毀損する。
- **現状**: ⚠️ 部分的 — FUNDING.yml が全 repo fallback として存在し `github: [thinkyou0714]` を有効化。ただしファイル内コメント自身が「申請承認後に有効化される。承認前は sponsor button が出ても profile に飛ばない」と GitHub Sponsors の未確定状態を注記し、Ko-fi / Buy Me a Coffee / custom URLs（note, Gumroad, LINE）は全てコメントアウトのまま = 現時点で確実に機能する支援経路が 1 つも確認されていない。
- **次の一手**: GitHub Sponsors の承認状態を確認し、未承認なら即時有効化できる channel（Ko-fi 等）を 1 つ開設してコメント解除し、sponsor button を実際に遷移可能なリンクにする。

#### BP-068 ❌ 大規模 repo には REPO_TOUR / ナビゲーション文書を置く
- **規範**: ファイル数の多い monorepo・大規模 repo には、注釈つきディレクトリツリーと「どこに何があるか」を示す REPO_TOUR（または AGENTS.md のナビ節）を置き、構造変更時に追従させる。
- **理由**: 1000 ファイル超の repo は README だけでは航行不能で、人間と AI エージェント双方の探索コストが変更のたびに膨らむ。
- **現状**: ❌ 未採用 — IMPROVEMENT-BACKLOG.md「Generate REPO_TOUR.md for the large monorepos」（P1.47、2026-06-07）: tyl-monorepo（1669 files）/ lab-infra（2130 files）/ lab-apps-internal（191 files, 5 packages）に REPO_TOUR なし、参照があるのは codex-hub のみ。2026-07 追補「Publish AGENTS.md/REPO_TOUR.md for the big monorepos」（P1.47）も open。
- **次の一手**: tyl-monorepo / lab-infra / lab-apps-internal に注釈つきツリーの REPO_TOUR.md（AGENTS.md から参照）を生成して commit する（backlog P1.47 消化）。

#### BP-069 ❌ CHANGELOG を Keep a Changelog 形式で維持する
- **規範**: 利用者のいる repo には Keep a Changelog 形式の CHANGELOG.md を置き、release ごとに Added / Changed / Fixed / Removed を人間向けの言葉で記録する。git log や commit 一覧を changelog の代用にしない。
- **理由**: 利用者は commit 履歴ではなく「自分に影響する変更は何か・壊れるか」を知りたいのであり、それに答える文書は changelog だけだから。
- **現状**: ❌ 未採用 — この repo に CHANGELOG.md なし。IMPROVEMENT-BACKLOG.md「Establish CHANGELOG + Releases discipline for flagship OSS」（P1.1）が「github-flow-kit has a release badge but ccmux, codex-toolkit, denken-os, claude-lab-skills lack visible CHANGELOG/Releases」と記録し（2026-06-07）、Done 節（2026-06-07 pass）にも消化記録なし。関連の「Build a reusable release-notes workflow」（P1.1）も未消化のまま。
- **次の一手**: flagship OSS 4 repo（ccmux, codex-toolkit, denken-os, claude-lab-skills）に Keep a Changelog 形式の CHANGELOG.md と baseline GitHub Release を追加し、backlog の tag-triggered release-notes reusable workflow で以後の entry を自動 draft 化する。

#### BP-070 ⚠️ 文書の相互参照は同一 PR で着地させ、リンク切れを main に入れない
- **規範**: 文書から資産（ファイル・節・URL）へリンクを張るときは、リンク先を同一 PR で作成・更新して着地させる。governance 文書が参照するファイルは CI で存在を assert し、リンクだけ先行した「作成予定」状態を main に残さない。
- **理由**: リンク切れは読者の導線と自動化（CI の前提）を同時に壊し、「どの文書が本当か」への信頼を毀損する。
- **現状**: ⚠️ 部分的 — ci.yml「Verify governance files」が README/CONVENTIONS から参照される BEST-PRACTICES.md・repos.json 等の存在を assert（本 PR で BEST-PRACTICES.md をリンクと同時に追加し充足）。.github/ISSUE_TEMPLATE/config.yml・CONTRIBUTING.md の空振りリンク（プロフィール URL 行き）も 2026-07-13 に実在の導線（SUPPORT.md / SECURITY.md）へ修正済。ただし URL リンク切れの機械検査（lychee 等の link checker）は未導入。
- **次の一手**: markdown link checker（lychee 等）を ci.yml に追加し、内部相対リンクと主要外部 URL の生存を PR 時に検査する。


## C8. リリース・バージョニング（BP-071〜BP-080）

#### BP-071 ❌ SemVer + annotated tag でリリース点を刻む
- **規範**: リリース点には SemVer（MAJOR.MINOR.PATCH）で番号を付け、`vX.Y.Z` の annotated tag として刻む。lightweight tag ではなく annotated tag を使い、tagger・日時・メッセージを履歴に残す。
- **理由**: バージョン番号と tag が変更の互換性影響を機械可読に伝え、任意時点の再現・rollback・比較の不変な基準点になるため。
- **現状**: ❌ 未採用 — この repo (.github) は `git tag -l` が空で tag ゼロ。CONVENTIONS.md の節構成は命名 / ブランチ・マージ / メタデータ / ライセンス / セキュリティ / 依存自動化のみで versioning・tag 規約が存在しない。IMPROVEMENT-BACKLOG.md（2026-06-07）に「Tag and release the .github reusable workflows so consumers can pin a version」（P1.65 quick win）が未消化のまま記録されている。
- **次の一手**: CONVENTIONS.md に versioning 節（SemVer + annotated tag `vX.Y.Z`）を追加し、まず .github 自身に v1.0.0 の annotated tag を切る。

#### BP-072 ⚠️ GitHub Releases と release notes を公開する
- **規範**: tag を push するだけで終えず GitHub Releases として公開し、変更点・破壊的変更・upgrade 手順を release notes に書く。
- **理由**: Releases は repo の玄関に時系列で表示され、watch 通知・RSS・API から消費できる唯一の公式なリリース面だから。
- **現状**: ⚠️ 部分的 — IMPROVEMENT-BACKLOG.md（2026-06-07）に「github-flow-kit has a release badge but ccmux, codex-toolkit, denken-os, claude-lab-skills lack visible CHANGELOG/Releases」と記録。一方 SECURITY.md は「The latest release of each project receives security updates」「credit reporters in release notes」と releases の存在を前提に書いており、実態と不整合。
- **次の一手**: backlog 項目「Establish CHANGELOG + Releases discipline for flagship OSS」を実行し、ccmux / codex-toolkit / denken-os / claude-lab-skills に baseline の GitHub Release を切る。

#### BP-073 ⚠️ release notes 自動生成 + draft release 運用
- **規範**: release notes の下書きは自動生成（GitHub の generate-release-notes や tag-trigger workflow）し、draft release で内容を確認してから publish する。
- **理由**: solo では手書き notes が真っ先に省略される作業であり、自動化しなければリリース記録そのものが途絶えるため。
- **現状**: ⚠️ 部分的 — repos.json（2026-07-08 生成）の github-flow-kit purpose に release-notes skill が含まれ、governance/anthropic-key-rotation.md も用途を「Claude-powered CI (review/release)」と記録。ただし IMPROVEMENT-BACKLOG.md（2026-06-07）は「The release-notes/codex-changelog skills run interactively」とし、tag-trigger で draft Release + CHANGELOG を生成する reusable workflow 化は未消化。基盤となる Conventional Commits は CONTRIBUTING.md と default.json の `:semanticCommits` で整備済み。
- **次の一手**: backlog どおり tag-trigger の reusable release-notes workflow を .github に実装し、draft Release 自動生成 → 内容確認 → publish の運用に切り替える。

#### BP-074 ❌ green CI に紐づく release gate
- **規範**: release は green CI を通過した commit からのみ切る。tag / release workflow に required status checks の合格確認を組み込み、CI を迂回した成果物を出さない。
- **理由**: リリース成果物が検証済み commit に紐づく保証がなければ、壊れた版の配布も supply-chain 上の疑義も防げないため。
- **現状**: ❌ 未採用 — IMPROVEMENT-BACKLOG.md（2026-06-07）に「Add a release gate that blocks tags failing required status checks」（P1.1）が未消化で残り、同項は release artifact を green CI に「provably tied」にする必要性＝現状の欠如を記録。.github/workflows/ci.yml の trigger は push / pull_request の branches: [main] のみで、tag・release イベントを扱う workflow がアカウントの governance SSOT に存在しない。
- **次の一手**: tag-trigger の release workflow に、tagged commit 上で CodeQL / ci / Build の合格を確認してから Release を publish する gate step を追加する（まず github-flow-kit / ccmux / codex-toolkit）。

#### BP-075 ❌ 共有 preset・reusable workflow 自体の versioned release
- **規範**: 他 repo から消費される reusable workflow・共有 preset は、それ自体を versioned release（v1 等の tag）として出す。consumer には @main ではなく tag か SHA で pin させる。
- **理由**: 共有部品への in-flight 編集が全 consumer を同時に壊す事故は、immutable ref への pin でしか防げないため。
- **現状**: ❌ 未採用 — dependency-review.yml と secrets-scan.yml のコメントは consumer に `uses: thinkyou0714/.github/.github/workflows/…@<tag|sha>` での参照を指示するが、`git tag -l` は空で pin 先の tag が存在しない。IMPROVEMENT-BACKLOG.md（2026-06-07）の「Pin reusable-workflow refs to SHA/release tag instead of @main」は lab-apps-internal / lab-skills-private が @main で消費中と記録。
- **次の一手**: .github に v1 の annotated tag + Release を切り、consumer repo の `uses:` を @main から @v1（または SHA）へ一括更新する。

#### BP-076 ⚠️ 成熟度（pre-alpha / beta / stable）の明示
- **規範**: プロジェクトの成熟度（pre-alpha / beta / stable）を README と repo description に明示し、実態が変わったら更新する。
- **理由**: 利用者と将来の自分が API 安定性と自己責任の度合いを誤解しないための、最も安価なシグナルだから。
- **現状**: ⚠️ 部分的 — denken-os は repos.json（2026-07-08 生成）と ARCHITECTURE.md の description で「(pre-alpha)」を明示。一方 fugu・agmsg・ccmux 等の他 flagship-oss に成熟度表示はなく、CONVENTIONS.md メタデータ節（description・topics≥3・homepage・social preview）にも成熟度の規定がない。
- **次の一手**: CONVENTIONS.md メタデータ節に成熟度表示規則（pre-alpha / beta / stable を description か README badge で明示）を追加し、flagship-oss 8 repo に展開する。

#### BP-077 ⚠️ breaking change の明示
- **規範**: breaking change は commit（Conventional Commits の `!` / `BREAKING CHANGE:` footer）と release notes の専用節の両方で明示し、SemVer の major bump に反映する。
- **理由**: 破壊的変更の告知漏れは利用者の環境を黙って壊す、信頼を最も損なう失敗だから。
- **現状**: ⚠️ 部分的 — CONTRIBUTING.md は Conventional Commits を全 repo 共通規約とし type 表と footer 例（Closes #123）を定めるが、`!` / `BREAKING CHANGE:` footer への言及がない。告知先となる release notes 面も未整備（Releases discipline 自体が IMPROVEMENT-BACKLOG.md 2026-06-07 の未消化項目）。
- **次の一手**: CONTRIBUTING.md の Commit message 節に `feat!:` / `BREAKING CHANGE:` footer の規定を追記し、release notes テンプレートに Breaking Changes 節を必須化する。

#### BP-078 ❌ CHANGELOG とリリースの一致
- **規範**: Keep a Changelog 形式の CHANGELOG.md を repo 内に維持し、内容を GitHub Releases と一致させる。片方だけの更新を許さない。
- **理由**: repo 内で完結する変更履歴は GitHub の外（clone・パッケージ tarball）でも読め、Releases との不一致は記録全体の信頼を毀損するため。
- **現状**: ❌ 未採用 — IMPROVEMENT-BACKLOG.md（2026-06-07）が「Add a Keep-a-Changelog CHANGELOG.md and cut a baseline GitHub Release」を未消化項目として記録し、ccmux / codex-toolkit / denken-os / claude-lab-skills に visible CHANGELOG なしと明記。この .github repo 自身のルートにも CHANGELOG.md が存在しない（ファイル一覧で確認）。
- **次の一手**: flagship OSS と .github に Keep a Changelog 形式の CHANGELOG.md を追加し、release workflow が Releases と同一内容を書き込むようにする。

#### BP-079 ⚠️ 小さく高頻度に出す
- **規範**: 変更を貯め込まず、小さな単位で高頻度にリリースする。solo では大きな bundle release より patch / minor の連発を選ぶ。
- **理由**: 小さいリリースは原因切り分けと rollback を容易にし、solo の限られたデバッグ時間を守るため。
- **現状**: ⚠️ 部分的 — 変更単位の小ささは制度化済み: CONTRIBUTING.md「1 PR = 1 concern」、CONVENTIONS.md の squash-only。IMPROVEMENT-BACKLOG.md の 2026-07 Done 節も 24 PR を repo 単位に分割して出荷したと記録。ただし versioned release としては出ておらず、denken-os は「pre-alpha auto-deploys main」（IMPROVEMENT-BACKLOG.md 2026-06-07）とリリース単位を持たない。
- **次の一手**: main への継続的 merge はそのままに、機能のまとまりごとに patch / minor の tag + Release を切る cadence（feature 完了時 or 月次）を flagship OSS に導入する。

#### BP-080 ❌ publish 時の provenance と 2FA
- **規範**: npm 等のレジストリへ publish する際はアカウント 2FA（または trusted publishing / OIDC）を必須にし、`--provenance` で成果物と source commit・build workflow の対応を証明する。
- **理由**: レジストリアカウントの乗っ取りと改ざんパッケージの配布が、個人メンテナを狙う最多の supply-chain 攻撃経路だから。
- **現状**: ❌ 未採用 — repo 全文 grep で npm publish・provenance・trusted publishing・2FA への言及ゼロ。CONVENTIONS.md セキュリティ節は repo 設定（default_workflow_permissions・secret scanning 等）のみで registry publish の規定がない。repos.json（2026-07-08 生成）の fugu は「Zero-dependency TypeScript client + CLI」で npm 配布が想定される形態。
- **次の一手**: CONVENTIONS.md に publish 規定（レジストリ 2FA 必須、npm は trusted publishing / OIDC + `--provenance`）を追記し、fugu を最初の適用対象にする。


## C9. AI エージェント協働開発（BP-081〜BP-090）

#### BP-081 ✅ CLAUDE.md / AGENTS.md はコード実態に正確に保つ
- **規範**: CLAUDE.md / AGENTS.md には実在するパス・コマンド・不変条件のみを書き、捏造と安全機構の過大表現を禁止する。コードが変わったらエージェント向けドキュメントも同じ PR で追従させる。
- **理由**: エージェントは書かれた内容を事実として行動するため、不正確な記述は誤ったコマンド実行や誤った安全前提を直接誘発する。
- **現状**: ✅ 採用済 — governance/claude-code-convention.md（2026-06 制定）が「コード実態に正確（捏造禁止。実在するパス/コマンド/不変条件のみ）」「安全層を記述する際は過大表現しない」を明文化。同 doc 採用状況節に ccmux / fugu / engineer-tenshoku-navi / denken-os が準拠と記録（2026-06）。IMPROVEMENT-BACKLOG.md 2026-07 Done 節に root AGENTS.md を含む web-readiness template を 22 repo へ PR 適用（CI green）と記録（2026-07）。

#### BP-082 ⚠️ permissions は read-only allow + 破壊的 deny、bypass の非強制を明記
- **規範**: .claude/settings.json の permissions.allow は read-only / 安全な操作（実在する package scripts + 読み取り専用 git）のみに限定し、deny に force-push・hard reset・force-clean・--no-verify 等の破壊的操作を明示する。あわせて bypass mode（--dangerously-skip-permissions）では allow/deny が強制されず hook のみが実効防御であることを必ず文書に明記する。
- **理由**: permissions は defense-in-depth の一層にすぎず、その限界を偽らず設計・記述しないと誤った安心感の下で破壊的操作が素通りする。
- **現状**: ⚠️ 部分的 — governance/claude-code-convention.md が allow=read-only 系のみ + deny 参考スケルトン（`git push --force*` / `git reset --hard*` / `git clean -f*` / `*--no-verify*`）と「bypass 下では permissions.allow/deny が強制されず hook のみが実効防御」の明記義務を規定。ただし同 doc 採用状況節（2026-06）で準拠は 4 repo のみ（repos.json の active は 28）。この .github repo 自体にも .claude/settings.json は存在しない。
- **次の一手**: convention のスケルトンを残り active repo へ rollout し、weekly-governance-audit に .claude/settings.json の conformance check（allow の read-only 性・deny の存在）を追加する。

#### BP-083 ⚠️ SessionStart bootstrap は POSIX・冪等・--ignore-scripts
- **規範**: cloud session（Claude Code on the web 等）向けに commit する SessionStart bootstrap は POSIX sh・冪等（node_modules 存在ガード等）・`npm ci --ignore-scripts` で書く。powershell・`C:\` パス等の OS 固有依存を committed hook に含めない。
- **理由**: cloud session は ephemeral な Linux container で毎回 hook を実行するため、非 POSIX は即死、非冪等は環境破壊、lifecycle script の unattended 実行は supply-chain リスクになる。
- **現状**: ⚠️ 部分的 — docs/claude-code-web-readiness.md §1 が POSIX bootstrap.sh テンプレ（`[ ! -d node_modules ]` ガードで冪等、`npm ci --no-audit --no-fund --ignore-scripts`、「No powershell, no C:\ paths」）を SSOT として規定。IMPROVEMENT-BACKLOG.md 2026-07 Done 節に 22 repo へ template 適用（CI green）と記録。一方 AUDIT-2026-07.md §3 は lab-infra の 106 Windows/powershell hooks の Linux 移行を deferred と記録（2026-07-03）。
- **次の一手**: lab-infra の committed hooks を POSIX + `$CLAUDE_PROJECT_DIR` へ移行するか、`CLAUDE_CODE_REMOTE` ガードで cloud では no-op にする（IMPROVEMENT-BACKLOG P1.2 / cloud-context guard 項）。

#### BP-084 ⚠️ commit する .mcp.json は HTTP/SSE のみ・トークン絶対不 commit
- **規範**: repo に commit する .mcp.json は hosted な HTTP/SSE server のみとし、stdio / npx / localhost server は user config に留める。Authorization header・PAT 等のトークンはいかなる形でも commit せず、認証は session 側の接続・env に委ねる。
- **理由**: committed .mcp.json は全 clone と cloud session に配布されるため、localhost/stdio 定義は web で 100% 壊れ、inline トークンは即時の credential 漏洩になる。
- **現状**: ⚠️ 部分的 — docs/claude-code-web-readiness.md §3 が HTTP/SSE-only・「never a committed token」・該当 server がなければ .mcp.json を commit しない、を規定。AUDIT-2026-07.md §0/R2 は account 唯一の committed .mcp.json（lab-infra）が全 11 server localhost/Windows/stdio で web-broken と記録（2026-07-03）。トークン commit の検出記録はなし（.github/workflows/secrets-scan.yml が gitleaks full-history scan を実施）。
- **次の一手**: lab-infra の .mcp.json を committed HTTP/SSE-only 版と local-only 版に分割する（IMPROVEMENT-BACKLOG「Strip lab-infra .mcp.json of localhost/Windows/stdio servers」P1.5）。

#### BP-085 ⚠️ skill は repo 固有最小で commit し public/private 境界を守る
- **規範**: repo に commit する skill はその repo に必要な 1-2 個に絞り、グローバル設定（user-level dev-OS）の丸ごとコピーを禁止する。public repo の skill は tech-agnostic な汎用に限定し、事業固有 skill は private repo に隔離して同名でも中身を混在させない。
- **理由**: skill は repo とともに全 clone・cloud session へ配布されるため、無差別コピーはノイズ化と事業機密の公開漏出という二重の事故経路になる。
- **現状**: ⚠️ 部分的 — docs/claude-code-web-readiness.md §2「Don't copy the whole global dev-OS — commit only what THIS repo needs」。CONVENTIONS.md「public / private skill 境界（重要）」節が claude-lab-skills（public・汎用）と lab-skills-private（private・事業固有）の意図的 split と混在禁止（CLAUDE.md hard rule）を規定（2026-06-07）。ただし IMPROVEMENT-BACKLOG.md の「Byte-diff a sample SKILL.md across claude-lab-skills vs lab-skills-private」（P4.4、当該節の最上位 quick win）が未実施 = clean extraction は未検証。
- **次の一手**: 両 repo に存在する同名 SKILL.md を byte-diff し、public 側に事業固有内容の混入がないことを検証して記録する（backlog P4.4）。

#### BP-086 ❌ SKILL.md frontmatter と .claude 可搬性を CI で validate
- **規範**: commit した .claude/skills/*/SKILL.md の frontmatter（name / description）と、.claude / .mcp.json の web-portability（powershell・`C:\`・localhost 不在、JSON 妥当性）を CI で validate する。手動チェックリストに依存しない。
- **理由**: frontmatter 欠落の skill は web session で silent に load されず、CI ゲートがなければ壊れた agent 設定が気づかれないまま regress する。
- **現状**: ❌ 未採用 — docs/claude-code-web-readiness.md「Verify」節は手動手順（grep / sh -n / json.load / frontmatter 目視）のみ。この repo の ci.yml は governance ファイル存在 + JSON/YAML 構文 + repos.json 整合の検査だけで SKILL.md 検査なし。IMPROVEMENT-BACKLOG.md に「Validate committed SKILL.md frontmatter in CI」（P1.47）と「Add a CI lint that rejects non-web-portable .claude/.mcp.json in public repos」（P1.47）が未着手 backlog として登録済み。
- **次の一手**: .github の reusable workflow に SKILL.md frontmatter + web-portability lint を実装し、skill を commit している repo の CI に配布する（backlog の 2 項を統合実装）。

#### BP-087 ✅ エージェントブランチは名前空間 + 定期 GC
- **規範**: AI エージェントには専用のブランチ名前空間（claude/*, codex/* 等）を使わせ、merge されず放置されたブランチを定期レポート + 明示操作（open PR 除外・age gate・restore 手段つき）で GC する。削除の自動即時実行は default にしない。
- **理由**: エージェントは人間より桁違いの速度でブランチを量産するため、名前空間と定期 GC がないと放置ブランチが三桁規模で堆積しリポジトリの見通しを壊す。
- **現状**: ✅ 採用済 — .github/workflows/stale-branch-gc.yml が prefixes `codex/,claude/` を週次 cron で dry-run レポートし、削除は workflow_dispatch の apply=true のみ・open PR ブランチ除外・30 日 age gate を実装。IMPROVEMENT-BACKLOG.md Done 節（2026-06-07）に「Pruned 123 abandoned agent branches (codex/*, claude/* with no open PR) — restore manifest saved」と全 repo への delete_branch_on_merge 適用を記録。

#### BP-088 ⚠️ 触らせない repo には AGENTS freeze marker
- **規範**: エージェントに変更させない repo には repo-local の AGENTS/CLAUDE freeze marker（「変更禁止・successor / 理由を明示」）を置き、一括自動化・監査の除外リストにも機械可読に反映する。暗黙の「触るな」に頼らない。
- **理由**: 口頭・暗黙の禁止はエージェントに伝わらず、marker がなければアカウント横断の自動化パスが保護対象 repo を巻き込んで書き換える。
- **現状**: ⚠️ 部分的 — CONVENTIONS.md セキュリティ節に「lab-infra は repo-local AGENTS により Codex 変更禁止のため、監査対象には含めるが mutable failure からは除外する」と記録（2026-06-07 refresh）。IMPROVEMENT-BACKLOG.md 2026-07 Done 節も lab-infra を audit-only、HOT な claude-lab-config / obsidian-vault を手動除外して 24 PR を実施と記録。ただし除外は prose + パスごとの手動判断で、「Encode lab-infra as an allowlisted read-only-audit repo in audit config」（P1.1）は未着手。
- **次の一手**: repos.json に agent_frozen / audit_only フラグを追加して監査・GC・一括 PR パスが機械的に skip できるようにし、HOT repo（claude-lab-config, obsidian-vault）にも freeze marker を置く。

#### BP-089 ⚠️ AI 出力を無検証で merge しない
- **規範**: AI エージェントの出力は必ず PR + CI を通し、人間が diff を検証してから merge する。エージェントによる default branch への直接 push や無検証 automerge を既定にしない。
- **理由**: エージェントは自信を持って誤ったコード・ドキュメントを生成するため、人間の検証ゲートを外すと誤りが SSOT や本番に直結する。
- **現状**: ⚠️ 部分的 — 運用実態は記録上 PR 経由: IMPROVEMENT-BACKLOG.md 2026-07 Done 節は当該パスの全 24 変更を per-repo PR（CI green）で適用と記録、AUDIT-2026-07.md R3 は public 14 repo へ required status checks 付き branch protection 適用と記録（2026-07）。ただし「AI 出力は人間が検証してから merge」という明文規範は CONTRIBUTING.md にも governance/claude-code-convention.md にもなく、solo 運用で required reviews=0（CONVENTIONS.md セキュリティ節）・private 8 repo は Free プランで branch protection なし（security-baseline-2026-06-07.md Notes）。
- **次の一手**: governance/claude-code-convention.md に「agent PR は人間の diff 確認 + CI green を merge 条件とする」を明文化する（技術的強制が効かない Free プランの private repo こそ規範を文書で固定する）。

#### BP-090 ✅ user-level 設定（~/.claude）を commit しない
- **規範**: user-level 設定（~/.claude/*, ~/.claude.json の MCP 定義, secrets, .env）をプロジェクト repo に commit しない。repo に置くのはその repo 用に書き下ろした project-scope 設定のみとし、user config を版管理したければ専用 repo に隔離する。
- **理由**: user config には全プロジェクト横断の秘密情報と個人環境依存が含まれ、commit すれば漏洩と他環境での誤動作の両方を引き起こす。
- **現状**: ✅ 採用済 — docs/claude-code-web-readiness.md「Do NOT commit」節が `~/.claude/*`・`~/.claude.json` MCP・secrets/PATs・`.env` の commit を明示的に禁止し、auto-load 表で user-level は web に load されない設計を明記。AUDIT-2026-07.md §0 は「dev-OS は user-scoped で repo には一切 project されていなかった」と確認（2026-07-03）。CONVENTIONS.md 2026-07-08 reconciliation は ~/.claude runtime を専用 private repo（claude-lab-config）、cross-tool config SSOT を lab-os（PRIVATE）として分離管理と記録。


## C10. 運用・ガバナンス継続（BP-091〜BP-100）

#### BP-091 ✅ 週次の自動ガバナンス監査（schedule + fail loudly）
- **規範**: アカウント横断のガバナンス監査は schedule 実行の workflow として自動化し、手動再実行用に workflow_dispatch も残す。期待と異なる状態や token の権限不足はサイレントに通さず、job を fail させて必ず可視化する。
- **理由**: solo では監査を思い出す仕組みが自分しかなく、自動実行と fail loudly だけが設定ドリフトの確実な検知手段になる。
- **現状**: ✅ 採用済 — .github/workflows/weekly-governance-audit.yml が cron "17 19 * * 0" + workflow_dispatch で scripts/audit-github-governance.ps1 を実行し、step summary + artifact（governance-audit.json/md）を出力。script は scope failure（active repo が repos.json の active_count 未満）・mutable failure・SSOT 読取失敗のいずれも Write-Error / throw で job を fail させる。scheduled workflow の 60 日自動無効化には keepalive job（enable API でタイマーリセット、2026-07-13 追加）で対処。CONVENTIONS.md セキュリティ節にも「active_count 未満は権限不足として失敗させる」と明文化。

#### BP-092 ⚠️ 閾値・件数は機械可読 SSOT から読む（magic number 禁止）
- **規範**: 監査や CI が使う閾値・件数（active repo 数など）はコードに直書きせず、機械可読な台帳（SSOT）から実行時に読む。SSOT が読めないときは古い定数へ静かにフォールバックせず fail させる。
- **理由**: magic number は実態と必ず乖離し、監査が「古い基準で green」になる偽陰性を生む。
- **現状**: ⚠️ 部分的 — scripts/audit-github-governance.ps1 が repos.json の active_count（=28）を読んで閾値化し、SSOT 読取失敗は silent fallback ではなく hard error（2026-07-13 修正。明示的な -MinimumActiveRepos 指定時のみ override 可）。weekly-governance-audit.yml もフラグを渡さない。stale-branch-gc.yml も列挙 repo 数を repos.json の active_count と突合。ただし例外 repo リスト（MutableExceptions=@("lab-infra")）は script 内 hardcode のまま。
- **次の一手**: MutableExceptions を repos.json 側（audit_only フラグ等）へ移し、script はそれを読む形にする。

#### BP-093 ✅ SSOT と派生文書の整合を CI で機械検査
- **規範**: 台帳 SSOT の内部整合（件数フィールドの相互一致）と、そこから派生する文書（repo map 等）との一致を CI で assert する。人手レビューではなく機械検査で乖離を止める。
- **理由**: 台帳と派生文書のドリフトは静かに進行し、以後の監査・意思決定すべての前提を汚染する。
- **現状**: ✅ 採用済 — ci.yml（2026-07-13）に「Validate JSON syntax」「Validate YAML syntax」「Verify repos.json SSOT integrity」（jq -e で active_count = 非 archived 件数、total = 配列長、total = active+archived）「Verify ARCHITECTURE.md matches repos.json」（マーカー照合）を実装し、README/CONVENTIONS が参照する BEST-PRACTICES.md 等の存在も assert。default.json の semantic 検証（renovate-config-validator）は backlog の open ⚡ 項目として残る。

#### BP-094 ✅ 監査は日付つきスナップショットとして残し再ベースライン
- **規範**: 監査結果は日付つきのスナップショット文書として repo に commit し、上書きせず日付別に積む。大きな変更が入ったら再監査して baseline を取り直す。
- **理由**: 日付固定のスナップショットがないと「いつ時点で何が真だったか」が失われ、改善の効果測定も回帰検知もできない。
- **現状**: ✅ 採用済 — AUDIT-2026-07.md（27 repo の /100 採点、footer に「Generated 2026-07-03. Scores are a defensible snapshot … re-run the audit after the 2026-07 PRs land to re-baseline」）と governance/security-baseline-2026-06-07.md（filename に日付を含む verified baseline）が別文書として併存。weekly-governance-audit.yml も generatedAtUtc 入りの governance-audit.json/md を artifact 保存。

#### BP-095 ✅ スコア付き改善バックログ + Done ログ
- **規範**: 改善案は impact×effort×risk でスコアリングした単一バックログに集約し、quick-win（高 impact・低 effort・低 risk）に印をつけて着手順を機械的に決める。完了した項目は日付つき Done 節へ移し、実施記録として残す。
- **理由**: 可処分時間が最小の solo では、スコアなしバックログは実質「何もやらない」に等しく、Done 記録がないと同じ調査・判断を繰り返す。
- **現状**: ✅ 採用済 — IMPROVEMENT-BACKLOG.md — header に「⚡ = quick win (high impact / low effort / low risk)」、全 120 案（95+25、2026-07-13 に実数へ訂正）に P スコアと risk を付記（例「P2.2 · risk:low」）。「✅ Done in the 2026-06-07 pass」（12 項目）と「✅ Done in the 2026-07 pass」（24 PR を PR 番号つきで列挙）に加え 2026-07-13 addendum の Fixed 節と、Done ログの運用が継続。governance/claude-code-convention.md も per-repo IDEAS.md（value×effort×risk）を推奨。

#### BP-096 ✅ 破壊的一括操作は dry-run → 手動 apply の2段階 + 復元手段
- **規範**: branch 一括削除や repo 削除などの破壊的操作は、schedule では report（dry-run）のみとし、実削除は手動トリガ + 明示フラグ（apply=true）の2段階にする。実行前に mirror backup または SHA 入り restore manifest を必ず残す。
- **理由**: solo には破壊的操作を止めるレビュアーがいないため、2段階化と復元手段だけが回復不能ミスに対する保険になる。
- **現状**: ✅ 採用済 — stale-branch-gc.yml — schedule は report-only、削除は workflow_dispatch の apply=true のみ。2026-07-13 強化: 未マージ commit を持つ branch は自動削除対象外（compare API の ahead_by 検査）、削除行に SHA を記録（restore manifest として機能）、apply=true は PAT 必須。過去実績: 123 branch prune（restore manifest 保存、2026-06-07）、旧 archived 5 repo 削除時の mirror backup（CONVENTIONS.md 系譜表）。「破壊的一括操作は dry-run→手動 apply + 復元手段」の standing rule も 2026-07-13 に CONVENTIONS.md ブランチ/マージ節へ明文化。

#### BP-097 ✅ 例外は正当化つきで明文化し監査ロジックにエンコード
- **規範**: 規約から外れる repo・設定は、理由（正当化）つきで SSOT に明文化し、監査ロジック側にも例外として機械的にエンコードする。暗黙の例外や無記録の逸脱を残さない。
- **理由**: 明文化されない例外は監査 fail の常態化（警報の無意味化）か、逆に隠れた穴のどちらかになる。
- **現状**: ✅ 採用済 — CONVENTIONS.md セキュリティ節「lab-infra は repo-local AGENTS により Codex 変更禁止のため、監査対象には含めるが mutable failure からは除外する」。scripts/audit-github-governance.ps1 が $MutableExceptions = @("lab-infra") として実装し、row ごとに exception flag、summary に strictExceptions を出力（監査対象には含め続ける = audit-only）。can_approve の許可も「allowlist + 正当化」と規定（CONVENTIONS.md）。

#### BP-098 ✅ プラン制約は明記して deferred + 補償コントロールを記録
- **規範**: 料金プラン上使えない機能（例: Free プランでは private repo の branch protection 不可）は、制約の事実・deferred という判断・当面の補償コントロールをセットで文書化する。「できない」を暗黙に放置しない。
- **理由**: 記録がないと未設定が意図か欠落か判別できず、プラン変更時に拾い直すトリガも失われる。
- **現状**: ✅ 採用済 — AUDIT-2026-07.md R3「The 8 private repos return 403 Upgrade to GitHub Pro — branch protection on private repos needs a paid plan (account is free); deferred until upgrade」（2026-07-03）。IMPROVEMENT-BACKLOG.md 2026-07 Done 節「Deferred (needs a decision or paid plan): branch protection on the 8 private repos (GitHub Pro) …」。governance/security-baseline-2026-06-07.md Notes に補償コントロール「squash-only + delete_branch_on_merge … required status checks, PR self-approve OFF」を明記（2026-06-07）。CONVENTIONS.md にも dependency-review の public 限定（GHAS 制約）と platformAutomerge の private 制約を明記（2026-07-13）。

#### BP-099 ✅ public に出る自動化出力へ private 情報を漏らさない
- **規範**: public repo の workflow ログ・step summary・artifact は全世界に読めることを前提に設計し、private repo の名前×脆弱性件数×弱点一覧のような「攻撃地図」になる出力を含めない。詳細が必要な監査はローカル実行や private な出力先に分離する。
- **理由**: 監査・自動化の出力は本体コードより見落とされやすい情報漏洩面で、public repo では run ログも artifact も誰でも閲覧できる。
- **現状**: ✅ 採用済 — scripts/audit-github-governance.ps1（2026-07-13 修正）: public 出力では private repo 行を1つの集計行に丸める（行単位の匿名化は名前順から repos.json で逆引き可能なため不採用）。詳細は `-IncludePrivateDetail` のローカル実行のみ。失敗 repo 名のログ出力も public 以外は "(private)" に秘匿。weekly-governance-audit.yml の artifact に `retention-days: 7`。

#### BP-100 ✅ 主張したポスチャは検証してから記録する
- **規範**: 規約に「設定してある」と書く前に、実際の設定を read-only 監査で取得して検証し、検証済みの結果だけを dated baseline として記録する。asserted（主張）と verified（検証済）を明確に区別する。
- **理由**: 文書上のポリシーと実設定は自然に乖離するため、未検証の記録は誤った安心（false assurance）の源になる。
- **現状**: ✅ 採用済 — governance/security-baseline-2026-06-07.md header「This is the *verified* posture (CONVENTIONS.md security section was asserted but never verified before this pass)」。IMPROVEMENT-BACKLOG.md の最高スコア項目（P5.5）「CONVENTIONS asserts a full security posture but recon never fetched per-repo settings … so policy is unverified」→ Done 節「Ran account-wide security audits … + committed baseline」（2026-06-07）で実施済み。AUDIT-2026-07.md も method に公式 docs 照合（doc verification）を明記（2026-07-03）。。なお 2026-06-07 baseline の branch-prot 列に測定誤りの疑いが判明し 2026-07-13 に訂正注記を追記 — verify 手法自体も次回 baseline で再点検対象
