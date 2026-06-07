# THINK YOU LAB — Repository Map (ARCHITECTURE)

> Single-glance map of every `thinkyou0714` repo: which repo owns what. Machine-readable SSOT: [`repos.json`](repos.json). Conventions: [`CONVENTIONS.md`](CONVENTIONS.md).
> Generated 2026-06-07 — **21 active + 5 archived = 26**.

## Flagship OSS (public, MIT)

| repo | vis | purpose |
|---|---|---|
| [`ccmux`](https://github.com/thinkyou0714/ccmux) | 🌐 | Claude Code Multiplexer (Zellij × git worktree × Obsidian) |
| [`github-flow-kit`](https://github.com/thinkyou0714/github-flow-kit) | 🌐 | 4 GitHub-native Claude Code skills (pr-respond, release-notes, issue-triage, repo-tour) |
| [`codex-toolkit`](https://github.com/thinkyou0714/codex-toolkit) | 🌐 | Portable installable dev OS for the Codex CLI |
| [`denken-os`](https://github.com/thinkyou0714/denken-os) | 🌐 | 電験 (電気主任技術者試験) 学習 OS (pre-alpha) |
| [`claude-lab-skills`](https://github.com/thinkyou0714/claude-lab-skills) | 🌐 | Tech-agnostic thinking-OS skill packs for Claude Code (MIT) |

## Content / Docs (public)

| repo | vis | purpose |
|---|---|---|
| [`public-docs`](https://github.com/thinkyou0714/public-docs) | 🌐 | Public template implementation guides (Next.js + MDX, Vercel) |
| [`zenn-content`](https://github.com/thinkyou0714/zenn-content) | 🌐 | Zenn article sources (AI automation / Claude Code / n8n / Obsidian) |
| [`lab-public`](https://github.com/thinkyou0714/lab-public) | 🌐 | Public-safe experiments and operational docs |
| [`thinkyou0714`](https://github.com/thinkyou0714/thinkyou0714) | 🌐 | Profile README |
| [`.github`](https://github.com/thinkyou0714/.github) | 🌐 | Org community-health + governance SSOT (CONVENTIONS, Renovate preset, audits) |

## Product (private)

| repo | vis | purpose |
|---|---|---|
| [`tyl-monorepo`](https://github.com/thinkyou0714/tyl-monorepo) | 🔒 | Product monorepo (Next.js): thinkyou-lp, acquisition-engine, video-pipeline, mcp-server, agents |
| [`lab-lms`](https://github.com/thinkyou0714/lab-lms) | 🔒 | LMS product (Next.js / Supabase / Stripe) |

## Infra / Tooling (private)

| repo | vis | purpose |
|---|---|---|
| [`lab-infra`](https://github.com/thinkyou0714/lab-infra) | 🔒 | Everything-monorepo shell + AI-agent operating discipline + public mirror |
| [`lab-infra-n8n`](https://github.com/thinkyou0714/lab-infra-n8n) | 🔒 | n8n workflow SSOT (491 workflow JSON) |
| [`lab-apps-internal`](https://github.com/thinkyou0714/lab-apps-internal) | 🔒 | Internal apps (autoclaw, signal-core, labctl, ollama-proxy, sva) |
| [`codex-hub`](https://github.com/thinkyou0714/codex-hub) | 🔒 | Codex provider routing & cost orchestration |
| [`claude-lab-config`](https://github.com/thinkyou0714/claude-lab-config) | 🔒 | Version-controlled ~/.claude personal dev kit |
| [`lab-skills-private`](https://github.com/thinkyou0714/lab-skills-private) | 🔒 | Business-sensitive private skill packs (strategy-design, data-auth-ops) |
| [`obsidian-vault`](https://github.com/thinkyou0714/obsidian-vault) | 🔒 | Obsidian knowledge vault sync |
| [`lab-inbox-bot`](https://github.com/thinkyou0714/lab-inbox-bot) | 🔒 | Slack inbox bot (capture-to-Obsidian front-end) |
| [`private-members`](https://github.com/thinkyou0714/private-members) | 🔒 | Gated member resources (paid-tier counterpart to public-docs) |

## Archived (read-only — see supersession)

| repo | vis | purpose |
|---|---|---|
| [`lab-os`](https://github.com/thinkyou0714/lab-os) | 🔒 | [archived] old AI-agent-config SSOT → claude-lab-config → **claude-lab-config** |
| [`obsidian-knowledge-ops`](https://github.com/thinkyou0714/obsidian-knowledge-ops) | 🔒 | [archived] Obsidian→NotebookLM→IP system → obsidian-vault → **obsidian-vault** |
| [`n8n-gmail-vault`](https://github.com/thinkyou0714/n8n-gmail-vault) | 🔒 | [archived] n8n × Gmail vault → lab-infra-n8n + tyl-monorepo → **lab-infra-n8n + tyl-monorepo** |
| [`skills-registry`](https://github.com/thinkyou0714/skills-registry) | 🔒 | [archived] skills registry → github-flow-kit → **github-flow-kit** |
| [`lab-n8n-workflows`](https://github.com/thinkyou0714/lab-n8n-workflows) | 🔒 | [archived] near-duplicate fork → tyl-monorepo + lab-infra-n8n → **tyl-monorepo + lab-infra-n8n** |

## Key relationships

- **`lab-infra`** is the everything-monorepo *shell*. Six subtrees were extracted (history-preserved, `MOVED.md` tombstones, no duplication): `lab-infra-n8n`, `lab-apps-internal`, `codex-hub`, `lab-lms`, `lab-skills-private`, `lab-inbox-bot`. **Do not re-merge.**
- **Public/private skill split:** `claude-lab-skills` (public, tech-agnostic) vs `lab-skills-private` (private, business-sensitive) — same pack names, different content. Never mix.
- **Content split:** `public-docs` (free guides) vs `private-members` (gated template bodies). `obsidian-templates/` is canonical in private, reference-copied to public.
- **n8n SSOT** = `lab-infra-n8n`. **Product SSOT** = `tyl-monorepo`. **Dev-kit SSOTs** = `claude-lab-config` (Claude) / `codex-toolkit` (Codex).
