[CmdletBinding()]
param(
  [string]$Owner = "thinkyou0714",
  [string[]]$MutableExceptions = @("lab-infra"),
  [int]$Limit = 1000,
  # Fallback floor only. When not passed explicitly, the value is ALWAYS replaced by the
  # repos.json (SSOT) active_count; failure to read the SSOT is a hard error (a silent
  # fallback would fail-open the scope check).
  [int]$MinimumActiveRepos = 21,
  [string]$JsonOut = "governance-audit.json",
  [string]$MarkdownOut = "governance-audit.md",
  # This repo (and its workflow summaries/artifacts) is PUBLIC, so private-repo rows are
  # redacted in outputs by default. Pass this switch on local runs for full detail.
  [switch]$IncludePrivateDetail
)

$ErrorActionPreference = "Stop"

function Invoke-GhJson {
  param([string[]]$Arguments)

  $output = & gh @Arguments 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw "gh $($Arguments -join ' ') failed: $output"
  }

  # native stderr lines arrive as ErrorRecord objects via 2>&1 — exclude them from the
  # JSON parse input (gh can print warnings on stderr even when it succeeds)
  $stdout = @($output | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] }) -join "`n"
  if ([string]::IsNullOrWhiteSpace($stdout)) {
    return $null
  }

  return $stdout | ConvertFrom-Json
}

function Try-GhJson {
  param([string[]]$Arguments)

  $output = & gh @Arguments 2>$null
  if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($output)) {
    return $null
  }

  return $output | ConvertFrom-Json
}

function Test-RepoPath {
  param(
    [string]$Repo,
    [string]$Path
  )

  $result = Try-GhJson @("api", "/repos/$Owner/$Repo/contents/$Path")
  return $null -ne $result
}

function Get-RepoDirectory {
  param(
    [string]$Repo,
    [string]$Path
  )

  $result = Try-GhJson @("api", "/repos/$Owner/$Repo/contents/$Path")
  if ($null -eq $result) {
    return @()
  }

  return @($result)
}

function Get-RepoFileText {
  param(
    [string]$Repo,
    [string]$Path
  )

  $result = Try-GhJson @("api", "/repos/$Owner/$Repo/contents/$Path")
  if ($null -eq $result -or [string]::IsNullOrWhiteSpace($result.content)) {
    return $null
  }

  $content = $result.content -replace "\s", ""
  return [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($content))
}

function Get-TopLevelBlock {
  param(
    [string]$Text,
    [string]$Name
  )

  $lines = $Text -split "\r?\n"
  for ($index = 0; $index -lt $lines.Count; $index++) {
    if ($lines[$index] -notmatch "^$([regex]::Escape($Name)):\s*(?:#.*)?$") {
      continue
    }

    $block = @()
    for ($child = $index + 1; $child -lt $lines.Count; $child++) {
      $line = $lines[$child]
      if ($line -match "^#") {
        # column-0 comments do not terminate a YAML block
        continue
      }
      if ($line -match "^\S") {
        break
      }

      $block += $line
    }

    return ($block -join "`n")
  }

  return $null
}

function Test-TopLevelReadPermissions {
  param([string]$Text)

  # inline shorthand forms: `permissions: {}` (all none) and `permissions: read-all`
  if ($Text -match "(?m)^permissions:\s*(\{\}|read-all)\s*(?:#.*)?$") {
    return $true
  }

  $block = Get-TopLevelBlock -Text $Text -Name "permissions"
  if ([string]::IsNullOrWhiteSpace($block)) {
    return $false
  }

  # hardened = at least one explicit entry and no write-level access at the top level
  # (job-level write grants are allowed and reviewed per job)
  $entries = 0
  foreach ($line in ($block -split "\n")) {
    if ($line -notmatch "^\s+([A-Za-z0-9_-]+):\s*([A-Za-z-]+)\s*(?:#.*)?$") {
      continue
    }

    $entries++
    if ($Matches[2] -notin @("read", "none")) {
      return $false
    }
  }

  return $entries -gt 0
}

