# PowerShell 5.1+, Windows only. Executes third-party native code ONLY with -Action Install.
param(
  [ValidateSet('Check','Install','RegisterCodex')][string]$Action='Check',
  [string]$PythonExe='python'
)
$ErrorActionPreference='Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Windows required.' }
$Root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$Bridge=Join-Path $Root 'private\vocaloid_bridge'
$Sha='8ac1f0287e227ccae8be51b8de3d5aaf60b51cdf'
function Need([string]$cmd) { if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "Missing command: $cmd" } }
function Good([string]$stage) { if ($LASTEXITCODE -ne 0) { throw "$stage failed: $LASTEXITCODE" } }
if ($Action -eq 'RegisterCodex') {
  Need 'codex'
  $BridgePy=Join-Path $Bridge '.venv\Scripts\python.exe'
  if (-not (Test-Path -LiteralPath $BridgePy)) { throw 'Run -Action Install first.' }
  & codex mcp add vocaloid7-native --env "VOCALOID_WORKSPACE=$Bridge" --env "PYTHONPATH=$Bridge" --env 'PYTHONUTF8=1' -- $BridgePy -m vocaloid_bridge
  Good 'Codex registration'
  Write-Host 'Registered in local Codex. Restart Codex and check: codex mcp list'
  exit 0
}
Need 'git'; Need 'dotnet'; Need $PythonExe
$PyPath=(& $PythonExe -c 'import sys; print(sys.executable)').Trim()
Good 'Python path check'
$PyOk=(& $PythonExe -c 'import sys; print(int(sys.version_info >= (3,11)))').Trim()
Good 'Python version check'
if ($PyOk -ne '1') { throw 'Python 3.11 or later required.' }
$Sdks=@(& dotnet --list-sdks)
Good '.NET SDK check'
if (-not @($Sdks | Where-Object { $_ -match '^10\.' }).Count) { throw '.NET 10 SDK required.' }
Write-Host "Python: $PyPath"; Write-Host '.NET 10 SDK: OK'; Write-Host "Bridge pinned commit: $Sha"
Write-Host 'WARNING: This is third-party native code; review source, privacy and licenses before running.'
if ($Action -eq 'Check') {
  Write-Host 'Check complete. No downloads or modifications performed.'
  exit 0
}
if (-not (Test-Path -LiteralPath $Bridge)) {
  New-Item -ItemType Directory -Path (Split-Path $Bridge -Parent) -Force | Out-Null
  & git clone 'https://github.com/Asakitan/vocaloid_bridge.git' $Bridge
  Good 'Clone bridge'
}
$Current=(& git -C $Bridge rev-parse HEAD).Trim()
Good 'Bridge HEAD check'
if ($Current -ne $Sha) {
  & git -C $Bridge checkout --detach $Sha
  Good 'Pin bridge commit'
}
$UpstreamSetup=Join-Path $Bridge 'tools\setup.ps1'
if (-not (Test-Path $UpstreamSetup)) { throw 'Missing upstream setup.ps1' }
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $UpstreamSetup -Python $PyPath -Product VOCALOID7
Good 'Build VOCALOID7 bridge'
if (-not (Test-Path (Join-Path $Bridge '.venv\Scripts\python.exe'))) { throw 'Missing bridge virtualenv' }
Write-Host 'Bridge installed (not yet verified against YOUR VOCALOID7 trial).'
Write-Host 'VS Code: open this trusted workspace, start vocaloid7-native MCP.'
Write-Host 'Codex: run this script again with -Action RegisterCodex.'
