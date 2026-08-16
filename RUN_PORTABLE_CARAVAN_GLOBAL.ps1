Param(
  [string]$CondaEnv = "hydromodel",
  [switch]$Download,
  [string]$Region = "Global",
  [string]$BasinId = ""
)

$ErrorActionPreference = "Stop"

# Run from this repo root (directory of this script)
Set-Location -Path $PSScriptRoot

Write-Host "Repo root: $PWD"

# Make the run fully portable:
$env:HOME = $PSScriptRoot
$env:USERPROFILE = $PSScriptRoot
$env:HOMEDRIVE = (Split-Path $PSScriptRoot -Qualifier)
$env:HOMEPATH = $PSScriptRoot.Substring($env:HOMEDRIVE.Length)
$env:HYDRO_SETTING_FILE = (Join-Path $PSScriptRoot "hydro_setting.yml")
$env:PYTHONUTF8 = "1"

Write-Host "Activating conda env: $CondaEnv"
conda activate $CondaEnv

Write-Host "1) Prepare/check CARAVAN under ./_portable_data/"
if ($Download) {
  python scripts/portable_download_caravan.py --download --region $Region
} else {
  python scripts/portable_download_caravan.py --region $Region
}

if ([string]::IsNullOrWhiteSpace($BasinId)) {
  Write-Host ""
  Write-Host "You must provide a BasinId from the printed list."
  Write-Host "Example:"
  Write-Host "  .\RUN_PORTABLE_CARAVAN_GLOBAL.ps1 -CondaEnv hydromodel -Region Global -BasinId <ID>"
  exit 1
}

Write-Host "2) Set basin id in config: $BasinId"
python scripts/set_caravan_basin_id_in_config.py --basin-id $BasinId --config configs/portable_caravan_global_quick.yaml

Write-Host "3) Calibration (quick settings)"
python scripts/run_xaj_calibration.py --config configs/portable_caravan_global_quick.yaml

Write-Host "4) Evaluation (test period)"
$caliDir = "results/portable_caravan_global/xaj_mz_SCE_UA"
python scripts/run_xaj_evaluate.py --calibration-dir $caliDir --eval-period test

Write-Host "5) Visualization (figures saved under eval_dir/figures)"
$evalDir = "$caliDir/evaluation_test"
python scripts/visualize.py --eval-dir $evalDir

Write-Host "6) Basin overview map (boundary + gauge marker)"
$basinFig = "$evalDir/figures/basin_${BasinId}_map.png"
python scripts/plot_public_basin_overview.py --dataset caravan --region $Region --basin-id $BasinId --output $basinFig

Write-Host "Done. Check: $evalDir/figures/"