function Test-TopLevelConcurrency {
  param([string]$Text)

  $block = Get-TopLevelBlock -Text $Text -Name "concurrency"
  if ([string]::IsNullOrWhiteSpace($block)) {
    return $false
  }

  # hardened = any non-empty group + an EXPLICIT cancel-in-progress (true or false).
  # delete/deploy-style jobs (e.g. stale-branch-gc) legitimately use cancel-in-progress: false.
  $hasGroup = $block -match "(?m)^[ \t]*group:\s*\S"
  $hasCancel = $block -match "(?m)^[ \t]*cancel-in-progress:\s*(true|false)\s*(?:#.*)?$"
  return $hasGroup -and $hasCancel
}

function Test-WorkflowHardening {
  param([string]$Text)

  if ([string]::IsNullOrWhiteSpace($Text)) {
    return $false
  }

  return (Test-TopLevelReadPermissions -Text $Text) -and (Test-TopLevelConcurrency -Text $Text)
}

function Test-BranchProtection {
  param(
    [string]$Repo,
    [string]$Branch
  )

  $result = Try-GhJson @("api", "/repos/$Owner/$Repo/branches/$Branch/protection")
  return $null -ne $result
}

function Get-OpenDependabotAlertCount {
  param([string]$Repo)

  # --paginate with a per-page `length` (one number per page). -1 = unknown
  # (alerts disabled or token lacks access) — callers must not treat it as a real count.
  $output = & gh api --paginate "/repos/$Owner/$Repo/dependabot/alerts?state=open&per_page=100" -q 'length' 2>$null
  if ($LASTEXITCODE -ne 0) {
    return -1
  }

  $total = 0
  foreach ($line in @($output)) {
    $trimmed = "$line".Trim()
    if ($trimmed -match '^\d+$') {
      $total += [int]$trimmed
    }
  }

  return $total
}

$repos = Invoke-GhJson @(
  "repo", "list", $Owner,
  "--limit", "$Limit",
  "--json", "name,isArchived,visibility,defaultBranchRef"
)

$activeRepos = @($repos | Where-Object { -not $_.isArchived })
$archivedRepos = @($repos | Where-Object { $_.isArchived })

# Read the repos.json SSOT once (local checkout preferred — correct on PR-dispatched runs —
# then the API copy) and derive both the active-repo floor and the audit-only exception list
# from it, so adding/removing a repo or flipping its audit_only flag is a one-place edit.
$reposJsonText = $null
if (Test-Path -Path "repos.json") {
  $reposJsonText = Get-Content -Path "repos.json" -Raw
} else {
  $reposJsonText = Get-RepoFileText -Repo ".github" -Path "repos.json"
}
$reposSsot = $null
if ($reposJsonText) {
  try {
    $reposSsot = $reposJsonText | ConvertFrom-Json
  } catch {
    $reposSsot = $null
  }
}

# Threshold: an explicit -MinimumActiveRepos always wins; otherwise an unreadable SSOT is a
# hard error instead of silently keeping the stale default (a silent fallback would fail-open
# the scope check).
if (-not $PSBoundParameters.ContainsKey("MinimumActiveRepos")) {
  if ($null -eq $reposSsot -or $null -eq $reposSsot.active_count -or [int]$reposSsot.active_count -le 0) {
    throw "Cannot read active_count from repos.json (SSOT). Pass -MinimumActiveRepos explicitly to override."
  }

  $MinimumActiveRepos = [int]$reposSsot.active_count
}

