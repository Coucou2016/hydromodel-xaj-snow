Param(
  [string]$CondaEnv = "hydromodel",
  [switch]$Download
)

$ErrorActionPreference = "Stop"

# Run from this repo root (directory of this script)
Set-Location -Path $PSScriptRoot

Write-Host "Repo root: $PWD"

# Make the run fully portable:
# - Force "~" to resolve inside this repo (so no config is written/read from C:\Users\...)
# - Point hydro_setting explicitly to the repo copy
$env:HOME = $PSScriptRoot
$env:USERPROFILE = $PSScriptRoot
$env:HOMEDRIVE = (Split-Path $PSScriptRoot -Qualifier)
$env:HOMEPATH = $PSScriptRoot.Substring($env:HOMEDRIVE.Length)
$env:HYDRO_SETTING_FILE = (Join-Path $PSScriptRoot "hydro_setting.yml")

Write-Host "Activating conda env: $CondaEnv"
conda activate $CondaEnv

Write-Host "1) Initialize/download CAMELS-US into ./_portable_data/"
if ($Download) {
  python scripts/portable_download_camels_us.py --download
} else {
  python scripts/portable_download_camels_us.py
}

Write-Host "2) Calibration (quick settings)"
python scripts/run_xaj_calibration.py --config configs/portable_camels_us_quick.yaml

Write-Host "3) Evaluation (test period)"
$caliDir = "results/portable_camels_us_01013500/xaj_mz_SCE_UA"
python scripts/run_xaj_evaluate.py --calibration-dir $caliDir --eval-period test

Write-Host "4) Visualization (figures saved under eval_dir/figures)"
$evalDir = "$caliDir/evaluation_test"
python scripts/visualize.py --eval-dir $evalDir

Write-Host "Done. Check: $evalDir/figures/"

