# Making a repo usable from **Claude Code on the web**

Claude Code web/cloud sessions (claude.ai/code, GitHub-connected) run in an **ephemeral Ubuntu
24.04 container** — NOT your machine. They cannot see your local `~/.claude/`, local Obsidian REST
API (`:27124`), or local Ollama (`:4101`). **Whatever the repo commits is all a web session gets.**

This is the SSOT template for making a `thinkyou0714` repo "web-ready" for **CLI + Skills + MCP**.
Verified against <https://code.claude.com/docs/en/claude-code-on-the-web.md> (2026-07).

## What auto-loads on web (commit these)

| File / dir | Loads on web? | Purpose |
|---|:--:|---|
| `AGENTS.md` or `CLAUDE.md` (root) or `.claude/CLAUDE.md` | ✅ | Project context for the agent |
| `.claude/skills/<name>/SKILL.md` | ✅ | Repo skills (need valid `name` + `description` frontmatter) |
| `.claude/commands/*.md` | ✅ | Slash commands |
| `.claude/rules/*.md` | ✅ | Policy files |
| `.claude/settings.json` hooks | ✅ | Run in cloud (must be POSIX — see below) |
| `.mcp.json` (repo root) | ✅ | **HTTP/SSE servers only** (see MCP section) |
| `~/.claude/*` (user-level) | ❌ | Never loads on web — that's why we project into the repo |

Pre-installed in the sandbox (no need to provision): **Node 20/21/22**, Python 3.x (pip/uv/poetry),
git, jq, ripgrep, Docker, PostgreSQL 16, Redis 7 — plus eslint/prettier/ruff/pytest/mypy.

## 1. CLI — install repo deps with a SessionStart hook

Base CLI tools are pre-installed; your repo's **dependencies are not**. Add a POSIX, idempotent,
cloud-guarded SessionStart hook. **No `powershell`, no `C:\` paths** (they fail on Linux).

`.claude/settings.json`:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          { "type": "command", "command": "sh \"$CLAUDE_PROJECT_DIR/.claude/bootstrap.sh\"" }
        ]
      }
    ]
  }
}
```

`.claude/bootstrap.sh` (idempotent — safe on every session, local and cloud). `--ignore-scripts`
keeps dependency lifecycle scripts (`postinstall`/`prepare`) from running **unattended** when a
cloud agent opens the repo (supply-chain hardening); drop it only if your repo needs those scripts:
```sh
#!/bin/sh
dir="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$dir" || exit 0
if [ -f package.json ] && [ ! -d node_modules ]; then
  if [ -f package-lock.json ]; then
    npm ci --no-audit --no-fund --ignore-scripts || npm install --no-audit --no-fund --ignore-scripts || true
  else
    npm install --no-audit --no-fund --ignore-scripts || true
  fi
fi
if [ -f pyproject.toml ] && [ ! -d .venv ] && command -v uv >/dev/null 2>&1; then
  uv sync --frozen 2>/dev/null || uv sync 2>/dev/null || true
fi
exit 0
```
Content/docs-only repos (no `package.json`) don't need this — skip it.

## 2. Skills — commit 1-2 real, repo-relevant skills

`.claude/skills/<name>/SKILL.md` with frontmatter:
```markdown
---
name: run-tests
description: Run this repo's test suite and summarize failures. Use when asked to test or verify changes.
---
Run `npm test` (or the project's documented test command). Summarize pass/fail counts and the first
failing assertion per failed test. Do not fix code unless asked.
```
Keep them concrete and repo-specific (test, build, release, lint). Don't copy the whole global
dev-OS — commit only what THIS repo needs.

## 3. MCP — HTTP/SSE only, never a committed token

**stdio/`npx`/`uvx` servers and anything on `localhost` do NOT work on web.** Only commit `.mcp.json`
when a hosted HTTP/SSE server genuinely helps this repo, and reference the token via env — never
inline a PAT.

`.mcp.json` (opt-in example — GitHub-hosted MCP):
```json
{
  "mcpServers": {
    "github": { "type": "http", "url": "https://api.githubcopilot.com/mcp/" }
  }
}
```
The web session supplies auth via its GitHub connection / env; do not commit `Authorization`
headers with real tokens. If no hosted server applies, **commit no `.mcp.json`** — local-only MCP
(Obsidian/Ollama/n8n) stays in your user config and simply isn't available on web (by design).

## 4. Root AGENTS.md — minimal repo context

```markdown
# AGENTS.md
<one-paragraph what/why of this repo>
- Stack: <language/framework>
- Setup: deps auto-install via `.claude/bootstrap.sh` (SessionStart)
- Test: `<command>`  ·  Build: `<command>`
- Conventions: <link to CONVENTIONS or 2-3 bullets>
```

## Do NOT commit
- User-level config (`~/.claude/*`, `~/.claude.json` MCP), secrets/PATs, `.env`.
- Windows-only hooks (`powershell`, `.bat`, `C:\...`).
- stdio/localhost MCP servers.

## Verify
1. `python -c "import json;json.load(open('.claude/settings.json'))"` and same for `.mcp.json`.
2. `sh -n .claude/bootstrap.sh` (POSIX syntax check).
3. `grep -REn 'powershell|C:\\\\|127.0.0.1|localhost' .claude .mcp.json` → must be empty.
4. Each `.claude/skills/*/SKILL.md` has `name:` + `description:` frontmatter.

Rollout status + per-repo tracking: see `AUDIT-2026-07.md` §0 and `IMPROVEMENT-BACKLOG.md`
(Web-readiness section).
