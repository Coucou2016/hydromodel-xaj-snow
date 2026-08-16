Param(
  [string]$CondaEnv = "hydromodel"
)

$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

Write-Host "Repo root: $PWD"
Write-Host "Using conda env: $CondaEnv"

$env:HOME = $PSScriptRoot
$env:USERPROFILE = $PSScriptRoot
$env:HOMEDRIVE = (Split-Path $PSScriptRoot -Qualifier)
$env:HOMEPATH = $PSScriptRoot.Substring($env:HOMEDRIVE.Length)
$env:HYDRO_SETTING_FILE = (Join-Path $PSScriptRoot "hydro_setting.yml")
$env:PYTHONUTF8 = "1"

$externalCaravan = "..\hydrodata\Caravan\usr\local\google\home\kratzert\Data\Caravan-Jan25-nc"
$junctionRoot = "_portable_data\datasets-origin\CARAVAN"
$junctionInner = "_portable_data\datasets-origin\CARAVAN\Caravan\Caravan"

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

Write-Host "1) Build minimal cache for 6 basins"
$dataRoot = "_portable_data\datasets-origin"
$regionFolder = "camels"
$cacheDir = "_portable_data\.cache"

# Clean existing caravan camels batch caches to avoid mixing basins.
Get-ChildItem -LiteralPath $cacheDir -Filter "caravan_camels_timeseries_batch_*.nc" -ErrorAction SilentlyContinue | Remove-Item -Force
# Also rebuild the minimal attributes cache so it contains exactly these basins.
$attrCache = "_portable_data\.cache\caravan_attributes.nc"
if (Test-Path $attrCache) {
  Remove-Item $attrCache -Force
}

$basins = @(
  "camels_01013500",
  "camels_01484100",
  "camels_14306500",
  "camels_14308990",
  "camels_14236200"
)

conda run -n $CondaEnv python scripts/build_caravan_minicache.py --data-root $dataRoot --region-folder $regionFolder --basin-ids $basins --t-range 1985-10-01 2014-09-30 --pet-preference FAO_PENMAN_MONTEITH

Write-Host "2) Calibration (quick, scipy NSE) for all basins"
conda run -n $CondaEnv python scripts/run_xaj_calibration.py --config configs/caravan_camels_multi_basin_quick_diag.yaml

Write-Host "3) Evaluation (test period)"
$caliDir = "results/caravan_camels_multi_basin_diag/xaj_mz_scipy"
conda run -n $CondaEnv python scripts/run_xaj_evaluate.py --calibration-dir $caliDir --eval-period test

Write-Host "Done. Check metrics CSV:"
Write-Host "  $caliDir/evaluation_test/basins_metrics.csv"

