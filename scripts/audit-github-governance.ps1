[CmdletBinding()]
param(
  [string]$Owner = "thinkyou0714",
  [string[]]$MutableExceptions = @("lab-infra"),
  [int]$Limit = 300,
  [int]$MinimumActiveRepos = 21,
  [string]$JsonOut = "governance-audit.json",
  [string]$MarkdownOut = "governance-audit.md"
)

$ErrorActionPreference = "Stop"

function Invoke-GhJson {
  param([string[]]$Arguments)

  $output = & gh @Arguments 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw "gh $($Arguments -join ' ') failed: $output"
  }

  if ([string]::IsNullOrWhiteSpace($output)) {
    return $null
  }

  return $output | ConvertFrom-Json
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
      if ($line -match "^\S" -and -not [string]::IsNullOrWhiteSpace($line)) {
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

  $block = Get-TopLevelBlock -Text $Text -Name "permissions"
  if ([string]::IsNullOrWhiteSpace($block)) {
    return $false
  }

  $hasContentsRead = $false
  foreach ($line in ($block -split "\n")) {
    if ($line -notmatch "^\s+([A-Za-z0-9_-]+):\s*([A-Za-z-]+)\s*(?:#.*)?$") {
      continue
    }

    $permission = $Matches[1]
    $access = $Matches[2]
    if ($permission -eq "contents" -and $access -eq "read") {
      $hasContentsRead = $true
    }

    if ($access -notin @("read", "none")) {
      return $false
    }
  }

  return $hasContentsRead
}

function Test-TopLevelConcurrency {
  param([string]$Text)

  $block = Get-TopLevelBlock -Text $Text -Name "concurrency"
  if ([string]::IsNullOrWhiteSpace($block)) {
    return $false
  }

  $hasGroup = $block -match "(?m)^[ \t]*group:\s*\$\{\{\s*github\.workflow\s*\}\}-\$\{\{\s*github\.ref\s*\}\}\s*$"
  $hasCancel = $block -match "(?m)^[ \t]*cancel-in-progress:\s*true\s*$"
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

  $output = & gh api "/repos/$Owner/$Repo/dependabot/alerts?state=open&per_page=100" 2>$null
  if ($LASTEXITCODE -ne 0) {
    return -1
  }

  $text = "$output".Trim()
  if ([string]::IsNullOrWhiteSpace($text) -or $text -eq "[]") {
    return 0
  }

  $parsed = $text | ConvertFrom-Json
  return @($parsed).Count
}

$repos = Invoke-GhJson @(
  "repo", "list", $Owner,
  "--limit", "$Limit",
  "--json", "name,isArchived,visibility,defaultBranchRef"
)

$activeRepos = @($repos | Where-Object { -not $_.isArchived })
$archivedRepos = @($repos | Where-Object { $_.isArchived })

# Self-maintaining floor: prefer active_count from the repos.json SSOT (.github repo) over the
# hard-coded $MinimumActiveRepos default, so adding/removing a repo updates the threshold in one place.
$reposJsonText = Get-RepoFileText -Repo ".github" -Path "repos.json"
if ($reposJsonText) {
  try {
    $reposSsot = $reposJsonText | ConvertFrom-Json
    if ($null -ne $reposSsot.active_count -and [int]$reposSsot.active_count -gt 0) {
      $MinimumActiveRepos = [int]$reposSsot.active_count
    }
  } catch { }
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

  $hasRenovate = (Test-RepoPath -Repo $name -Path "renovate.json") -or
    (Test-RepoPath -Repo $name -Path ".github/renovate.json")
  $hasDependabot = (Test-RepoPath -Repo $name -Path ".github/dependabot.yml") -or
    (Test-RepoPath -Repo $name -Path ".github/dependabot.yaml")
  $hasDependencyAutomation = $hasRenovate -or $hasDependabot

  $workflowNames = @($workflows | ForEach-Object { $_.name })
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
    (Test-RepoPath -Repo $name -Path ".github/CODEOWNERS") -and
    $hasDependencyAutomation -and
    [bool]($workflowNames | Where-Object { $_ -match "dependency-review" }) -and
    [bool]($workflowNames | Where-Object { $_ -match "secrets-scan" }) -and
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
    codeowners = Test-RepoPath -Repo $name -Path ".github/CODEOWNERS"
    dependencyAutomation = $hasDependencyAutomation
    dependencyReview = [bool]($workflowNames | Where-Object { $_ -match "dependency-review" })
    secretsScan = [bool]($workflowNames | Where-Object { $_ -match "secrets-scan" })
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
  rows = $rows
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
$markdown += ""
$markdown += "| repo | visibility | passed | exception | alerts | missing hardening |"
$markdown += "|---|---:|---:|---:|---:|---|"
foreach ($row in ($rows | Sort-Object repo)) {
  $missing = if ($row.missingHardening.Count -eq 0) { "" } else { ($row.missingHardening -join ", ") }
  $markdown += "| ``$($row.repo)`` | $($row.visibility) | $($row.passed) | $($row.exception) | $($row.openDependabotAlerts) | $missing |"
}

$markdown | Set-Content -Path $MarkdownOut -Encoding UTF8

if ($scopeFailure) {
  Write-Error "Governance audit saw only $($activeRepos.Count) active repo(s), below the required minimum of $MinimumActiveRepos. Check ORG_GOVERNANCE_AUDIT_TOKEN repo/read:org access."
}

if ($mutableFailures.Count -gt 0) {
  Write-Error "Governance audit failed for mutable repos: $($mutableFailures.repo -join ', ')"
}

Write-Host "Governance audit passed for mutable repos: $($summary.mutableScore)"
if ($strictFailures.Count -gt 0) {
  Write-Host "Strict exceptions/failures: $($strictFailures.repo -join ', ')"
}