# Audit-only exceptions (audited but excluded from mutable-failure): read the `audit_only: true`
# flag from repos.json so the exception list is declared in the SSOT, not hard-coded here.
# Fall back to the historical lab-infra exception only if the SSOT is unreadable.
if (-not $PSBoundParameters.ContainsKey("MutableExceptions")) {
  if ($null -ne $reposSsot -and $null -ne $reposSsot.repos) {
    $ssotExceptions = @($reposSsot.repos | Where-Object { $_.audit_only -eq $true } | ForEach-Object { $_.name })
    if ($ssotExceptions.Count -gt 0) {
      $MutableExceptions = $ssotExceptions
    }
  }
}

$scopeFailure = $activeRepos.Count -lt $MinimumActiveRepos
$rows = @()

foreach ($repo in ($activeRepos | Sort-Object name)) {
  $name = $repo.name
  $visibility = $repo.visibility
  $defaultBranch = $repo.defaultBranchRef.name
  $workflows = Get-RepoDirectory -Repo $name -Path ".github/workflows" |
    Where-Object { $_.name -match "\.ya?ml$" }

  $missingHardening = @()
  foreach ($workflow in $workflows) {
    $workflowPath = ".github/workflows/$($workflow.name)"
    $workflowText = Get-RepoFileText -Repo $name -Path $workflowPath
    if (-not (Test-WorkflowHardening -Text $workflowText)) {
      $missingHardening += $workflow.name
    }
  }

  $repoSettings = Try-GhJson @("api", "/repos/$Owner/$name")
  $security = $repoSettings.security_and_analysis

  # GitHub accepts CODEOWNERS in .github/, the repo root, or docs/
  $hasCodeowners = $false
  foreach ($codeownersPath in @(".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS")) {
    if (Test-RepoPath -Repo $name -Path $codeownersPath) {
      $hasCodeowners = $true
      break
    }
  }

  $hasRenovate = (Test-RepoPath -Repo $name -Path "renovate.json") -or
    (Test-RepoPath -Repo $name -Path ".github/renovate.json")
  $hasDependabot = (Test-RepoPath -Repo $name -Path ".github/dependabot.yml") -or
    (Test-RepoPath -Repo $name -Path ".github/dependabot.yaml")
  $hasManifest = (Test-RepoPath -Repo $name -Path "package.json") -or
    (Test-RepoPath -Repo $name -Path "go.mod") -or
    (Test-RepoPath -Repo $name -Path "requirements.txt") -or
    (Test-RepoPath -Repo $name -Path "pyproject.toml") -or
    (Test-RepoPath -Repo $name -Path "Cargo.toml") -or
    (Test-RepoPath -Repo $name -Path "Gemfile") -or
    (Test-RepoPath -Repo $name -Path "pom.xml")
  # NOTE: manifest probe is repo-root only (Test-RepoPath does not recurse). A repo whose ONLY
  # manifest lives in a subdir (uncommon here — tyl-monorepo carries a root package.json) would be
  # treated as manifest-less and exempted. Accepted limitation; revisit if a nested-only repo appears.
  # Reconciled 2026-07: require dependency automation only where a manifest exists.
  # Renovate-primary is the standard; a documented Renovate+Dependabot-security hybrid is accepted
  # (denken-os: npm security-only w/ version-updates disabled; engineer-tenshoku-navi: post-CVE
  # regression prevention). Repos with no manifest are exempt (nothing to automate).
  $hasDependencyAutomation = (-not $hasManifest) -or $hasRenovate -or $hasDependabot

  $workflowNames = @($workflows | ForEach-Object { $_.name })
  $hasDependencyReview = [bool]($workflowNames | Where-Object { $_ -match "dependency-review" })
  $hasSecretsScan = [bool]($workflowNames | Where-Object { $_ -match "secrets-scan" })

  $publicBranchProtection = $null
  if ($visibility -eq "PUBLIC") {
    $publicBranchProtection = Test-BranchProtection -Repo $name -Branch $defaultBranch
  }

  $publicSecretScanning = $null
  $publicPushProtection = $null
  if ($visibility -eq "PUBLIC" -and $null -ne $security) {
    $publicSecretScanning = $security.secret_scanning.status -eq "enabled"
    $publicPushProtection = $security.secret_scanning_push_protection.status -eq "enabled"
  }

  $openAlerts = Get-OpenDependabotAlertCount -Repo $name
  $isException = $MutableExceptions -contains $name
  $passed = (
    $defaultBranch -eq "main" -and
    $hasCodeowners -and
    $hasDependencyAutomation -and
    # dependency-review-action works on public repos only for personal accounts
    # (private repos would need a GHAS license, unavailable on personal plans)
    ($visibility -ne "PUBLIC" -or $hasDependencyReview) -and
    $hasSecretsScan -and
    $missingHardening.Count -eq 0 -and
    $openAlerts -eq 0 -and
    ($visibility -ne "PUBLIC" -or $publicBranchProtection -eq $true) -and
    ($visibility -ne "PUBLIC" -or $publicSecretScanning -eq $true) -and
    ($visibility -ne "PUBLIC" -or $publicPushProtection -eq $true)
  )

  $rows += [pscustomobject]@{
    repo = $name
    visibility = $visibility
    defaultBranch = $defaultBranch
    codeowners = $hasCodeowners
    dependencyAutomation = $hasDependencyAutomation
    dependencyReview = $hasDependencyReview
    secretsScan = $hasSecretsScan
    missingHardening = $missingHardening
    openDependabotAlerts = $openAlerts
    publicBranchProtection = $publicBranchProtection
    publicSecretScanning = $publicSecretScanning
    publicPushProtection = $publicPushProtection
    exception = $isException
    passed = $passed
  }
}

