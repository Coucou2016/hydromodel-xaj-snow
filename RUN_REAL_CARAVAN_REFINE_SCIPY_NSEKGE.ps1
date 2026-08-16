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

$dataRoot = "_portable_data\datasets-origin"
$basinId = "camels_01013500"
$regionFolder = "camels"

Write-Host "1) Ensure minimal CARAVAN cache for one basin"
$tsCache = "_portable_data\.cache\caravan_camels_timeseries_batch_camels_01013500_camels_01013500.nc"
if (-not (Test-Path $tsCache) -or (Get-Item $tsCache).Length -eq 0) {
  if (Test-Path $tsCache) { Remove-Item $tsCache -Force }
  conda run -n $CondaEnv python scripts/build_caravan_minicache.py --data-root $dataRoot --region-folder $regionFolder --basin-id $basinId --t-range 1985-10-01 2014-09-30 --pet-preference FAO_PENMAN_MONTEITH
}

Write-Host "2) Calibration refine (scipy, NSEKGE loss)"
conda run -n $CondaEnv python scripts/run_xaj_calibration.py --config configs/real_caravan_camels_01013500_refine_scipy_nsekge.yaml

Write-Host "3) Evaluation (test period)"
$caliDir = "results/real_caravan_camels_01013500_refine_scipy_nsekge/xaj_mz_scipy"
conda run -n $CondaEnv python scripts/run_xaj_evaluate.py --calibration-dir $caliDir --eval-period test

Write-Host "4) Visualization"
$evalDir = "$caliDir/evaluation_test"
conda run -n $CondaEnv python scripts/visualize.py --eval-dir $evalDir

Write-Host "5) Basin overview map"
$basinFig = "$evalDir/figures/basin_${basinId}_map.png"
conda run -n $CondaEnv python scripts/plot_public_basin_overview.py --dataset caravan --region US --basin-id $basinId --output $basinFig

Write-Host "Done. Check: $evalDir/figures/"

