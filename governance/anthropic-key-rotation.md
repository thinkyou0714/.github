# ANTHROPIC_API_KEY — rotation runbook (audit 2026-06-07)

> The key is **rotated by you** in the Anthropic console; this doc tells you every place that must be updated so nothing silently breaks. Prior note: the `tyl-monorepo` + `lab-infra` Actions secrets were observed **invalid** — rotation also fixes those.

## Where the key lives

### GitHub Actions secrets (CI)
| repo | secret | likely use |
|---|---|---|
| `tyl-monorepo` | `ANTHROPIC_API_KEY` | LAB Daily Audit / agent CI (observed invalid → rotate) |
| `lab-infra` | `ANTHROPIC_API_KEY` | agent CI / audits (observed invalid → rotate) |
| `github-flow-kit` | `ANTHROPIC_API_KEY` | Claude-powered CI (review/release) |

### Runtime SDK consumers (`@anthropic-ai/sdk` in package.json)
| repo | surface | where the key is configured |
|---|---|---|
| `denken-os` | app/CI | Vercel env and/or repo Actions secret |
| `lab-inbox-bot` | bot runtime | host/process env (`ANTHROPIC_API_KEY`), Slack bot |
| `lab-lms` | app | Vercel env (Supabase/Stripe app) |

> Also check non-repo consumers: local `autoclaw` / `codex-hub` services read the key from machine env, not a GitHub secret.

## Rotation steps
1. **Create new key**: console.anthropic.com → API Keys → Create. Copy once.
2. **Update the 3 Actions secrets** (fast, scriptable):
   ```bash
   for r in tyl-monorepo lab-infra github-flow-kit; do
     gh secret set ANTHROPIC_API_KEY -R thinkyou0714/$r --body "<NEW_KEY>"
   done
   ```
3. **Update runtime configs**: Vercel (`denken-os`, `lab-lms`) project env → `ANTHROPIC_API_KEY`; `lab-inbox-bot` host env / process manager; local `autoclaw`/`codex-hub` env.
4. **Revoke the old key** in the console only after CI + runtime are green.
5. **Verify**: re-run `LAB Daily Audit` (tyl-monorepo) / any Claude CI job → should pass (was failing on the invalid key).

## Prevention
- Prefer a single short-lived/scoped key per surface where possible.
- Don't commit keys. 3 repo のうち secret scanning + push protection が有効なのは **`github-flow-kit` (public) のみ**。`tyl-monorepo` / `lab-infra` は private のため secret scanning 対象外（`security-baseline-2026-06-07.md` でも n/a）— キー混入防止は read-only workflow token・gitleaks CI・手動レビューに依存する。
