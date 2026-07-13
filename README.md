# .github — thinkyou0714 community health + governance SSOT

このリポジトリは [thinkyou0714](https://github.com/thinkyou0714) アカウントの**特別リポジトリ**で、3つの役割を持ちます。

1. **Default community health files** — 各リポジトリで未定義のファイルのフォールバック
2. **ガバナンス SSOT** — 全リポジトリ共通の規約・台帳・監査記録
3. **自動化** — 週次ガバナンス監査・Renovate 中央 preset 等

## 1. Default community health files

GitHub の `.github` リポジトリ機構により、各リポジトリで該当ファイルが定義されていない場合、ここに置かれたファイルが**フォールバックとして自動適用**されます。

| File | 目的 |
|---|---|
| `FUNDING.yml` | リポ右上の Sponsor ボタンに表示される funding link |
| `CONTRIBUTING.md` | コントリビューションガイドライン |
| `CODE_OF_CONDUCT.md` | Contributor Covenant v2.1 |
| `SECURITY.md` | 脆弱性報告先 |
| `SUPPORT.md` | ユーザサポート窓口 |
| `.github/ISSUE_TEMPLATE/` | Issue テンプレ (bug / feature / question) と contact links の fallback（仕様上、issue テンプレのみ `.github/ISSUE_TEMPLATE/` 配下必須） |
| `PULL_REQUEST_TEMPLATE.md` | PR テンプレ |

> **継承されないもの**: `LICENSE`・`.github/CODEOWNERS`・`.github/workflows/` は community health file ではなく**このリポジトリ自身のためのファイル**です（他リポには継承されません）。各リポジトリには個別に LICENSE 等を置く必要があります。

### 上書き

個別リポジトリで同名ファイルを定義すると、そちらが優先されます。
たとえば `thinkyou0714/ccmux/CONTRIBUTING.md` があれば、`ccmux` ではそれが使われ、本リポの `CONTRIBUTING.md` は無視されます。対象リポジトリで要件（例: セキュリティ連絡先、テンプレ項目）が異なる場合は各リポジトリで上書きしてください。

## 2. ガバナンス SSOT

| File | 内容 |
|---|---|
| [`CONVENTIONS.md`](CONVENTIONS.md) | 全 repo 共通規約（命名 / ブランチ / メタデータ / ライセンス / セキュリティ / 依存自動化）の SSOT |
| [`BEST-PRACTICES.md`](BEST-PRACTICES.md) | 個人開発者ベストプラクティス 100（各項目にこのアカウントでの採用状況を紐付け） |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | 全 repo の一覧マップ（`repos.json` から再生成） |
| [`repos.json`](repos.json) | リポジトリ台帳の機械可読 SSOT（`weekly-governance-audit` が `active_count` を参照） |
| [`IMPROVEMENT-BACKLOG.md`](IMPROVEMENT-BACKLOG.md) | スコア付き改善バックログ（2026-06 の 95 案 + 2026-07 の 25 案 + 2026-07-13 追補） |
| [`AUDIT-2026-07.md`](AUDIT-2026-07.md) | 日付つき監査スナップショット（27 repo /100 採点） |
| [`governance/`](governance/) | セキュリティベースライン・鍵ローテーション runbook・Claude Code 規約 |
| [`docs/claude-code-web-readiness.md`](docs/claude-code-web-readiness.md) | Claude Code on the web 対応テンプレート |

## 3. 自動化

| File | 内容 |
|---|---|
| `default.json` | **Renovate 中央 preset**（全 repo の依存ポリシーの唯一の編集点）。各 repo は `{ "extends": ["local>thinkyou0714/.github"] }` で継承 |
| `.github/workflows/ci.yml` | このリポ自身のガバナンスファイル検査（存在 + JSON/YAML 構文 + SSOT 整合） |
| `.github/workflows/weekly-governance-audit.yml` | 週次のアカウント横断監査（repo 設定 / Dependabot alerts / workflow hardening） |
| `.github/workflows/stale-branch-gc.yml` | 放置エージェントブランチ（`codex/*`, `claude/*`）の定期レポート + 手動 GC |
| `.github/workflows/secrets-scan.yml` | gitleaks による secret スキャン（full history） |
| `.github/workflows/dependency-review.yml` | PR の依存レビュー |
| `scripts/audit-github-governance.ps1` | 週次監査の実体（閾値は `repos.json` の `active_count` を参照） |

## ライセンス

本リポジトリは [MIT License](LICENSE) です（`LICENSE` が正）。ドキュメント類も MIT の許諾条件（著作権表示の保持）の下で自由に流用できます。アカウント全体のライセンスポリシー（software → MIT / 文章・記事 → CC-BY-4.0）は [`CONVENTIONS.md`](CONVENTIONS.md) を参照してください。

## 参考

- [GitHub Docs — Creating a default community health file](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)
