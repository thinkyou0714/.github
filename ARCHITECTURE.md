# THINK YOU LAB — Repository Map (ARCHITECTURE)

> Single-glance map of every `thinkyou0714` repo. Machine-readable SSOT: [`repos.json`](repos.json). Conventions: [`CONVENTIONS.md`](CONVENTIONS.md).
> Regenerated 2026-07-13 from `repos.json` (2026-07-08 reconciliation) — **28 repos, all active**.
> ⚠️ この表は `repos.json` から再生成する。repo を増減させたら `repos.json` を先に更新し、本ファイルを追従させること（CI が下のマーカーと `repos.json.active_count` の一致を検査する）。

<!-- repos.json active_count: 28 -->

## Flagship OSS (public, 8)

| repo | vis | purpose |
|---|---|---|
| [`agmsg`](https://github.com/thinkyou0714/agmsg) | 🌐 | Cross-vendor CLI-agent messaging (Bash+SQLite, no daemon); fork of fujibee/agmsg |
| [`agmsg-kit`](https://github.com/thinkyou0714/agmsg-kit) | 🌐 | Hardened reproducible installer + governance for fujibee/agmsg cross-agent messaging |
| [`ccmux`](https://github.com/thinkyou0714/ccmux) | 🌐 | Claude Code Multiplexer (Zellij × git worktree × Obsidian) |
| [`claude-lab-skills`](https://github.com/thinkyou0714/claude-lab-skills) | 🌐 | Tech-agnostic thinking-OS skill packs for Claude Code (MIT) |
| [`codex-toolkit`](https://github.com/thinkyou0714/codex-toolkit) | 🌐 | Portable installable dev OS for the Codex CLI |
| [`denken-os`](https://github.com/thinkyou0714/denken-os) | 🌐 | 電験 (電気主任技術者試験) 学習 OS (pre-alpha) |
| [`fugu`](https://github.com/thinkyou0714/fugu) | 🌐 | Zero-dependency TypeScript client + CLI for the Sakana Fugu OpenAI-compatible API |
| [`github-flow-kit`](https://github.com/thinkyou0714/github-flow-kit) | 🌐 | 6 GitHub-native Claude Code skills (pr-respond, release-notes, issue-triage, repo-tour, gh-pr-perm-audit, gh-repo-security-audit) |

## Content / Docs (public, 6)

| repo | vis | purpose |
|---|---|---|
| [`.github`](https://github.com/thinkyou0714/.github) | 🌐 | Account-default community health + governance SSOT (CONVENTIONS, Renovate preset, audits) |
| [`engineer-tenshoku-navi`](https://github.com/thinkyou0714/engineer-tenshoku-navi) | 🌐 | Engineer/IT-career affiliate static site (Astro, SEO/compliance-designed) — public product; a future `product-public` group may be warranted |
| [`lab-public`](https://github.com/thinkyou0714/lab-public) | 🌐 | Public-safe experiments and operational docs |
| [`public-docs`](https://github.com/thinkyou0714/public-docs) | 🌐 | Public template implementation guides (Next.js + MDX, Vercel) |
| [`thinkyou0714`](https://github.com/thinkyou0714/thinkyou0714) | 🌐 | Profile README |
| [`zenn-content`](https://github.com/thinkyou0714/zenn-content) | 🌐 | Zenn article sources (AI automation / Claude Code / n8n / Obsidian) |

## Product (private, 2)

| repo | vis | purpose |
|---|---|---|
| [`lab-lms`](https://github.com/thinkyou0714/lab-lms) | 🔒 | LMS product (Next.js / Supabase / Stripe) |
| [`tyl-monorepo`](https://github.com/thinkyou0714/tyl-monorepo) | 🔒 | Product monorepo (Next.js): thinkyou-lp, acquisition-engine, video-pipeline, mcp-server, agents |

## Infra / Tooling (private, 12)

| repo | vis | purpose |
|---|---|---|
| [`claude-lab-config`](https://github.com/thinkyou0714/claude-lab-config) | 🔒 | Version-controlled ~/.claude personal dev kit |
| [`codex-hub`](https://github.com/thinkyou0714/codex-hub) | 🔒 | Codex provider routing & cost orchestration |
| [`lab-apps-internal`](https://github.com/thinkyou0714/lab-apps-internal) | 🔒 | Internal apps (autoclaw, signal-core, labctl, ollama-proxy, sva) |
| [`lab-inbox-bot`](https://github.com/thinkyou0714/lab-inbox-bot) | 🔒 | Slack inbox bot (capture-to-Obsidian front-end) |
| [`lab-infra`](https://github.com/thinkyou0714/lab-infra) | 🔒 | Everything-monorepo shell + AI-agent operating discipline + public mirror |
| [`lab-infra-n8n`](https://github.com/thinkyou0714/lab-infra-n8n) | 🔒 | n8n workflow SSOT (491 workflow JSON) |
| [`lab-os`](https://github.com/thinkyou0714/lab-os) | 🔒 | Cross-tool config SSOT repo (Cursor+Claude Code+Obsidian); recreated 2026-07-05 — canonical status vs claude-lab-config is a pending owner decision |
| [`lab-research`](https://github.com/thinkyou0714/lab-research) | 🔒 | Private research KM scaffold (validate CI); recreated |
| [`lab-skills-private`](https://github.com/thinkyou0714/lab-skills-private) | 🔒 | Business-sensitive private skill packs (strategy-design, data-auth-ops) |
| [`obsidian-vault`](https://github.com/thinkyou0714/obsidian-vault) | 🔒 | Obsidian knowledge vault sync |
| [`private-members`](https://github.com/thinkyou0714/private-members) | 🔒 | Gated member resources (paid-tier counterpart to public-docs) |
| [`skills-registry`](https://github.com/thinkyou0714/skills-registry) | 🔒 | Minimal skill registry/index (validate CI); recreated |

## Deleted (2026-06-07, formerly archived — lineage preserved)

| deleted repo | superseded by |
|---|---|
| `lab-n8n-workflows` | tyl-monorepo + lab-infra-n8n |
| `obsidian-knowledge-ops` | obsidian-vault |
| `n8n-gmail-vault` | lab-infra-n8n + tyl-monorepo |
| `lab-os` (旧) | claude-lab-config |
| `skills-registry` (旧) | github-flow-kit |

> ⚠️ `lab-os` と `skills-registry` は 2026-07 に**同名の新 repo として再作成**された（CONVENTIONS.md「2026-07-08 reconciliation」参照）。上表の系譜は 2026-06-07 に削除された**旧 repo** についての記録であり、現行の同名 repo とは別物。

## Key relationships

- **`lab-infra`** is the everything-monorepo *shell*. Six subtrees were extracted (history-preserved, `MOVED.md` tombstones, no duplication): `lab-infra-n8n`, `lab-apps-internal`, `codex-hub`, `lab-lms`, `lab-skills-private`, `lab-inbox-bot`. **Do not re-merge.**
- **Public/private skill split:** `claude-lab-skills` (public) vs `lab-skills-private` (private) — same pack names, different content. Never mix.
- **Content split:** `public-docs` (free) vs `private-members` (gated).
- **Config SSOT boundary:** `lab-os` (recreated 2026-07-05) = cross-tool config SSOT *repo*; `claude-lab-config` = live `~/.claude` runtime component. Owner-confirmed "keep both" — canonical-vs-component boundary is a pending owner decision (see `repos.json`).
- **SSOTs:** n8n = `lab-infra-n8n` · product = `tyl-monorepo` · dev-kits = `claude-lab-config` (Claude) / `codex-toolkit` (Codex) · governance = `.github` (this repo).