$mutableFailures = @($rows | Where-Object { -not $_.exception -and -not $_.passed })
$strictFailures = @($rows | Where-Object { -not $_.passed })
$openAlertsTotal = ($rows | Where-Object { $_.openDependabotAlerts -gt 0 } | Measure-Object openDependabotAlerts -Sum).Sum
if ($null -eq $openAlertsTotal) {
  $openAlertsTotal = 0
}

# This repo is public: its step summary and artifacts are world-readable. Per-repo rows for
# private repos would map their attack surface (open alert counts, unhardened workflow names)
# to names that are already public via repos.json — anonymized per-row output is reversible
# by sort order, so private repos are collapsed into ONE aggregate row instead.
# Pass/fail gating stays exact; run locally with -IncludePrivateDetail for the full table.
if ($IncludePrivateDetail) {
  $displayRows = @($rows | Sort-Object repo)
} else {
  $publicRows = @($rows | Where-Object { $_.visibility -eq "PUBLIC" } | Sort-Object repo)
  $privateRows = @($rows | Where-Object { $_.visibility -ne "PUBLIC" } | Sort-Object repo)
  $displayRows = $publicRows
  if ($privateRows.Count -gt 0) {
    $privateAlerts = ($privateRows | Where-Object { $_.openDependabotAlerts -gt 0 } |
      Measure-Object openDependabotAlerts -Sum).Sum
    if ($null -eq $privateAlerts) { $privateAlerts = 0 }
    $privateHardeningCount = (@($privateRows | ForEach-Object { @($_.missingHardening).Count }) |
      Measure-Object -Sum).Sum
    $privateFailedCount = @($privateRows | Where-Object { -not $_.passed }).Count
    $privateHardening = @()
    if ($privateHardeningCount -gt 0) {
      $privateHardening = @("$privateHardeningCount workflow(s) across private repos (redacted)")
    }
    $displayRows += [pscustomobject]@{
      repo = "(private x $($privateRows.Count) - aggregated)"
      visibility = "PRIVATE"
      defaultBranch = "-"
      codeowners = $null
      dependencyAutomation = $null
      dependencyReview = $null
      secretsScan = $null
      missingHardening = $privateHardening
      openDependabotAlerts = $privateAlerts
      publicBranchProtection = $null
      publicSecretScanning = $null
      publicPushProtection = $null
      exception = (@($privateRows | Where-Object { $_.exception }).Count -gt 0)
      passed = ($privateFailedCount -eq 0)
    }
  }
}

