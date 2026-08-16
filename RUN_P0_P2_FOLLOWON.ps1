# After refine: rep=200 sensitivity + small batch1 (camels, rep=200)
# Usage: .\RUN_P0_P2_FOLLOWON.ps1
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

Write-Host "=== P0 rep budget tier: 200 (800 reused; 2000/5000 via RUN_REP_BUDGET_SENSITIVITY.ps1) ==="
& $py scripts/run_rep_budget_sensitivity.py --python $py --reps 200

Write-Host "=== P2 small batch1: 6 basins x 2 models, rep=200 ==="
# Prefer mixed snow/no-snow subset of sample_batch1
& $py scripts/run_batch_calibration.py `
  --python $py `
  --sample-csv results/sampling/sample_batch1.csv `
  --rep 200 `
  --workers 1 `
  --limit 6 `
  --skip-minicache

Write-Host "=== P3 applicability first look ==="
& $py scripts/analyze_applicability_first_look.py `
  --sample results/sampling/sample_batch1.csv

Write-Host "FOLLOWON_DONE"
