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
$regionFolder = "camels"

$basins = @(
  "camels_01013500",
  "camels_01484100",
  "camels_14306500",
  "camels_14308990"
)

$sceuaTpl = "configs\real_caravan_external_camels_sceua_template.yaml"
$refineTpl = "configs\real_caravan_external_camels_refine_from_sceua_template.yaml"

Write-Host ""
Write-Host "1) Build shared minimal cache for all basins (new cache dir from hydro_setting.yml)"
$cacheDir = "_portable_data\.cache_global_then_refine_v2"
New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null

conda run -n $CondaEnv python scripts/build_caravan_minicache.py --data-root $dataRoot --region-folder $regionFolder --basin-ids $basins --cache-dir $cacheDir --t-range 1985-10-01 2014-09-30 --pet-preference FAO_PENMAN_MONTEITH

foreach ($bid in $basins) {
  Write-Host ""
  Write-Host "============================================================"
  Write-Host "Basin: $bid"
  Write-Host "============================================================"

  $cali1 = "results\multi_basin_global_then_refine_v2\$bid\xaj_mz_SCE_UA"
  if (-not (Test-Path "$cali1\calibration_results.json")) {
    # Stage 1 config
    $cfg1 = "configs\_tmp_stage1_sceua.yaml"
    Copy-Item -Force $sceuaTpl $cfg1
    conda run -n $CondaEnv python scripts/set_caravan_basin_id_in_config.py --basin-id $bid --config $cfg1

    # Stage 1: global SCE-UA
    conda run -n $CondaEnv python scripts/run_xaj_calibration.py --config $cfg1
  } else {
    Write-Host "Stage-1 exists, skip calibration: $cali1"
  }

  if (-not (Test-Path "$cali1\evaluation_test\basins_metrics.csv")) {
    conda run -n $CondaEnv python scripts/run_xaj_evaluate.py --calibration-dir $cali1 --eval-period test
    conda run -n $CondaEnv python scripts/visualize.py --eval-dir "$cali1\evaluation_test"
    conda run -n $CondaEnv python scripts/plot_public_basin_overview.py --dataset caravan --region US --basin-id $bid --output "$cali1\evaluation_test\figures\basin_overview.png"
  } else {
    Write-Host "Stage-1 evaluation exists, skip: $cali1\evaluation_test"
  }

  $cali2 = "results\multi_basin_global_then_refine_v2\$bid\xaj_mz_scipy"
  if (-not (Test-Path "$cali2\calibration_results.json")) {
    # Stage 2 config
    $cfg2 = "configs\_tmp_stage2_refine.yaml"
    Copy-Item -Force $refineTpl $cfg2
    conda run -n $CondaEnv python scripts/set_caravan_basin_id_in_config.py --basin-id $bid --config $cfg2

    # Stage 2: local refine from Stage 1 best params
    conda run -n $CondaEnv python scripts/run_xaj_calibration.py --config $cfg2
  } else {
    Write-Host "Stage-2 exists, skip calibration: $cali2"
  }

  if (-not (Test-Path "$cali2\evaluation_test\basins_metrics.csv")) {
    conda run -n $CondaEnv python scripts/run_xaj_evaluate.py --calibration-dir $cali2 --eval-period test
    conda run -n $CondaEnv python scripts/visualize.py --eval-dir "$cali2\evaluation_test"
    conda run -n $CondaEnv python scripts/plot_public_basin_overview.py --dataset caravan --region US --basin-id $bid --output "$cali2\evaluation_test\figures\basin_overview.png"
  } else {
    Write-Host "Stage-2 evaluation exists, skip: $cali2\evaluation_test"
  }
}

Write-Host ""
Write-Host "Done. Stage-1 results:"
Write-Host "  results\\multi_basin_global_then_refine_v2\\<basin>\\xaj_mz_SCE_UA\\evaluation_test\\figures\\"
Write-Host "Stage-2 refined results:"
Write-Host "  results\\multi_basin_global_then_refine_v2\\<basin>\\xaj_mz_scipy\\evaluation_test\\figures\\"

