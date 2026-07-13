# THINK YOU LAB — Security Baseline (verified 2026-06-07)

> Account-wide read-only audit via `gh_repo_security_audit` + `gh_actions_pr_perm_audit`. This is the *verified* posture (CONVENTIONS.md security section was asserted but never verified before this pass).
>
> ⚠️ **訂正 (2026-07-13)**: 本表の branch-prot 列「yes」は 2026-07-03 の再監査（`AUDIT-2026-07.md` §3 R3: branch protection **0/27**）と両立しない。1ヶ月で全 public の protection が消えた記録は無く、本表の branch-prot 判定手法の誤りの疑いが濃厚。現況は AUDIT-2026-07 パスで **14 public repo に適用済**（private は Free プラン制約で deferred）。branch-prot 列は本表を根拠にしないこと。

## Summary
- repos audited: 21 active
- repo-security WARN findings: **0**
- PR self-approve risk repos (can_approve=true, unallowlisted): **0**
- All repos: `default_workflow_permissions=read`, `allowed_actions=selected`, Dependabot alerts `on`.
- All public repos: secret scanning `enabled`, branch protection `yes`.
- SHA-pinning: central Renovate preset extends `helpers:pinGitHubActionDigests` (account-wide).

## Per-repo
| repo | vis | token | actions | branch-prot | secret-scan | dependabot | PR self-approve |
|---|---|---|---|---|---|---|---|
| .github | public | read | selected | yes | enabled | on | OFF (secure) |
| ccmux | public | read | selected | yes | enabled | on | OFF (secure) |
| claude-lab-config | private | read | selected | none | n/a | on | OFF (secure) |
| claude-lab-skills | public | read | selected | yes | enabled | on | OFF (secure) |
| codex-hub | private | read | selected | none | n/a | on | OFF (secure) |
| codex-toolkit | public | read | selected | yes | enabled | on | OFF (secure) |
| denken-os | public | read | selected | yes | enabled | on | OFF (secure) |
| github-flow-kit | public | read | selected | yes | enabled | on | OFF (secure) |
| lab-apps-internal | private | read | selected | none | n/a | on | OFF (secure) |
| lab-inbox-bot | private | read | selected | none | n/a | on | OFF (secure) |
| lab-infra | private | read | selected | none | n/a | on | OFF (secure) |
| lab-infra-n8n | private | read | selected | none | n/a | on | OFF (secure) |
| lab-lms | private | read | selected | none | n/a | on | OFF (secure) |
| lab-public | public | read | selected | yes | enabled | on | OFF (secure) |
| lab-skills-private | private | read | selected | none | n/a | on | OFF (secure) |
| obsidian-vault | private | read | selected | none | n/a | on | OFF (secure) |
| private-members | private | read | selected | none | n/a | on | OFF (secure) |
| public-docs | public | read | selected | yes | enabled | on | OFF (secure) |
| thinkyou0714 | public | read | selected | yes | enabled | on | OFF (secure) |
| tyl-monorepo | private | read | selected | none | n/a | on | OFF (secure) |
| zenn-content | public | read | selected | yes | enabled | on | OFF (secure) |

## Notes
- Branch protection shows `none` on private repos: GitHub free tier cannot enforce it (Pro required). Compensating controls: squash-only + `delete_branch_on_merge` enforced via repo settings, required status checks where present, PR self-approve OFF.
- Re-run: `bash ~/.claude/scripts/gh_repo_security_audit.sh` + `bash ~/.claude/scripts/gh_actions_pr_perm_audit.sh`. The `.github` `weekly-governance-audit` also covers this on a schedule.