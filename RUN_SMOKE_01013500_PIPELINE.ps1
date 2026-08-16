# Quick pipeline verification: minicache fix + SCE-UA smoke + scipy smoke + evaluate + HTML report
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:HOME = $PSScriptRoot
$env:USERPROFILE = $PSScriptRoot
$env:HOMEDRIVE = (Split-Path $PSScriptRoot -Qualifier)
$env:HOMEPATH = $PSScriptRoot.Substring($env:HOMEDRIVE.Length)
$env:HYDRO_SETTING_FILE = Join-Path $PSScriptRoot "hydro_setting.yml"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$py = "D:\miniforge3\envs\hydromodel\python.exe"

& $py scripts/build_caravan_minicache.py --data-root "_portable_data/datasets-origin" --region-folder camels --basin-id camels_01013500 --t-range 1985-10-01 2014-09-30 --cache-dir "_portable_data/.cache_global_then_refine_v2"
& $py scripts/run_xaj_calibration.py --config configs/real_caravan_camels_01013500_extended_sceua_smoke.yaml
& $py scripts/run_xaj_evaluate.py --calibration-dir "results/real_caravan_camels_01013500_extended_sceua_smoke/xaj_mz_SCE_UA" --eval-period test
& $py scripts/run_xaj_calibration.py --config configs/real_caravan_camels_01013500_extended_refine_scipy_smoke.yaml
& $py scripts/run_xaj_evaluate.py --calibration-dir "results/real_caravan_camels_01013500_extended_refine_scipy_smoke/xaj_mz_scipy" --eval-period test
"PIPELINE_DONE=1" | Out-File "results/diagnostics/smoke_pipeline_status.txt" -Encoding utf8
& $py scripts/generate_iteration_html_report.py
