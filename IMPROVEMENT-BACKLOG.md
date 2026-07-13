# THINK YOU LAB — GitHub Improvement Backlog

> Scored backlog from the 2026-06-07 consolidation audit (a 42-agent analysis workflow over all 26 repos = active 21 + archived 5 + best-practice research).
> 95 de-duplicated ideas across 5 domains. ⚡ = quick win (high impact / low effort / low risk).
> ⚠️ 2026-06 パスの項目のうち、旧 archived 5 repo（lab-os / skills-registry / obsidian-knowledge-ops / n8n-gmail-vault / lab-n8n-workflows）を対象とするもの（tombstone banner / AGENTS freeze marker / topics 除去 / branch policy 等）は **2026-06-07 の repo 削除により実行不能 (obsolete)**。lab-os / skills-registry は 2026-07 に同名の**別 repo**として再作成されている点に注意。
> **Verdict of the audit: the account is already well-factored — 0 merges / 0 deletions warranted. The value is hygiene, governance, and verification.**

## ✅ Done in the 2026-06-07 pass

- Refreshed CONVENTIONS.md group classification to 21 active / 5 archived (post-mother-cleanup)
- Corrected archive-lineage table (added lab-n8n-workflows, fixed n8n-gmail-vault successor)
- Added extraction-lineage section (6 mother-cleanup splits) + claude-/codex- prefix exception
- Pruned 123 abandoned agent branches (codex/*, claude/* with no open PR) — restore manifest saved
- Enforced squash-only + delete_branch_on_merge across all repos (free settings API)
- Added scheduled account-wide stale-branch GC workflow to .github (schedule + manual apply; NOT a reusable workflow — cross-repo sweeper に per-repo 呼び出しは不要)
- Fixed private-members README (lab-os/secrets → claude-lab-config)
- Fixed public-docs README (master → main)
- Added lab-infra README extraction callout (post-mother-cleanup reality)
- Published .github/ARCHITECTURE.md repo-map + machine-readable repos.json SSOT
- Ran account-wide security audits (gh-repo-security-audit + gh-pr-perm-audit) + committed baseline
- Committed this IMPROVEMENT-BACKLOG.md

## Backlog (by domain, priority-sorted)

### CI/CD & automation

- ⚡ **Self-test the central Renovate preset (.github/default.json) in CI** · P2.2 · risk:low _(.github)_  
  Add a renovate-config-validator job in .github that validates default.json plus a fixture renovate.json extending it. The preset is the single edit point for all 21 repos' dependency policy, so a typo
- ⚡ **Add Renovate-conformance check to governance audit (renovate.json present, dependabot.yml absent)** · P2.2 · risk:low _(.github, ccmux, tyl-monorepo, lab-infra)_  
  CONVENTIONS mandates Renovate-only with central preset extends ['local>thinkyou0714/.github'] and bans version-update dependabot.yml. Add an audit assertion across active repos that renovate.json exis
- ⚡ **Add account-wide default_workflow_permissions=read drift check to security audit** · P2.2 · risk:low _(.github, lab-infra, tyl-monorepo)_  
  Extend the security audit to GET each repo's Actions default_workflow_permissions and flag any that are 'write' (CONVENTIONS requires read). Pair with gh_repo_security_audit.sh so the posture is conti
- ⚡ **Enable helpers:pinGitHubActionDigests in the central Renovate preset** · P2.2 · risk:low _(.github)_  
  github-flow-kit uses helpers:pinGitHubActionDigests as a repo override. Promote SHA-pinning of GitHub Actions to central default.json so every repo pins third-party actions to digests by default, with
- ⚡ **Tag and release the .github reusable workflows so consumers can pin a version** · P1.65 · risk:low _(.github)_  
  Cut versioned releases (e.g. v1) of the reusable CI/dependency-review/secrets-scan workflows so the SHA-pin work has a stable, human-meaningful ref to track. Without a release the only stable handle i
- ⚡ **Make weekly-governance-audit fail loudly when its token under-scopes or sees <21 repos** · P1.65 · risk:low _(.github)_  
  The audit fails if it sees fewer than 21 active repos (permission proxy), but document and verify the failure path: emit a clear 'token scope insufficient' message and open/refresh a tracking issue, s
- ⚡ **Add actionlint to central CI and run it on every repo's workflows** · P1.65 · risk:low _(.github, ccmux, tyl-monorepo, lab-lms)_  
  github-flow-kit already runs actionlint; lift it into the .github reusable CI so all 21 repos lint workflow YAML on PR. Cheap; catches syntax/permission/expression mistakes the Dangerous-Workflow and 
- ⚡ **Lint that required-check workflows include 'main' in branch triggers** · P1.65 · risk:low _(.github, denken-os, zenn-content, ccmux)_  
  CONVENTIONS warns renaming a repo with required checks can strand workflows whose branches: list omits main. Add a lint that fails if any workflow gating a required check lacks 'main' in its push/pull
- **Pin reusable-workflow refs to SHA/release tag instead of @main** · P1.1 · risk:low _(lab-apps-internal, lab-skills-private, .github)_  
  Repos consuming thinkyou0714/.github reusable workflows (CI/dependency-review/secrets-scan) should reference them by immutable SHA or versioned tag, not @main, so an in-flight edit can't break every c
- **Adopt the lab-infra-n8n validate_workflows.py guardrail as a reusable n8n-lint workflow** · P1.1 · risk:low _(lab-infra-n8n, lab-inbox-bot, tyl-monorepo)_  
  lab-infra-n8n has validate_workflows.py + n8n_git_lint_autofix.py as its CI guardrail. Promote the validation step into a shared reusable workflow so any repo carrying n8n JSON (lab-inbox-bot, tyl-mon
- **Standardize CodeQL across all code-bearing public repos** · P1.1 · risk:low _(ccmux, denken-os, public-docs, claude-lab-skills)_  
  ccmux ships a CodeQL badge but other public TS/Python repos (denken-os, public-docs, claude-lab-skills, github-flow-kit, codex-toolkit) should run the same CodeQL reusable workflow so the 'required st
- **Build a reusable release-notes workflow from the github-flow-kit release-notes skill** · P1.1 · risk:low _(github-flow-kit, ccmux, codex-toolkit, denken-os)_  
  The release-notes/codex-changelog skills run interactively. Wrap them in a tag-triggered reusable workflow that drafts a GitHub Release + CHANGELOG entry on new tags so flagship OSS repos get consiste
- **Add a release gate that blocks tags failing required status checks** · P1.1 · risk:low _(github-flow-kit, ccmux, codex-toolkit)_  
  For flagship OSS repos that publish releases, add a release workflow that proceeds only when CodeQL/ci/Build pass on the tagged commit, so the release artifact is provably tied to green CI rather than
- **Auto-correct public-docs default-branch/visibility metadata drift in the audit** · P1.1 · risk:low _(.github, public-docs)_  
  public-docs README references 'master' while default is 'main', plus a private:true flag on a public repo. Add a metadata-consistency check (default branch matches docs, visibility matches group class

### governance

- ⚡ **Rewrite CONVENTIONS.md archive-lineage table (it is factually wrong)** · P5.5 · risk:low _(.github, lab-n8n-workflows, n8n-gmail-vault, lab-infra-n8n)_  
  The supersession table omits newly-archived lab-n8n-workflows and points n8n-gmail-vault at it (now dead). Re-point n8n-gmail-vault -> lab-infra-n8n (n8n SSOT) + tyl-monorepo (product SSOT), add a lab
- ⚡ **Document the 'claude-' kit-prefix exception in CONVENTIONS naming section** · P3.3 · risk:low _(.github, claude-lab-config, claude-lab-skills)_  
  claude-lab-config and claude-lab-skills use a 'claude-' prefix deviating from lab-/tyl- but accepted as a dev-kit exception (rename cost > benefit). Codify it in the naming section so audits treat it 
- ⚡ **Record the resolved tyl-monorepo vs lab-n8n-workflows duplication in CONVENTIONS** · P3.3 · risk:low _(.github, lab-n8n-workflows, tyl-monorepo)_  
  The one genuine duplication (lab-n8n-workflows was a near-identical fork of tyl-monorepo, resolved by archival 2026-06-01) is captured in the archive description but not the governance SSOT. Add it to
- ⚡ **Refresh CONVENTIONS.md group classification to current 26-repo reality** · P2.75 · risk:low _(.github, lab-infra-n8n, lab-apps-internal, codex-hub)_  
  The group-classification section is pre-mother-cleanup: it lists archived lab-n8n-workflows as infra-private and omits the 6 extracted repos plus the public/private skill split. Add lab-infra-n8n, lab
- ⚡ **Standardize archive tombstone banner across all 5 archived repos** · P2.2 · risk:low _(lab-os, n8n-gmail-vault, skills-registry, lab-n8n-workflows)_  
  Only obsidian-knowledge-ops carries a [!CAUTION] Deprecated banner pointing at its successor. Apply the same top-of-README 'archived → superseded by X' tombstone to lab-os, n8n-gmail-vault, skills-reg
- ⚡ **Make CONVENTIONS/repos.json the single edit point for the active-repo count (21)** · P2.2 · risk:low _(.github)_  
  weekly-governance-audit fails if it sees fewer than 21 active repos, but 21 is a magic number duplicated in CI logic. Pin the expected active-repo list in repos.json/CONVENTIONS and have the audit rea
- ⚡ **Document the 6 'mother cleanup' extractions as a lineage section in CONVENTIONS** · P2.2 · risk:low _(.github, lab-infra, lab-infra-n8n, lab-apps-internal)_  
  The deliberate history-preserved extractions (lab-infra-n8n, lab-apps-internal, codex-hub, lab-lms, lab-skills-private from lab-infra; obsidian-vault) are only described in individual READMEs. Add an 
- ⚡ **Protect main on every repo carrying branch debt before the hygiene pass** · P2.2 · risk:low _(obsidian-vault, lab-infra, tyl-monorepo, ccmux)_  
  Confirm branch protection on main (required status checks, required reviews=0, enforce_admins=false per CONVENTIONS) for all repos being pruned, so a mistaken force-push or branch-delete during the pa
- ⚡ **Document a branch-naming + lifecycle convention in CONVENTIONS.md** · P1.65 · risk:low _(.github, lab-infra)_  
  CONVENTIONS covers default branch, squash-only, delete_on_merge but has no branch-naming or max-age rule. Add a short feature/<slug>, fix/<slug> naming + 'delete within 7d of merge' policy so future b
- ⚡ **Standardize CODEOWNERS across active repos** · P1.65 · risk:low _(.github, ccmux, github-flow-kit, codex-toolkit)_  
  Only zenn-content visibly carries CODEOWNERS. Add a minimal CODEOWNERS (solo: thinkyou0714 global owner) via the .github default or per-repo file so review routing and the enforce_admins=false hotfix 
- ⚡ **Add per-archived-repo AGENTS/CLAUDE freeze marker to prevent agent edits** · P1.65 · risk:low _(lab-os, n8n-gmail-vault, skills-registry, lab-n8n-workflows)_  
  lab-infra has a repo-local AGENTS rule excluding it from mutable audit failures. Apply an analogous 'archived: do not edit, use successor' marker (AGENTS.md/CLAUDE.md stub) to the 5 archived repos so 
- ⚡ **Document the obsidian-templates dual-maintenance boundary as a governed one-way mirror** · P1.65 · risk:low _(.github, private-members, public-docs)_  
  public-docs and private-members both ship Obsidian templates (public reference vs private canonical). Record in CONVENTIONS that private-members is canonical and public-docs receives a build-time copy
- **Adopt GitHub repository rulesets to enforce squash-only + delete_branch_on_merge** · P1.5 · risk:med _(.github, lab-infra, tyl-monorepo, ccmux)_  
  CONVENTIONS mandates squash-only and delete_branch_on_merge but these are per-repo UI toggles. Define a ruleset (or a documented gh api apply script in .github) enforcing the merge policy declarativel
- **Add a machine-readable repos.json manifest in .github as governance SSOT** · P1.47 · risk:low _(.github)_  
  Group classification, archive lineage, and the 21-active count live only as prose tables. Emit a structured repos.json (name, visibility, group, status, superseded_by) so weekly-governance-audit, CONV
- **Add a scheduled stale-branch report to weekly-governance-audit** · P1.47 · risk:low _(.github)_  
  Extend the weekly audit to emit a per-repo stale-branch count (branches merged or older than N days, excluding main, excluding obsidian-vault sync churn by pattern) so branch debt is surfaced continuo
- **Add a CONVENTIONS rule + audit check banning active→archived cross-references** · P1.47 · risk:low _(.github)_  
  Two stale-pointer bugs (private-members→lab-os, supersession-table→lab-n8n-workflows) share a root cause: nothing forbids active repos or governance docs from linking archived ones. Add a CONVENTIONS 
- **Add CONVENTIONS conformance to the weekly-governance-audit checklist** · P1.1 · risk:low _(.github)_  
  The audit checks Dependabot, hardening, and branch protection but not CONVENTIONS-declared facts (squash-only, delete_branch_on_merge, default branch=main, license type). Extend it to assert these per
- **Encode lab-infra as an allowlisted read-only-audit repo in audit config** · P1.1 · risk:low _(.github, lab-infra)_  
  CONVENTIONS states lab-infra is Codex-change-forbidden (audited but excluded from mutable failure). Encode this explicitly in the audit config so future automated remediation jobs (branch prune, setti
- **Add a homepage-field policy and audit for content/docs repos** · P1.1 · risk:low _(.github, lab-public, thinkyou0714, public-docs)_  
  Metadata rules forbid homepage = own GitHub URL, but thinkyou0714 profile and lab-public README link homepage as github.com/thinkyou0714. Document the deployed-URL-or-empty expectation per content/doc
- **Consolidate CI into reusable workflows hosted in .github** · P0.9 · risk:med _(.github, ccmux, github-flow-kit, codex-toolkit)_  
  lab-apps-internal and lab-skills-private already pull reusable CI (CI/dependency-review/secrets-scan) from .github, but flagship-OSS repos (ccmux, github-flow-kit, codex-toolkit, denken-os) carry thei

### metadata & READMEs

- ⚡ **Standardize 6 pinned repos to the flagship-OSS set** · P4.4 · risk:low _(thinkyou0714, ccmux, github-flow-kit, codex-toolkit)_  
  Pin the four flagship-OSS repos (ccmux, github-flow-kit, codex-toolkit, denken-os) plus claude-lab-skills and public-docs so the profile's top-6 pins match the CONVENTIONS group classification rather 
- ⚡ **Fix claude-lab-skills README title + name drift + skill count** · P2.2 · risk:low _(claude-lab-skills)_  
  README H1 reads '# lab-skills' while the repo is claude-lab-skills, pyproject self-identifies as 'lab-skills', and the description's skill count (40/41) mismatches the actual pack count. Reconcile H1,
- ⚡ **Fix private-members README stale pointers (archived lab-os + raw Vercel URL)** · P2.2 · risk:low _(private-members, claude-lab-config)_  
  private-members README references archived lab-os/secrets/ for config and links the public site via the raw 'public-docs-phi.vercel.app' preview URL. Re-point config refs to claude-lab-config (the doc
- ⚡ **Refresh profile README 'Reach' line + pinned-repo coverage** · P2.2 · risk:low _(thinkyou0714, zenn-content)_  
  thinkyou0714 profile README says 'Zenn: 順次公開予定' although zenn-content already ships 3 published articles, and 'Currently working on' omits flagship OSS codex-toolkit and claude-lab-skills. Update the 
- **Cross-link the public/private skill split in both skill READMEs** · P2.2 · risk:low _(claude-lab-skills, lab-skills-private)_  
  claude-lab-skills (public, tech-agnostic) and lab-skills-private (business-sensitive) are a deliberate split; lab-skills-private points to the public one but the public README doesn't point back. Add 
- ⚡ **Replace raw Vercel preview URL with a stable homepage everywhere** · P1.65 · risk:low _(public-docs, private-members)_  
  public-docs and private-members both surface 'public-docs-phi.vercel.app' (an auto-generated preview hostname) as canonical. Set a stable production domain (or document the canonical Vercel alias) and
- ⚡ **Add CI/license/release badge rows to bare flagship READMEs** · P1.65 · risk:low _(codex-toolkit, codex-hub, denken-os)_  
  ccmux, github-flow-kit, claude-lab-skills, zenn-content have badge rows; codex-toolkit, codex-hub, denken-os do not. Add a consistent badge block (CI status, License, release where applicable) so the 
- ⚡ **Normalize topics across active repos to ≥3 and a shared vocabulary** · P1.65 · risk:low _(private-members, obsidian-vault, thinkyou0714, lab-public)_  
  CONVENTIONS requires topics≥3, but private-members and obsidian-vault carry only 3 generic ones and several repos drift between 'solo-dev'/'solo-developer'. Define a canonical topic vocabulary and bri
- ⚡ **Add uniform 'Where this came from' lineage block to extracted repos** · P1.65 · risk:low _(codex-hub, lab-apps-internal, lab-infra-n8n, lab-lms)_  
  The mother-cleanup extractions (codex-hub, lab-apps-internal, lab-infra-n8n, lab-lms, lab-skills-private) have varying tombstone quality. Add a uniform short lineage note (extracted from lab-infra/<pa
- **Generate REPO_TOUR.md for the large monorepos** · P1.47 · risk:low _(tyl-monorepo, lab-infra, lab-apps-internal)_  
  Only codex-hub references a REPO_TOUR.md. tyl-monorepo (1669 files), lab-infra (2130 files), and lab-apps-internal (191 files, 5 packages) are hardest to navigate; produce a REPO_TOUR with annotated t
- **Reconcile tyl-monorepo README with its actual identity** · P1.47 · risk:low _(tyl-monorepo)_  
  tyl-monorepo's README is generic 'THINK YOU LAB / Self-Evolving Automation Platform' boilerplate (nearly identical to archived lab-n8n-workflows) and its Structure section still reads cursor-spec-firs
- **Reconcile public-docs metadata: default branch master→main and private flag** · P1.35 · risk:med _(public-docs)_  
  public-docs is public yet shows default branch 'master' (CONVENTIONS mandates main) and an inconsistent private:true signal. Rename default branch to main (updating workflow branches: triggers and any
- **Add social-preview PNGs to flagship + content public repos** · P1.1 · risk:low _(ccmux, github-flow-kit, codex-toolkit, denken-os)_  
  CONVENTIONS mandates a 1280x640 social preview but no public repo appears to have one. Generate and upload previews (web UI) for ccmux, github-flow-kit, codex-toolkit, denken-os, claude-lab-skills, pu
- **Strip/neutralize topics on archived repos** · P1.1 · risk:low _(lab-n8n-workflows, lab-os, obsidian-knowledge-ops, n8n-gmail-vault)_  
  Archived repos still surface topics in search and account listings; lab-n8n-workflows, lab-os, obsidian-knowledge-ops, n8n-gmail-vault, skills-registry should have minimal topics (or an 'archived' mar
- **Establish CHANGELOG + Releases discipline for flagship OSS** · P1.1 · risk:low _(ccmux, codex-toolkit, denken-os, claude-lab-skills)_  
  github-flow-kit has a release badge but ccmux, codex-toolkit, denken-os, claude-lab-skills lack visible CHANGELOG/Releases. Add a Keep-a-Changelog CHANGELOG.md and cut a baseline GitHub Release so con
- **Add an English README to JP-primary flagship repos** · P1.1 · risk:low _(denken-os, codex-hub)_  
  claude-lab-skills ships README.en.md; denken-os and codex-hub are JP-primary with no English entry point despite being public/OSS-positioned. Add a concise README.en.md (or bilingual header) to widen 
- **Add a Quick Start / usage block to policy-oriented READMEs** · P1.1 · risk:low _(public-docs, lab-public, obsidian-vault)_  
  ccmux, codex-toolkit, codex-hub, lab-lms have runnable quick-starts; obsidian-vault, lab-public, public-docs READMEs are policy/structure-oriented without a 'how do I use this' entry. Add a short usag
- **Add clear deprecation README to topic-less archived repos** · P1.1 · risk:low _(skills-registry, n8n-gmail-vault, lab-os, lab-n8n-workflows)_  
  skills-registry has no description and obsidian-knowledge-ops/n8n-gmail-vault are archived; ensure each archived repo's README opens with a clear deprecation callout + 'superseded by' link (obsidian-k

### repo consolidation & structure

- ⚡ **Byte-diff a sample SKILL.md across claude-lab-skills vs lab-skills-private** · P4.4 · risk:low _(claude-lab-skills, lab-skills-private)_  
  Pick one same-named SKILL.md present in both the public claude-lab-skills and private lab-skills-private and byte-diff it to confirm the public/private split is a clean extraction (no accidental same 
- ⚡ **Diagnose obsidian-vault's 81 branches before any bulk delete** · P2.75 · risk:low _(obsidian-vault)_  
  81 branches are almost certainly obsidian-git auto-sync per-conflict/per-device artifacts. Enumerate them (git branch -r --merged main vs --no-merged, with last-commit dates) to confirm they're merged
- ⚡ **Bulk-prune merged sync branches in obsidian-vault** · P2.75 · risk:low _(obsidian-vault)_  
  After diagnosis confirms merged-into-main, delete the merged-only branches (keep main + genuinely unmerged work), then watch for re-accumulation. Reversible via reflog/SHA for already-merged refs.
- **Sweep low-count repos to clean main-only state** · P2.2 · risk:low _(codex-toolkit, .github, lab-lms)_  
  codex-toolkit (3), .github (3), lab-lms (3) sit at 2-3 branches; delete the 1-2 merged extras each to reach main-only, demonstrating the convention end-to-end on small repos before tackling the big on
- **Investigate the 7 branches on the thinkyou0714 profile repo** · P2.2 · risk:low _(thinkyou0714)_  
  The special README profile repo (10 files) shouldn't need 7 branches — likely github-metrics.svg auto-commit branches or abandoned edits. Enumerate and collapse to main so the public-facing account re
- ⚡ **Verify codex-hub package isn't duplicated inside lab-apps-internal** · P2.2 · risk:low _(codex-hub, lab-apps-internal, lab-infra)_  
  codex-hub was extracted from lab-infra apps/codex-hub; lab-apps-internal holds autoclaw/labctl/etc. also from lab-infra/apps. Confirm codex-hub's package isn't also vendored in lab-apps-internal (two 
- ⚡ **Collapse intra-repo duplicate WF-01 JSON in lab-inbox-bot, reference lab-infra-n8n SSOT** · P2.2 · risk:low _(lab-inbox-bot, lab-infra-n8n)_  
  lab-inbox-bot carries the same WF-01 workflow JSON in two paths. Delete one copy and make the remaining one reference (or CI-fetch from) the lab-infra-n8n canonical workflow instead of vendoring, plus
- ⚡ **Add tombstone in lab-infra for the extracted n8n-unified/ path now in lab-infra-n8n** · P2.2 · risk:low _(lab-infra, lab-infra-n8n)_  
  lab-infra-n8n's README notes the sync loop was 'stranded in the upstream lab-infra monorepo pointing at a path that moved here.' Drop a tombstone/README stub at lab-infra's old n8n-unified/ location p
- ⚡ **Add a single ARCHITECTURE/repo-map doc enumerating repos and their boundaries** · P2.2 · risk:low _(.github, lab-infra, thinkyou0714)_  
  No top-level map of which repo owns what (product=tyl-monorepo, workflows=lab-infra-n8n, public skills=claude-lab-skills, private skills=lab-skills-private, infra=lab-infra). Publish one repo-map (in 
- **Confirm intent of 112d-idle lab-public (refresh README or mark archive candidate)** · P2.2 · risk:low _(lab-public)_  
  lab-public is the only active repo idle 112d+ with no content duplication. Decide explicitly whether it stays an active public-experiments surface or becomes a future archive candidate; if kept, add a
- **Document git gc/repack stance for heavy-history repos post-prune** · P2.2 · risk:low _(obsidian-vault, lab-infra, tyl-monorepo)_  
  obsidian-vault holds ~286 MiB of old plugin binaries (accepted) and lab-infra/tyl/lab-n8n-workflows are 30+ GB-class. Document that branch deletion alone doesn't shrink history and that repacking/hist
- **Audit all six lab-infra extractions for leftover source files** · P1.83 · risk:low _(lab-infra, codex-hub, lab-apps-internal, lab-lms)_  
  The mother cleanup extracted codex-hub, lab-apps-internal, lab-lms, lab-infra-n8n, lab-skills-private (history preserved). Grep lab-infra for original apps/codex-hub, apps/, lms/, n8n-unified/, lab-sk
- **Verify no branch carries unpushed unique work before deletion (safety gate)** · P1.8 · risk:med _(lab-infra, tyl-monorepo, ccmux, obsidian-vault)_  
  For any branch flagged --no-merged, confirm via the inventory whether its tip is reachable from main or another branch; only delete branches whose unique commits are zero or captured elsewhere, record
- ⚡ **Update lab-infra description/README to post-extraction reality** · P1.65 · risk:low _(lab-infra)_  
  lab-infra's description still lists ccmux, autoclaw, codex-hub, labctl as its contents, but those moved to public ccmux + lab-apps-internal + codex-hub. Rewrite it to reflect the infra shell (not the 
- **Fix obsidian-git config to stop spawning auto-sync branches** · P1.5 · risk:med _(obsidian-vault)_  
  Root cause of the 81-branch problem is obsidian-git's sync/conflict behavior creating branches. Set it to commit-and-push on a single branch (disable conflict-branch creation / pull-then-push on main)
- **Verify tyl-monorepo lab/ and lab-infra-n8n don't both carry live n8n workflow JSON** · P1.47 · risk:low _(tyl-monorepo, lab-infra-n8n)_  
  tyl-monorepo's lab/ dir lists 'n8n 本番ワークフロー (WF-xx)' while lab-infra-n8n is the declared SSOT (491 JSON). Confirm tyl-monorepo's lab/ isn't a live second copy; if it is, collapse it to reference lab-i
- **Build a read-only cross-repo branch inventory script (squash-aware)** · P1.2 · risk:med _(.github, claude-lab-config)_  
  gh-API script (sibling to gh_repo_security_audit.sh) listing every branch across 21 active repos with merged-status, last-commit date, ahead/behind main, and associated open PR. Must detect 'content l
- **Triage lab-infra's 51 branches read-only (AGENTS-protected, no auto-delete)** · P1.2 · risk:med _(lab-infra, codex-hub, lab-apps-internal, lab-infra-n8n)_  
  lab-infra is the intentional everything-monorepo whose repo-local AGENTS forbids Codex changes and is excluded from mutable audit failures. Produce a read-only inventory (merged vs unmerged, author, a
- **Prune merged feature branches on heavy active repos (tyl/ccmux/denken-os)** · P1.2 · risk:med _(tyl-monorepo, ccmux, denken-os)_  
  After delete_branch_on_merge is on, sweep merged/abandoned branches: tyl-monorepo (12), ccmux (9, mapped to its 15 open issues), denken-os (8, pre-alpha auto-deploys main). Compare by content/PR state
- **Decide branch policy for ARCHIVED lab-n8n-workflows (20 branches)** · P1.1 · risk:low _(lab-n8n-workflows)_  
  Archived repos are read-only so its 20 branches can't be deleted while archived. Either accept them as frozen (document it) or briefly unarchive to prune then re-archive. Recommend frozen+documented u
- **One-time PR-cleanup pass: drive stale PRs to a terminal state** · P1.1 · risk:low _(tyl-monorepo, ccmux, lab-lms, codex-hub)_  
  Stale branches often persist because PRs are neither merged nor closed. Triage open PRs on tyl-monorepo, ccmux, lab-lms, codex-hub, claude-lab-config to merged/closed so delete_branch_on_merge then cl
- **Resolve obsidian-templates triple-maintenance via build-time copy from canonical** · P0.9 · risk:med _(private-members, public-docs)_  
  Obsidian templates are hand-synced across private-members (canonical), public-docs (reference), and archived obsidian-knowledge-ops. Designate private-members canonical and generate the public-docs co

### security-secrets

- ⚡ **Run account-wide gh_repo_security_audit and commit a dated baseline** · P5.5 · risk:low _(all-active, .github)_  
  CONVENTIONS asserts a full security posture but recon never fetched per-repo settings (branches.txt/tree.txt empty for all 25 repos), so policy is unverified. Run read-only gh_repo_security_audit.sh a
- ⚡ **Verify can_approve_pull_request_reviews=false across all repos and wire into weekly audit** · P4.4 · risk:low _(.github, all-active)_  
  CONVENTIONS L33 requires Actions PR self-approval off; with required-review=0 for solo ops, self-approval is the only remaining gate. Run gh_actions_pr_perm_audit.sh across 21 repos and wire it (audit
- **Verify and enforce default_workflow_permissions=read on all repos with Actions** · P2.75 · risk:low _(ccmux, github-flow-kit, codex-toolkit, claude-lab-skills)_  
  CONVENTIONS L32 mandates read-only GITHUB_TOKEN but no repo's actual setting was confirmed. GET each repo's Actions default token permission, flip any 'write' to 'read', declare per-job write where ge
- **Confirm secret scanning + push protection on every public repo (enable where off)** · P2.75 · risk:low _(ccmux, codex-toolkit, github-flow-kit, claude-lab-skills)_  
  CONVENTIONS L34 requires secret scanning + push protection on public repos but the flag was never verified. Public repos ship installable code and example configs — the prime leak surface. Verify via 
- ⚡ **Roll SHA-pinning of GitHub Actions to all repos via central preset** · P2.2 · risk:low _(.github, ccmux, denken-os, tyl-monorepo)_  
  Only github-flow-kit uses helpers:pinGitHubActionDigests; ~19 repos reference Actions by mutable tag (force-move supply-chain risk). Add pinGitHubActionDigests to central .github/default.json so every
- ⚡ **Confirm fail-closed .gitignore allowlist holds across dotfile/config repos** · P2.2 · risk:low _(claude-lab-config, obsidian-vault, lab-skills-private)_  
  claude-lab-config uses an allowlist .gitignore (everything ignored, only safe paths un-ignored) to structurally prevent secret commits. Verify zero committed files match secrets/ certs/ *.key *.pem *.
- ⚡ **Audit Dangerous-Workflow triggers (pull_request_target / workflow_run) across repos** · P2.2 · risk:low _(denken-os, tyl-monorepo, lab-infra, ccmux)_  
  pull_request_target and workflow_run workflows that checkout PR head are an RCE surface (untrusted fork code with secret/write access). The account runs CodeQL, Renovate, zenn auto-publish, deploy-pag
- **Add SECURITY.md disclosure path; verify .github fallback resolves** · P2.2 · risk:low _(.github, ccmux, github-flow-kit, codex-toolkit)_  
  The .github repo provides a fallback SECURITY.md; confirm it resolves to a monitored contact and add repo-local SECURITY.md to the highest-reach public flagships so responsible disclosure works for th
- **Scan n8n workflow JSON for embedded credentials and hardcoded webhook secrets** · P1.83 · risk:low _(lab-infra-n8n, n8n-gmail-vault)_  
  lab-infra-n8n carries 491 workflow JSON (plus archived n8n-gmail-vault). Exported n8n workflows frequently embed credential refs, API keys in HTTP/Set nodes, and webhook paths. Add an n8n-specific sca
- **Scope down and set rotation for ORG_GOVERNANCE_AUDIT_TOKEN** · P1.8 · risk:med _(.github)_  
  weekly-governance-audit uses a PAT with org-wide read — a high-value target. Replace the classic PAT with a fine-grained PAT scoped to metadata+administration:read on only the audited repos, set expli
- ⚡ **Harden lab-inbox-bot Slack token handling and pin minimum scopes** · P1.65 · risk:low _(lab-inbox-bot)_  
  lab-inbox-bot runs Slack Socket Mode with xapp-/xoxb- tokens plus OpenAI/Anthropic keys and an optional n8n webhook. Verify tokens come only from env (no committed .env), authenticate the n8n webhook 
- ⚡ **Scan public installable repos for example configs leaking real values** · P1.65 · risk:low _(ccmux, codex-toolkit, github-flow-kit, claude-lab-skills)_  
  ccmux, codex-toolkit, github-flow-kit, claude-lab-skills, public-docs ship installers and example configs (config.json, config.toml.example, env.sh, .env.example). Verify every template has only dummy
- ⚡ **Verify archived repos' secret hygiene and live-wiring before they're forgotten** · P1.65 · risk:low _(lab-n8n-workflows, n8n-gmail-vault, lab-os, obsidian-knowledge-ops)_  
  Five archived private repos (lab-n8n-workflows, obsidian-knowledge-ops, n8n-gmail-vault, lab-os, skills-registry) retain secrets-era history; n8n-gmail-vault handled Gmail OAuth. Confirm any credentia
- **Enforce webhook authentication on n8n workflow webhook nodes** · P1.5 · risk:med _(lab-infra-n8n)_  
  Many lab-infra-n8n automations (embed-engine, inbox-classifier, vault-triage) are webhook-triggered. Add a CI lint that fails any webhook-trigger node lacking header/HMAC auth or an allowlist, so no u
- **Audit Stripe webhook signature verification and key segregation in lab-lms** · P1.5 · risk:med _(lab-lms)_  
  lab-lms (Next.js + Supabase + Stripe + Resend + Upstash + Sentry) ships a Stripe webhook. Verify Stripe-Signature enforcement, restricted Stripe key usage, Supabase service-role keys kept server-only 
- **Standardize a gitleaks CI gate via the central reusable workflow** · P1.47 · risk:low _(.github, lab-infra, lab-apps-internal, lab-skills-private)_  
  lab-infra PR #283 hardens gitleaks; lab-apps-internal/lab-skills-private reference a 'secrets-scan' reusable workflow from .github. Promote one canonical gitleaks reusable workflow and wire every acti
- **Make weekly-governance-audit assert SHA-pinning, secret-scanning, and PR-approve toggle** · P1.47 · risk:low _(.github)_  
  The audit lists repos and checks Dependabot/hardening/branch-protection but doesn't assert (a) Actions SHA-pinned, (b) secret scanning + push protection on for public repos, (c) no off-allowlist can_a
- **Enable secret scanning on private repos that handle live credentials** · P1.47 · risk:low _(lab-lms, lab-inbox-bot, codex-hub, lab-apps-internal)_  
  Private repos lack free public scanning yet hold real secrets: lab-lms (Stripe/Supabase/Resend/Upstash/Sentry/Slack), lab-inbox-bot (Slack xapp-/xoxb-, OpenAI, Anthropic), codex-hub, lab-apps-internal
- **Audit and rotate ANTHROPIC_API_KEY across all consumers, standardize one secret name** · P1.2 · risk:med _(denken-os, lab-inbox-bot, lab-lms, lab-apps-internal)_  
  @anthropic-ai/sdk is used in denken-os, lab-inbox-bot, lab-lms, plus autoclaw and codex-hub — 5+ places the same key likely lives. Inventory every usage, rotate once, standardize on one secret name, d
- **Finish codex-hub CSP + rate-limit hardening; verify its local API surface** · P1.2 · risk:med _(codex-hub)_  
  codex-hub PR #11 (strict-nonce CSP + observability + rate limiting) is an open draft. codex-hub exposes a Next.js UI and HTTP API surfaced as MCP tools (hub_vault_write) that write to the Obsidian vau
- **Audit obsidian-vault history for committed secret-residue (rotate if found)** · P0.68 · risk:med _(obsidian-vault)_  
  obsidian-vault retains ~286 MiB of historical plugin binaries and is an auto-synced working tree where stale credentials/state could be buried. Audit history for any committed *.env / *auth*.json / to

---

# 2026-07 addendum — Claude Code **web-readiness** + follow-through

> New axis not covered by the 2026-06-07 pass: making repos usable from **Claude Code on the web**
> (ephemeral Ubuntu cloud sessions). Verified against the official web docs. ⚡ = quick win.
> Total itemized ideas across both passes: **95 + 25 = 120**（2026-07-13 訂正: 旧記載の「33」は実項目数 25 と不一致だった — Web-readiness 12 + Branch protection 3 + Docs/LICENSE/CI 5 + Local↔remote 5）。

## ✅ Done in the 2026-07 pass
- Published `AUDIT-2026-07.md` — /100 scorecard for all 27 repos + the web MCP/SKILL/CLI verdict + local↔remote consistency reconciliation.
- Published `docs/claude-code-web-readiness.md` — the SSOT web-ready template (SessionStart bootstrap hook, HTTP/SSE-only `.mcp.json`, skills, AGENTS.md).
- Applied the web-readiness template to **all 14 code repos** via per-repo PRs (CI green): PUBLIC — fugu #28, denken-os #54, engineer-tenshoku-navi #3 (+MIT LICENSE), claude-lab-skills #14, github-flow-kit #28, codex-toolkit #12, agmsg-kit #2, ccmux #86, agmsg #2; PRIVATE — tyl-monorepo #95, lab-lms #53, lab-apps-internal #66, lab-inbox-bot #22, codex-hub #50.
- Refreshed the account profile README (thinkyou0714 #17): skill count 4→6, added fugu/codex-toolkit/claude-lab-skills, Zenn published.
- Extended web-readiness to **all remaining repos** (per-fire, CI green): public-docs #17, zenn-content #13, lab-public #21, lab-infra-n8n #50, skills-registry #1 (**+new validate CI**), lab-research #2 (**+new validate CI**), lab-skills-private #8, private-members #14. skills-registry + lab-research previously had **no CI** — now gated by a non-fragile JSON/YAML data-integrity check.
- **Total this pass: 24 PRs** (audit #12 + profile #17 + 22 web-readiness repos). Every repo is addressed **except 3 with clear rationale**: lab-infra (audit-only / Codex-change-forbidden), claude-lab-config + obsidian-vault (HOT — actively edited). External forks (onyx, supabase-grafana) are out of scope.
- **Deferred (needs a decision or paid plan)**: branch protection on the 8 private repos (GitHub Pro); lab-inbox-bot's `npm audit` (form-data high) → Renovate; lab-infra hook/MCP の POSIX 化 + web-port（large, audit-only repo）; stale-branch GC の apply 実行（workflow は存在、対象ブランチ群への適用が未了）; local dirty-tree reconciliation (owner-gated).
- Added MIT LICENSE to `engineer-tenshoku-navi` (only public repo missing one).
- Enabled light solo-friendly branch protection on **all 14 public repos** (linear history, block force-push/deletion, strict status checks, self-merge allowed). Private repos (8) require GitHub Pro — deferred.

## Web-readiness (Claude Code on the web)

- ⚡ **Commit a POSIX SessionStart bootstrap hook to every code repo** · P0.9 · risk:low _(fugu, ccmux, denken-os, tyl-monorepo, lab-lms)_
  `.claude/settings.json` -> `.claude/bootstrap.sh` that `npm ci`/`uv sync` idempotently so a cloud session has repo deps without manual setup. No powershell/`C:\`.
- ⚡ **Add a root `AGENTS.md` to every public repo** · P0.9 · risk:low _(denken-os, engineer-tenshoku-navi, codex-toolkit, public-docs, lab-public)_
  Cloud sessions load root `AGENTS.md`/`CLAUDE.md`; 22/27 repos have neither. One paragraph of what/why + setup/test/build commands.
- ⚡ **Commit 1-2 repo-relevant skills to flagship OSS** · P1.1 · risk:low _(fugu, ccmux, codex-toolkit, github-flow-kit, denken-os)_
  `.claude/skills/{run-tests,release}/SKILL.md` travel to web; only tyl-monorepo (14) + fugu (1) have any. Keep them repo-specific, not a global-kit copy.
- **Strip lab-infra `.mcp.json` of localhost/Windows/stdio servers for a web profile** · P1.5 · risk:med _(lab-infra)_
  All 11 servers (obsidian:27124, n8n:5679, autoclaw:3101, codex-hub:3500, lab_index Windows path) break on web. Split a committed HTTP/SSE-only `.mcp.json` from the local-only set.
- **Port lab-infra 106 hooks off powershell/`C:\` to POSIX + `$CLAUDE_PROJECT_DIR`** · P1.2 · risk:med _(lab-infra, tyl-monorepo)_
  Repo-committed settings.json hooks run in the Linux cloud container; Windows shell/paths fail. Guard local-only steps with an OS/`CLAUDE_CODE_REMOTE` check.
- ⚡ **Document GitHub-hosted MCP as the opt-in web MCP pattern (no committed PAT)** · P1.65 · risk:low _(.github, ccmux, github-flow-kit)_
  Only HTTP/SSE servers work on web. Provide a copy-paste `.mcp.json` snippet in the web-readiness doc and README; auth via the session GitHub connection, never an inline token.
- **Add a CI lint that rejects non-web-portable `.claude`/`.mcp.json` in public repos** · P1.47 · risk:low _(.github)_
  Reusable workflow asserting no `powershell`/`C:\`/`localhost`/stdio in committed `.claude` + `.mcp.json`, and that `.claude/settings.json`/`.mcp.json` are valid JSON. Prevents web-readiness regressions.
- **Validate committed SKILL.md frontmatter in CI** · P1.47 · risk:low _(.github, claude-lab-skills, fugu)_
  Assert every `.claude/skills/*/SKILL.md` has `name:`+`description:` so web auto-load never silently drops a skill.
- ⚡ **Add a "Using with Claude Code (web)" README section to flagship repos** · P1.65 · risk:low _(fugu, ccmux, denken-os, codex-toolkit)_
  Two lines: deps auto-install via bootstrap hook; which skills ship; MCP is local-only unless a hosted server is configured.
- **Publish the web-readiness template as a reusable, versioned kit** · P1.1 · risk:low _(.github, claude-lab-skills)_
  Ship `bootstrap.sh` + `settings.json` + skill skeletons as a template consumers copy (or a `scaffold` script in .github), so rollout to the remaining 20 repos is mechanical.
- ⚡ **Add `.nvmrc` / pin `engines.node` on Node repos** · P2.2 · risk:low _(fugu, ccmux, denken-os, lab-lms, tyl-monorepo)_
  Cloud has Node 20/21/22; pin the one this repo builds on so bootstrap installs against a deterministic runtime.
- **Cloud-context guard (`CLAUDE_CODE_REMOTE`) for local-only hooks across repos** · P1.5 · risk:med _(lab-infra, tyl-monorepo, ccmux)_
  Any committed hook that pushes/syncs/writes to a local service must no-op in cloud; add the guard as a shared snippet so a web session never fires a machine-local side effect.

## Branch protection & security follow-through (extends 2026-06 security-secrets)

- **Enable light branch protection on all repos with CI** · P0.9 · risk:med _(all-active)_
  `required_linear_history=true`, `allow_force_pushes=false`, `required_status_checks`=CI contexts, `required_pull_request_reviews=null` (self-merge), `enforce_admins=false`. 0/27 protected at audit time. Applied to all 14 public repos this pass; **private repos need GitHub Pro** (free-plan 403) — deferred.
- **Add branch-protection presence to weekly-governance-audit** · P1.47 · risk:low _(.github)_
  Assert every active repo main has the light ruleset; open a tracking issue on drift. Pairs with the existing squash-only/delete-on-merge checks.
- ⚡ **Enable secret scanning + push protection on all public repos, verify the flag** · P1.47 · risk:low _(fugu, ccmux, codex-toolkit, github-flow-kit, claude-lab-skills)_
  Previously flagged unverified; make it an asserted, remediated setting now that the pass touches these repos.

## Docs, LICENSE, CI (extends 2026-06 metadata & CI)

- ⚡ **Add MIT LICENSE to engineer-tenshoku-navi** · P0.9 · risk:low _(engineer-tenshoku-navi)_
  Only public repo with no LICENSE; a public repo with no license is legally "all rights reserved" — contrary to its OSS positioning.
- **Add a proprietary/`UNLICENSED` notice to private product repos** · P1.1 · risk:low _(tyl-monorepo, lab-lms, lab-apps-internal, lab-inbox-bot)_
  Private repos deliberately omit MIT; add an explicit "proprietary, all rights reserved" LICENSE so intent is unambiguous (do NOT auto-MIT private code).
- ⚡ **Add minimal validate CI to the 2 CI-less private stubs** · P1.65 · risk:low _(lab-research, skills-registry)_
  A lint/markdown/link-check workflow (or a documented WIP/archived marker if they are inert) so no active repo is CI-blind.
- ⚡ **Expand the 4 stub READMEs** · P1.65 · risk:low _(lab-public, thinkyou0714, lab-skills-private, obsidian-vault)_
  <2.5K READMEs with no "what/how do I use this"; add purpose + quick-start (obsidian-vault deferred while HOT).
- **Publish `AGENTS.md`/`REPO_TOUR.md` for the big monorepos** · P1.47 · risk:low _(tyl-monorepo, lab-infra, lab-apps-internal)_
  Combine web-readiness AGENTS.md with a repo-tour so both humans and cloud agents can navigate 1600+ file trees.

## Local<->remote consistency (owner-gated — no destructive auto-action)

- **Archive the duplicate `public-docs` clone after unpushed-work check** · P1.1 · risk:med _(public-docs)_
  `/c/work/lab/public-docs` (16 dirty, chore/vinext-check) duplicates canonical `content/public-docs`; verify no unique unpushed commits, then archive the stray.
- **Reconcile the stale `apps/nextjs-boilerplate` clone (repo renamed -> tyl-monorepo)** · P1.1 · risk:low _(tyl-monorepo)_
  4-mo clone of the old repo name; archive and use `apps/tyl-monorepo`.
- **Rescue or discard `lab-os` local (43 dirty + 2 unpushed commits)** · P1.2 · risk:med _(lab-os)_
  旧 lab-os は 2026-06-07 に**削除済**（archived ではない）なので push 先の旧 remote は存在しない。クローンが持つ 2 unpushed commits は data-loss risk — 新 lab-os（2026-07-05 再作成の別 repo）へ移すか discard するか owner 判断。
- **Decide fate of stale `lab-inbox-bot` local edits (5 dirty, 5-mo)** · P1.1 · risk:low _(lab-inbox-bot)_
  Commit or discard; unblocks a clean canonical clone.
- **Clone the 4 uncloned repos into their group dirs when next worked** · P2.2 · risk:low _(lab-apps-internal, agmsg, lab-skills-private, lab-public)_
  No canonical local clone today; note the intended `/c/work/lab/<group>/` path so future work lands consistently.

---

# 2026-07-13 addendum — `.github` repo 深掘り監査（構造・GitHub 機構・整合性）

> `.github` repo 自体を対象に、GitHub 機構の正当性 / 全文書の横断整合性 / workflow・script の精読の
> 3 軸で実施した監査の記録。**修正済み**は同日の PR (repo-structure-best-practices) で着地。
> 併せて `BEST-PRACTICES.md`（個人開発者ベストプラクティス100 + 採用状況）を新設した。

## ✅ Fixed in the 2026-07-13 pass

- **ISSUE_TEMPLATE を root → `.github/ISSUE_TEMPLATE/` へ移動**（default issue templates は `.github/ISSUE_TEMPLATE` 配下必須という公式仕様。root 配置では他 repo への fallback 継承が効かないおそれ）
- **stale-branch-gc の誤削除リスク3件**: open PR 列挙が `gh pr list` の default limit 30 で打ち切られ 31 件目以降の PR の head branch が削除候補になり得た（→ `--paginate` の API 列挙に変更）/ prefixes 入力の空要素が `""*`= 全ブランチ一致になり得た（→ validation 追加）/ 未マージ commit を持つブランチも年齢だけで削除していた（→ `compare` API で ahead_by>0 は自動削除対象外に）
- **stale-branch-gc の fail-open**: `github.token` フォールバック時は private repo が列挙されず削除も全滅するのに黙って不完全レポートになっていた（→ apply=true は PAT 必須で fail-fast、repos.json の active_count との突合 guard 追加）
- **weekly audit が自リポで毎週 FAIL する自己矛盾**: ps1 の concurrency 判定が stale-branch-gc 自身の正当な `cancel-in-progress: false` を弾いていた（→ 判定を「非空 group + 明示的 cancel-in-progress」に緩和）。`permissions: {}` / `read-all` も hardened と認識するよう修正
- **public repo での private 情報露出**: 週次監査の step summary / artifact（誰でも閲覧可）に private repo 名 × open alert 数 × 未 hardening workflow 一覧が出ていた（→ 既定で private 行を1集計行に丸め、`-IncludePrivateDetail` はローカル実行時のみ。artifact `retention-days: 7`）
- **監査 script の測定バグ**: Dependabot alerts が per_page=100 でページネーション無し（→ `--paginate` で合計）/ -1（無効/権限なし）が表で裸のまま（→ `n/a` 表記）/ CODEOWNERS を `.github/` のみ検査（→ root / `docs/` も許容）/ repos.json 読取失敗時に閾値が黙って 21 に落ちる fail-open（→ SSOT 読取失敗は hard error、明示 `-MinimumActiveRepos` のみ override 可）
- **個人アカウントで無効な前提**: dependency-review-action は personal の private repo では動作しない（GHAS 必須）のに監査が全 repo に必須化していた（→ public のみ必須化、CONVENTIONS に明記）
- **scheduled workflow の 60 日自動無効化対策**: weekly-governance-audit に keepalive job（enable API でタイマーリセット）を追加
- **reusable workflow の実体化**: 文書は「reusable CI を参照」と主張していたがどの workflow にも `on: workflow_call` が無かった（→ dependency-review / secrets-scan に `workflow_call` を追加。ci.yml は repo 固有検査のため対象外、stale-branch-gc は呼称を訂正）
- **ARCHITECTURE.md の陳腐化**（21 repo・7 repo 欠落・再作成の未反映）→ repos.json から 28 repo 構成で再生成 + `active_count` マーカーを CI で機械検査
- **ci.yml の検査強化**: 存在チェックのみ → JSON/YAML 構文検証 + repos.json の内部整合（active_count = 配列長等）+ ARCHITECTURE マーカー照合
- **文書間矛盾の解消**: README ライセンス表記（CC0 vs MIT）/ README の repo 役割説明の過少 / CODE_OF_CONDUCT の実在しない「private issue」/ SECURITY.md の文章分断・SLA の節配置 / config.yml と CONTRIBUTING の空振り contact link / security-baseline の branch-prot 列訂正注記 / anthropic-key-rotation の「3 repo とも public」誤記 / claude-code-convention の採用状況日付 / 本文書の「95+33=128」過大計上・Deferred 二重記載・lab-os「archived」誤記 / CONVENTIONS の「21件」ハードコード・グループ分類節の SSOT 自称・pinGitHubActionDigests 陳腐例・automerge 要約の過少記述

### ✅ 追加実装（2026-07-13 follow-up）

- ⚡ **Renovate 中央 preset を CI で self-test**（2026-06 backlog P2.2 消化）: ci.yml「Validate Renovate central preset」step が `renovate-config-validator --strict` で default.json + renovate.json を schema 検証（28 repo に波及する preset の typo を PR で阻止）。ローカルで green 検証済
- ⚡ **actionlint 導入**（2026-06 backlog P1.65 消化）: ci.yml「Lint workflows (actionlint)」step（actionlint@v1.7.12）。ubuntu-latest 同梱 shellcheck により run: ブロックの shell も検査。ローカルで actionlint 1.7.12 + shellcheck 0.11.0 で全 workflow EXIT 0 確認
- ⚡ **内部 Markdown リンク検査**: scripts/check-internal-links.py + ci.yml step で全 .md の内部相対リンク（ファイル/アンカー）の実在を検査（外部 URL liveness は network flaky のため対象外）
- **監査除外リストの SSOT 化**: `$MutableExceptions` の hardcode を廃し、repos.json の `audit_only: true` フラグ（lab-infra）から導出（未指定時のみ historical fallback）。BP-092/BP-097 の残 hardcode を解消
- **versioning 規約の新設**: CONVENTIONS.md「リリース / バージョニング」節（SemVer + annotated tag + Releases + release gate + reusable workflow 版 pin + breaking change 表記）。private product の UNLICENSED 明示もライセンス節へ追記

## Open（今回の監査で新規に判明、未着手）

- ⚡ **本 repo の workflow が digest 未 pin**（tag 参照のまま）。preset の `helpers:pinGitHubActionDigests` により Renovate が pin PR を出すはずだが、この repo で Renovate が実際に動いているか（onboarding 済みか）要確認。動いていなければ手動 pin（他 repo の action SHA 解決が要るためエージェントのスコープ外）
- **fallback ISSUE_TEMPLATE の実地確認**: テンプレを持たない repo の New Issue 画面で `.github/ISSUE_TEMPLATE/` からの継承が効いているか目視確認（移動後の検証）
- **branch protection の真相確認**: security-baseline (2026-06-07)「all public yes」vs AUDIT-2026-07「0/27」の矛盾はどちらかの測定誤り。現況を `gh api` で再検証して正誤を確定
- **lab-research の系譜断絶**: 「recreated」と記録されているが旧 lab-research が削除系譜のどこにも無い。実在したなら系譜表へ追記、純粋な新規なら「newly created」へ訂正（owner 確認）
- **stale-branch-gc / ps1 の API エラー分類**: 403/429/5xx を 404 と区別して retry する堅牢化（現状は握り潰しでスキップ）
- **reusable workflow の versioned release**: 本 PR merge 後に .github へ v1.0.0 annotated tag + Release を切り、consumer repo の `@main` 参照を `@v1`/SHA へ移行（feature branch commit への tag 付けは不適切なため merge 後に実施）
