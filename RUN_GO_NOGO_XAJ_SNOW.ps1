# Go/no-go runner for XAJ-Snow vs XAJ-MZ (camels_01013500 and camels_14306500)
# Sets HOME to this repo so hydrodataset reads hydro_setting.yml -> _portable_data.
# NOTE: do not use ErrorActionPreference=Stop around native python.exe — Python
# writes UserWarnings to stderr and PowerShell would abort as NativeCommandError.
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$env:HOME = $PSScriptRoot
$env:USERPROFILE = $PSScriptRoot
$env:HOMEDRIVE = (Split-Path $PSScriptRoot -Qualifier)
$env:HOMEPATH = $PSScriptRoot.Substring($env:HOMEDRIVE.Length)
$env:HYDRO_SETTING_FILE = Join-Path $PSScriptRoot "hydro_setting.yml"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$py = "D:\miniforge3\envs\hydromodel\python.exe"
if (-not (Test-Path $py)) {
    $py = "python"
}

function Invoke-Py {
    param([Parameter(ValueFromRemainingArguments = $true)]$PyArgs)
    & $py @PyArgs
    if ($LASTEXITCODE -ne 0) {
        throw "python failed (exit=$LASTEXITCODE): $($PyArgs -join ' ')"
    }
}

function Invoke-CalibEval([string]$Config, [string]$CaliDir) {
    Invoke-Py scripts/run_xaj_calibration.py --config $Config
    Invoke-Py scripts/run_xaj_evaluate.py --calibration-dir $CaliDir --eval-period test
}

Write-Host "=== Build minicache (P, PET, Q, T) for go/no-go basins ==="
Invoke-Py scripts/build_caravan_minicache.py `
    --data-root "_portable_data/datasets-origin" `
    --region-folder camels `
    --basin-ids camels_01013500 camels_14306500 `
    --t-range 1985-10-01 2014-09-30 `
    --cache-dir "_portable_data/.cache_global_then_refine_v2"

$mode = "all"
if ($args.Count -ge 1) { $mode = $args[0] }

if ($mode -eq "smoke" -or $mode -eq "all") {
    Write-Host "=== Smoke SCE-UA (rep=120) 01013500 XAJ-MZ then XAJ-Snow ==="
    Invoke-CalibEval "configs/xaj_mz_go_nogo_01013500_smoke.yaml" "results/xaj_snow_go_nogo/smoke_camels_01013500_xaj_mz/xaj_mz_SCE_UA"
    Invoke-CalibEval "configs/xaj_snow_go_nogo_01013500_smoke.yaml" "results/xaj_snow_go_nogo/smoke_camels_01013500_xaj_snow/xaj_snow_SCE_UA"
}

if ($mode -eq "medium" -or $mode -eq "all") {
    Write-Host "=== Medium SCE-UA (rep=800) paired go/no-go ==="
    Invoke-CalibEval "configs/xaj_mz_go_nogo_01013500.yaml" "results/xaj_snow_go_nogo/camels_01013500_xaj_mz/xaj_mz_SCE_UA"
    Invoke-CalibEval "configs/xaj_snow_go_nogo_01013500.yaml" "results/xaj_snow_go_nogo/camels_01013500_xaj_snow/xaj_snow_SCE_UA"
    Invoke-CalibEval "configs/xaj_mz_go_nogo_14306500.yaml" "results/xaj_snow_go_nogo/camels_14306500_xaj_mz/xaj_mz_SCE_UA"
    Invoke-CalibEval "configs/xaj_snow_go_nogo_14306500.yaml" "results/xaj_snow_go_nogo/camels_14306500_xaj_snow/xaj_snow_SCE_UA"
}

if ($mode -eq "refine" -or $mode -eq "all") {
    Write-Host "=== Optional scipy NSE refine for XAJ-Snow + XAJ-MZ 01013500 (paired) ==="
    Invoke-CalibEval "configs/xaj_snow_go_nogo_01013500_refine_scipy.yaml" "results/xaj_snow_go_nogo/camels_01013500_xaj_snow_refine_scipy/xaj_snow_scipy"
    Invoke-CalibEval "configs/xaj_mz_go_nogo_01013500_refine_scipy.yaml" "results/xaj_snow_go_nogo/camels_01013500_xaj_mz_refine_scipy/xaj_mz_scipy"
}

Write-Host "=== Write diagnostics + HTML report from real CSV/JSON ==="
Invoke-Py scripts/generate_xaj_snow_go_nogo_report.py
"GO_NOGO_DONE mode=$mode" | Out-File "results/diagnostics/xaj_snow_go_nogo_status.txt" -Encoding utf8
Write-Host "Done. See results/diagnostics/xaj_snow_go_nogo.md and results/reports/xaj_snow_go_nogo_report.html"