$summary = [pscustomobject]@{
  owner = $Owner
  generatedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
  activeRepos = $activeRepos.Count
  minimumActiveRepos = $MinimumActiveRepos
  scopeFailure = $scopeFailure
  archivedRepos = $archivedRepos.Count
  mutableExceptions = $MutableExceptions
  mutableFailures = $mutableFailures.Count
  strictFailures = $strictFailures.Count
  openDependabotAlerts = $openAlertsTotal
  mutableScore = if ($mutableFailures.Count -eq 0) { "100/100" } else { "FAIL" }
  strictExceptions = @($strictFailures | Where-Object { $_.exception } | ForEach-Object { $_.repo })
  privateRowsRedacted = (-not $IncludePrivateDetail)
  rows = $displayRows
}

$summary | ConvertTo-Json -Depth 8 | Set-Content -Path $JsonOut -Encoding UTF8

$markdown = @()
$markdown += "# GitHub Governance Audit"
$markdown += ""
$markdown += "- Owner: ``$Owner``"
$markdown += "- Generated UTC: ``$($summary.generatedAtUtc)``"
$markdown += "- Active repos: $($summary.activeRepos)"
$markdown += "- Minimum active repos: $($summary.minimumActiveRepos)"
$markdown += "- Scope failure: $($summary.scopeFailure)"
$markdown += "- Archived repos: $($summary.archivedRepos)"
$markdown += "- Mutable score: **$($summary.mutableScore)**"
$markdown += "- Mutable failures: $($summary.mutableFailures)"
$markdown += "- Strict failures: $($summary.strictFailures)"
$markdown += "- Open Dependabot alerts: $($summary.openDependabotAlerts)"
if ($summary.privateRowsRedacted) {
  $markdown += "- Private-repo rows are redacted (public output). Re-run locally with ``-IncludePrivateDetail`` for names."
}
$markdown += ""
$markdown += "| repo | visibility | passed | exception | alerts | missing hardening |"
$markdown += "|---|---:|---:|---:|---:|---|"
foreach ($row in $displayRows) {
  $missing = if (@($row.missingHardening).Count -eq 0) { "" } else { (@($row.missingHardening) -join ", ") }
  $alerts = if ($row.openDependabotAlerts -lt 0) { "n/a" } else { "$($row.openDependabotAlerts)" }
  $markdown += "| ``$($row.repo)`` | $($row.visibility) | $($row.passed) | $($row.exception) | $alerts | $missing |"
}

$markdown | Set-Content -Path $MarkdownOut -Encoding UTF8

if ($scopeFailure) {
  Write-Error "Governance audit saw only $($activeRepos.Count) active repo(s), below the required minimum of $MinimumActiveRepos. Check ORG_GOVERNANCE_AUDIT_TOKEN repo/read:org access."
}

# log output is world-readable on this public repo too — keep private repo names out of it
function Get-SafeRepoNames {
  param([object[]]$FailedRows)

  if ($IncludePrivateDetail) {
    return ($FailedRows | ForEach-Object { $_.repo }) -join ', '
  }

  $names = @($FailedRows | ForEach-Object {
    if ($_.visibility -eq "PUBLIC") { $_.repo } else { "(private)" }
  })
  return $names -join ', '
}

if ($mutableFailures.Count -gt 0) {
  Write-Error "Governance audit failed for $($mutableFailures.Count) mutable repo(s): $(Get-SafeRepoNames -FailedRows $mutableFailures)"
}

Write-Host "Governance audit passed for mutable repos: $($summary.mutableScore)"
if ($strictFailures.Count -gt 0) {
  Write-Host "Strict exceptions/failures: $(Get-SafeRepoNames -FailedRows $strictFailures)"
}
