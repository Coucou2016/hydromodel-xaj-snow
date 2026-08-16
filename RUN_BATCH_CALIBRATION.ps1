# Batch paired calibration for frozen stratified sample
# Usage:
#   .\RUN_BATCH_CALIBRATION.ps1                 # full frozen sample, rep=800, workers=1
#   .\RUN_BATCH_CALIBRATION.ps1 24 400 2        # limit=24 basins, rep=400, workers=2
#   .\RUN_BATCH_CALIBRATION.ps1 0 800 1         # all frozen, medium budget
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$env:HOME = $PSScriptRoot
$env:USERPROFILE = $PSScriptRoot
$env:HOMEDRIVE = (Split-Path $PSScriptRoot -Qualifier)
$env:HOMEPATH = $PSScriptRoot.Substring($env:HOMEDRIVE.Length)
$env:HYDRO_SETTING_FILE = Join-Path $PSScriptRoot "hydro_setting.yml"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$py = "D:\miniforge3\envs\hydromodel\python.exe"
if (-not (Test-Path $py)) { $py = "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\python.exe" }

$limit = 0
$rep = 800
$workers = 1
if ($args.Count -ge 1) { $limit = [int]$args[0] }
if ($args.Count -ge 2) { $rep = [int]$args[1] }
if ($args.Count -ge 3) { $workers = [int]$args[2] }

if (-not (Test-Path "results\sampling\sample_frozen.csv")) {
  Write-Host "=== Build stratified freeze sample first ==="
  & $py scripts/build_stratified_sample.py --n-freeze 80 --nc-check-n 120
}

Write-Host "=== Batch calibration limit=$limit rep=$rep workers=$workers ==="
$cmd = @(
  "scripts/run_batch_calibration.py",
  "--python", $py,
  "--rep", "$rep",
  "--workers", "$workers",
  "--sample-csv", "results/sampling/sample_frozen.csv"
)
if ($limit -gt 0) { $cmd += @("--limit", "$limit") }
& $py @cmd
Write-Host "Done. See results/batch/metrics_summary.csv and results/batch/logs/"
