# ai-knowledge-mirror-sync.ps1
# AI_knowledge（Google Drive）を正本として、GitHub の Private リポジトリ
# ys1887/ai-knowledge-mirror へ一方向に写す日次スクリプト。
#
# 正本（保管）: AI_knowledge\20_areas\ai-operations\scripts\ai-knowledge-mirror-sync.ps1
# 実行コピー  : C:\Users\nekol\scripts\ai-knowledge-mirror-sync.ps1
# 実行方法    : タスクスケジューラから、本人のアカウントで毎日 1 回。
#               初回だけは手で実行して様子を見る。
#
# 動作:
#   1. 作業フォルダ（clone）が無ければ作る。
#   2. 資格情報らしい名前のファイルが正本側に無いか軽く確認し、あれば止まる。
#   3. robocopy /MIR で正本を作業フォルダへ写す（.git と SYNC-LOG.md は除く）。
#   4. 写し側に入った .gitignore / .gitattributes は消す（git の制御ファイルは
#      写しに含めない、という意図した差異。Drive 側の原本は触らない）。
#   5. 変更があれば、要約を SYNC-LOG.md に追記して commit し、push する。
#   6. 実行の記録は C:\Users\nekol\ai-knowledge-mirror-last-run.log に残す。
#
# 注意:
#   - force push はしない。push に失敗したら記録して異常終了する。
#   - GitHub 側を直接編集しない前提。編集は常に対象の正本（Drive）で行う。

$ErrorActionPreference = 'Stop'
$OutputEncoding = [Console]::OutputEncoding = [Text.UTF8Encoding]::new()

$Source = 'E:\Documents\Google Drive\AI_knowledge'
$Stage  = 'C:\Users\nekol\ai-knowledge-mirror'
$Remote = 'git@github.com:ys1887/ai-knowledge-mirror.git'
$RunLog = 'C:\Users\nekol\ai-knowledge-mirror-last-run.log'
$GitName  = 'akanekoplay'
$GitEmail = '200343389+ys1887@users.noreply.github.com'

function Log([string]$msg) {
  $line = '{0} {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
  Add-Content -LiteralPath $RunLog -Value $line -Encoding UTF8
  Write-Output $line
}

function Fail([string]$msg) {
  Log "ERROR: $msg"
  exit 2
}

Set-Content -LiteralPath $RunLog -Value '' -Encoding UTF8
Log 'sync start'

# --- 1. 前提の確認と作業フォルダの用意 ---
if (-not (Test-Path -LiteralPath $Source)) { Fail "source not found: $Source" }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Fail 'git not found' }

if (-not (Test-Path -LiteralPath (Join-Path $Stage '.git'))) {
  Log 'staging clone not found; cloning'
  if (Test-Path -LiteralPath $Stage) { Fail "staging path exists but is not a clone: $Stage" }
  git clone $Remote $Stage 2>&1 | ForEach-Object { Log "clone: $_" }
  if (-not (Test-Path -LiteralPath (Join-Path $Stage '.git'))) { Fail 'clone failed' }
}
Set-Location -LiteralPath $Stage
git config user.name $GitName
git config user.email $GitEmail
git config core.longpaths true
git config core.autocrlf false
git config core.quotepath false
# 初回（まだ commit が無い）場合はブランチ名を main にそろえる
git rev-parse --verify HEAD *> $null
if ($LASTEXITCODE -ne 0) { git symbolic-ref HEAD refs/heads/main }

# --- 2. 資格情報らしい名前のファイルの軽い確認（あれば止まる）---
$namePattern = '(?i)(^\.env($|\.)|auth\.json$|credential|secret|\.pem$|\.key$|\.p12$|\.pfx$|^id_rsa|^\.netrc$|\.kdbx$)'
$suspects = Get-ChildItem -LiteralPath $Source -Recurse -File -Force -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match $namePattern -and $_.Name -ne '.env.example' -and $_.FullName -notmatch '\\.venv\\' }
if ($suspects) {
  foreach ($s in $suspects) { Log "SUSPECT NAME: $($s.FullName.Substring($Source.Length + 1))" }
  Fail 'credential-like file names found; push stopped. Check the files and, if they are fine, adjust this script.'
}

