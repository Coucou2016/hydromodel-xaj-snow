# SCE-UA rep budget sensitivity: XAJ-MZ vs XAJ-Snow @ 01013500 & 14306500
# Usage:
#   .\RUN_REP_BUDGET_SENSITIVITY.ps1                 # full {200,800,2000,5000}
#   .\RUN_REP_BUDGET_SENSITIVITY.ps1 200,800         # reduced tiers
#   .\RUN_REP_BUDGET_SENSITIVITY.ps1 2000,5000       # long-run remainder
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

$reps = "200,800,2000,5000"
if ($args.Count -ge 1) { $reps = $args[0] }

Write-Host "=== Ensure minicache for pilot basins ==="
& $py scripts/build_caravan_minicache.py `
  --data-root "_portable_data/datasets-origin" `
  --region-folder camels `
  --basin-ids camels_01013500 camels_14306500 `
  --t-range 1985-10-01 2014-09-30 `
  --cache-dir "_portable_data/.cache_global_then_refine_v2"

Write-Host "=== Rep budget sensitivity reps=$reps ==="
& $py scripts/run_rep_budget_sensitivity.py --python $py --reps $reps
Write-Host "Done. See results/diagnostics/rep_budget_sensitivity.csv and .md"
