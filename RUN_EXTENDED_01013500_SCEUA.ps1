# Extended SCE-UA for camels_01013500 (requires minicache; uses repo hydro_setting.yml)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
# hydrodataset reads ~/hydro_setting.yml at import — point HOME to repo (see other RUN_*.ps1)
$env:HOME = $PSScriptRoot
$env:USERPROFILE = $PSScriptRoot
$env:HOMEDRIVE = (Split-Path $PSScriptRoot -Qualifier)
$env:HOMEPATH = $PSScriptRoot.Substring($env:HOMEDRIVE.Length)
$env:HYDRO_SETTING_FILE = Join-Path $PSScriptRoot "hydro_setting.yml"
$env:PYTHONUTF8 = "1"
$py = "D:\miniforge3\envs\hydromodel\python.exe"
# Rebuild minicache (removes overlapping batch files that break hydrodataset basin concat)
& $py scripts/build_caravan_minicache.py --data-root "_portable_data/datasets-origin" --region-folder camels --basin-id camels_01013500 --t-range 1985-10-01 2014-09-30 --cache-dir "_portable_data/.cache_global_then_refine_v2"
& $py scripts/run_xaj_calibration.py --config configs/real_caravan_camels_01013500_extended_sceua.yaml
$cali1 = "results/real_caravan_camels_01013500_extended_sceua/xaj_mz_SCE_UA"
& $py scripts/run_xaj_evaluate.py --calibration-dir $cali1 --eval-period test
& $py scripts/run_xaj_calibration.py --config configs/real_caravan_camels_01013500_extended_refine_scipy.yaml
$cali2 = "results/real_caravan_camels_01013500_extended_refine_scipy/xaj_mz_scipy"
& $py scripts/run_xaj_evaluate.py --calibration-dir $cali2 --eval-period test
# Smoke (rep=80): configs/*_smoke.yaml + matching run_xaj_evaluate.py calls