# --- 3. 正本を作業フォルダへ写す ---
robocopy $Source $Stage /MIR /XD '.git' /XF 'SYNC-LOG.md' /R:1 /W:1 /NP /NFL /NDL | Out-Null
if ($LASTEXITCODE -ge 8) { Fail "robocopy failed with code $LASTEXITCODE" }
Log "robocopy done (code $LASTEXITCODE)"

# --- 4. git の制御ファイルを写し側から外す ---
Get-ChildItem -LiteralPath $Stage -Recurse -File -Force -ErrorAction SilentlyContinue |
  Where-Object { ($_.Name -eq '.gitignore' -or $_.Name -eq '.gitattributes') -and $_.FullName -notmatch '\\.git\\' } |
  ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force }

# --- 5. 変更の確認と要約 ---
git add -A
$changes = git -c core.quotepath=false diff --cached --name-status
if (-not $changes) {
  Log 'no changes; nothing to push'
  exit 0
}
$added = @($changes | Where-Object { $_ -match '^A' }).Count
$modified = @($changes | Where-Object { $_ -match '^M' }).Count
$deleted = @($changes | Where-Object { $_ -match '^D' }).Count
$topGroups = $changes | ForEach-Object { ($_ -split "`t")[-1] -split '[\\/]' | Select-Object -First 1 } |
  Group-Object | Sort-Object Count -Descending | ForEach-Object { '{0}: {1}' -f $_.Name, $_.Count }
$bigFiles = @()
foreach ($c in $changes) {
  $parts = $c -split "`t"
  if ($parts[0] -match '^[AM]') {
    $p = Join-Path $Stage $parts[-1]
    if ((Test-Path -LiteralPath $p) -and (Get-Item -LiteralPath $p).Length -gt 1MB) {
      $bigFiles += '{0} ({1:N1} MB)' -f $parts[-1], ((Get-Item -LiteralPath $p).Length / 1MB)
    }
  }
}
$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
$digest = @()
$digest += "## $stamp"
$digest += ''
$digest += "- 追加 $added 件 / 変更 $modified 件 / 削除 $deleted 件"
$digest += "- 第 1 階層の内訳: $($topGroups -join ', ')"
if ($bigFiles) { $digest += "- 1 MB 超の追加・変更: $($bigFiles -join ', ')" }
$digest += ''

$syncLog = Join-Path $Stage 'SYNC-LOG.md'
if (-not (Test-Path -LiteralPath $syncLog)) {
  Set-Content -LiteralPath $syncLog -Value "# SYNC-LOG`n`nAI_knowledge の写しの同期記録。新しいものが上に来るように追記する。`n" -Encoding UTF8
}
$syncLines = @(Get-Content -LiteralPath $syncLog)
$insertAt = -1
for ($i = 0; $i -lt $syncLines.Count; $i++) {
  if ($syncLines[$i] -match '^## ') { $insertAt = $i; break }
}
if ($insertAt -lt 0) {
  Add-Content -LiteralPath $syncLog -Value ($digest -join "`n") -Encoding UTF8
} else {
  $merged = @()
  if ($insertAt -gt 0) { $merged += $syncLines[0..($insertAt - 1)] }
  $merged += $digest
  $merged += $syncLines[$insertAt..($syncLines.Count - 1)]
  Set-Content -LiteralPath $syncLog -Value $merged -Encoding UTF8
}
git add SYNC-LOG.md

# --- 6. commit と push ---
$msg = "mirror sync $stamp (+$added ~$modified -$deleted)"
git commit -m $msg | ForEach-Object { Log "commit: $_" }
git push origin main 2>&1 | ForEach-Object { Log "push: $_" }
if ($LASTEXITCODE -ne 0) { Fail 'push failed' }
Log 'sync done'
exit 0
