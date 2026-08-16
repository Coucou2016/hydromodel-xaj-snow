Param(
  [string]$CondaEnv = "hydromodel"
)

$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot
Write-Host "Repo root: $PWD"

# Fully portable home & settings
$env:HOME = $PSScriptRoot
$env:USERPROFILE = $PSScriptRoot
$env:HOMEDRIVE = (Split-Path $PSScriptRoot -Qualifier)
$env:HOMEPATH = $PSScriptRoot.Substring($env:HOMEDRIVE.Length)
$env:HYDRO_SETTING_FILE = (Join-Path $PSScriptRoot "hydro_setting.yml")
$env:PYTHONUTF8 = "1"

Write-Host "Activating conda env: $CondaEnv"
conda activate $CondaEnv

Write-Host "0) Generate local demo dataset under ./_portable_data/"
python scripts/generate_demo_selfmade_dataset.py

Write-Host "1) Calibration (fast scipy)"
python scripts/run_xaj_calibration.py --config configs/portable_selfmade_demo_quick.yaml

Write-Host "2) Evaluation (test period)"
$caliDir = "results/portable_demo_selfmade/xaj_mz_scipy"
python scripts/run_xaj_evaluate.py --calibration-dir $caliDir --eval-period test

Write-Host "3) Visualization"
$evalDir = "$caliDir/evaluation_test"
python scripts/visualize.py --eval-dir $evalDir

Write-Host "4) Basin overview map (boundary/river/gauge)"
$figDir = "$evalDir/figures"
python scripts/plot_basin_overview.py --dataset-name demo_selfmade --basin-id basin_001 --output "$figDir/basin_001_map.png"

Write-Host "Done. Check: $evalDir/figures/"

