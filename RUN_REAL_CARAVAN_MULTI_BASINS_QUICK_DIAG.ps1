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

$externalCaravan = "..\hydrodata\Caravan\usr\local\google\home\kratzert\Data\Caravan-Jan25-nc"
$junctionRoot = "_portable_data\datasets-origin\CARAVAN"
$junctionInner = "_portable_data\datasets-origin\CARAVAN\Caravan\Caravan"

Write-Host "Repo root: $PWD"
Write-Host "Using conda env: $CondaEnv"

Write-Host "0) Link external CARAVAN into ./_portable_data/datasets-origin/"
if (Test-Path $junctionRoot) {
  $item = Get-Item $junctionRoot -ErrorAction SilentlyContinue
  if ($item -and ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    Remove-Item $junctionRoot -Force
  }
}
New-Item -ItemType Directory -Path "_portable_data\datasets-origin\CARAVAN\Caravan" -Force | Out-Null
if (-not (Test-Path $junctionInner)) {
  New-Item -ItemType Junction -Path $junctionInner -Target $externalCaravan | Out-Null
}

$dataRoot = "_portable_data\datasets-origin"
$cacheDir = "_portable_data\.cache"
$regionFolder = "camels"

$basins = @(
  "camels_01013500",
  "camels_01484100",
  "camels_14306500",
  "camels_14308990"
)

foreach ($bid in $basins) {
  Write-Host ""
  Write-Host "============================================================"
  Write-Host "Basin: $bid"
  Write-Host "============================================================"

  # Build minimal cache for this basin (overwrite batch + attributes each time)
  Get-ChildItem -LiteralPath $cacheDir -Filter "caravan_camels_timeseries_batch_*.nc" -ErrorAction SilentlyContinue | Remove-Item -Force
  $attrCache = "_portable_data\.cache\caravan_attributes.nc"
  if (Test-Path $attrCache) { Remove-Item $attrCache -Force }

  conda run -n $CondaEnv python scripts/build_caravan_minicache.py --data-root $dataRoot --region-folder $regionFolder --basin-id $bid --t-range 1985-10-01 2014-09-30 --pet-preference FAO_PENMAN_MONTEITH

  # Create a temp config from template and replace placeholder everywhere
  $tmpConfig = "configs\_tmp_quick_diag.yaml"
  Copy-Item -Force "configs\real_caravan_external_camels_quick_template.yaml" $tmpConfig
  conda run -n $CondaEnv python scripts/set_caravan_basin_id_in_config.py --basin-id $bid --config $tmpConfig

  # Run calibration + evaluation(test)
  conda run -n $CondaEnv python scripts/run_xaj_calibration.py --config $tmpConfig
  $caliDir = "results\multi_basin_quick_diag\$bid\xaj_mz_scipy"
  conda run -n $CondaEnv python scripts/run_xaj_evaluate.py --calibration-dir $caliDir --eval-period test

  # Visualize figures (same style as other cases)
  $evalDir = "$caliDir\evaluation_test"
  conda run -n $CondaEnv python scripts/visualize.py --eval-dir $evalDir

  # Basin overview schematic (boundary + gauge marker)
  $figDir = Join-Path $evalDir "figures"
  New-Item -ItemType Directory -Path $figDir -Force | Out-Null
  $outPng = Join-Path $figDir "basin_overview.png"
  conda run -n $CondaEnv python scripts/plot_public_basin_overview.py --dataset caravan --region US --basin-id $bid --output $outPng
}

Write-Host ""
Write-Host "Done. Each basin metrics in:"
Write-Host "  results\\multi_basin_quick_diag\\<basin>\\xaj_mz_scipy\\evaluation_test\\basins_metrics.csv"
Write-Host "Figures in:"
Write-Host "  results\\multi_basin_quick_diag\\<basin>\\xaj_mz_scipy\\evaluation_test\\figures\\"

