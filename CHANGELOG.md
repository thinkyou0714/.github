# Changelog

`thinkyou0714/.github`（アカウント community health + governance SSOT）の変更履歴。
書式は [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)、versioning は
[Semantic Versioning](https://semver.org/spec/v2.0.0.html) に従う。

**バージョン付けの対象**: 他 repo から参照される reusable workflow
（`dependency-review` / `secrets-scan`）が版管理の public surface。consumer は
tag で pin する（README「Reusable workflows を他 repo から使う」節を参照）。

## [Unreleased]

### Added

- `CHANGELOG.md`（本ファイル）と README「Reusable workflows を他 repo から使う」節（`@vX.Y.Z` pin の手順）。

## [1.0.0] - 2026-07-13

最初のタグ付きリリース（内容は #16 マージ時点）。

> **タグ付けは owner 手番**: 本 repo の authoring 環境（git relay）は tag の push を受け付けないため、
> v1.0.0 タグはまだ remote に無い。以下のいずれかで作成する。
> `git tag -a v1.0.0 <#16 merge commit> -m "v1.0.0" && git push origin v1.0.0`、
> または GitHub → Releases → *Draft a new release* → tag `v1.0.0`（#16 マージ commit を指定）。
> タグ作成後、上の compare/releases リンクが解決し、consumer は `@v1.0.0` で pin 可能になる。

### Added

- `BEST-PRACTICES.md`: 個人開発者 GitHub ベストプラクティス 100（各項目に採用状況 + 根拠）。
- reusable workflow を `on: workflow_call` で公開: `dependency-review`, `secrets-scan`。
- `repos.json`: 機械可読リポジトリ台帳 SSOT（`active_count`・`audit_only` フラグ）。
- CI ゲート: JSON/YAML 構文・repos.json 整合・ARCHITECTURE マーカー・内部リンク検査・Renovate preset 検証・actionlint。
- `weekly-governance-audit` の keepalive（60 日自動無効化対策）、`stale-branch-gc` の安全強化。
- community health files: CONTRIBUTING / CODE_OF_CONDUCT / SECURITY / SUPPORT / FUNDING / issue・PR テンプレ。
- Renovate 中央 preset（`default.json`）= 全 repo の依存ポリシー単一編集点。

### Changed

- `ARCHITECTURE.md` を `repos.json` から再生成（21 → 28 repo）。
- CONVENTIONS.md に「リリース / バージョニング」節を新設。

### Fixed

- `ISSUE_TEMPLATE/` → `.github/ISSUE_TEMPLATE/`（default issue templates の必須パス）。
- `stale-branch-gc` の誤削除リスク（open PR のページネーション・未マージ branch 除外・apply 時 PAT 必須）。
- governance 監査: public 出力での private repo 秘匿・自リポ自己 FAIL 判定・閾値/例外の SSOT 化。
- 多数のドキュメント整合修正（ライセンス表記・件数・陳腐化参照）— 詳細は #16。

[Unreleased]: https://github.com/thinkyou0714/.github/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/thinkyou0714/.github/releases/tag/v1.0.0
