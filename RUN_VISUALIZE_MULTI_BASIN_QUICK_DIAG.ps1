Param(
  [string]$CondaEnv = "hydromodel"
)

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$env:HOME = $PSScriptRoot
$env:USERPROFILE = $PSScriptRoot
$env:HOMEDRIVE = (Split-Path $PSScriptRoot -Qualifier)
$env:HOMEPATH = $PSScriptRoot.Substring($env:HOMEDRIVE.Length)
$env:HYDRO_SETTING_FILE = (Join-Path $PSScriptRoot "hydro_setting.yml")
$env:PYTHONUTF8 = "1"

$basins = @(
  "camels_01013500",
  "camels_01484100",
  "camels_14306500",
  "camels_14308990"
)

foreach ($bid in $basins) {
  $evalDir = "results\multi_basin_quick_diag\$bid\xaj_mz_scipy\evaluation_test"
  if (-not (Test-Path $evalDir)) {
    Write-Host "Skip (missing eval dir): $evalDir"
    continue
  }

  Write-Host ""
  Write-Host "============================================================"
  Write-Host "Visualize: $bid"
  Write-Host "============================================================"

  # 1) Standard figures (timeseries/scatter/fdc/monthly)
  conda run -n $CondaEnv python scripts/visualize.py --eval-dir $evalDir

  # 2) Basin overview schematic (boundary + gauge marker)
  $figDir = Join-Path $evalDir "figures"
  New-Item -ItemType Directory -Path $figDir -Force | Out-Null
  $outPng = Join-Path $figDir "basin_overview.png"
  conda run -n $CondaEnv python scripts/plot_public_basin_overview.py --dataset caravan --region US --basin-id $bid --output $outPng
}

Write-Host ""
Write-Host "Done. Figures are under:"
Write-Host "  results\\multi_basin_quick_diag\\<basin>\\xaj_mz_scipy\\evaluation_test\\figures\\"

