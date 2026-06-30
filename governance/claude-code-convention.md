# Claude Code per-repo convention (org standard)

> 2026-06 制定。各 active repo が Claude Code (AI 支援開発) に対してどう自己記述するかの SSOT 補遺。
> `CONVENTIONS.md`「メタデータ」の Claude Code 版。

GitHub の community-health ファイル (SECURITY.md / CONTRIBUTING.md 等) はこの `.github` repo から
**自動継承**されるが、**`CLAUDE.md` / `.claude/` は自動継承されない**。各 repo が自前で持つ必要がある。
本ドキュメントはその**テンプレート兼リファレンス**。

## 各 active repo が持つべきもの

1. **`CLAUDE.md`** (repo root)
   - 階層的・簡潔・**コード実態に正確** (捏造禁止。実在するパス/コマンド/不変条件のみ)。
   - 推奨セクション: `Quick Start` → `Architecture` → `Commands` (package scripts を正確に) →
     `Testing` → `Safety / Guardrails` → `Extending`。
   - 安全層を記述する際は**過大表現しない**: hook の blocklist は「curated な特定トークン列」であって
     汎用フィルタではないこと、`--dangerously-skip-permissions` (bypass) 下では `permissions.allow/deny`
     が**強制されず hook のみが実効防御**であること、を明記する。

2. **`.claude/settings.json`**
   - `permissions.allow` は **read-only/安全な操作のみ** (repo の実 package scripts + 読み取り専用 git:
     `git status`/`log`/`diff`/`branch`)。
   - `permissions.deny` に破壊的操作 (force-push / hard reset / force-clean / `--no-verify` /
     再帰強制削除) を明示 (defense-in-depth。bypass mode では非強制な点に留意)。
   - 推測フィールドを足さない。

   参考スケルトン:
   ```json
   {
     "permissions": {
       "allow": [
         "Bash(npm test)", "Bash(npm run typecheck)", "Bash(npm run lint)", "Bash(npm run build)",
         "Bash(git status)", "Bash(git log)", "Bash(git diff)", "Bash(git branch)"
       ],
       "deny": [
         "Bash(git push --force*)", "Bash(git push -f*)", "Bash(git reset --hard*)",
         "Bash(git clean -f*)", "Bash(*--no-verify*)"
       ]
     }
   }
   ```

3. **`IDEAS.md`** (任意) — スコア付き改善 backlog (value × effort × risk、T1/T2/T3)。

## Renovate / Dependabot との関係
- 依存自動化は **Renovate 一本** (`CONVENTIONS.md`「依存自動化」)。Renovate 採用 repo に
  **Dependabot を重ねない** (PR 競合)。`.claude/settings.json` はこの方針と直交。

## 採用状況 (2026-06)
- `ccmux` / `fugu` / `engineer-tenshoku-navi` / `denken-os` が本 convention に準拠。
- 新規 active repo は first push 前メタデータ整備時に `CLAUDE.md` + `.claude/settings.json` を併せて用意する。

## 関連
- `CONVENTIONS.md` (リポジトリ規約 SSOT) ―「メタデータ」「依存自動化」「セキュリティ」節。
- 各 repo の `IDEAS.md` (per-repo 改善 backlog)。
