# XAJ-Snow large-N round delivery (local)

Generated from real CSV/JSON under `results/`. No fabricated metrics.
Python: `D:\miniforge3\envs\hydromodel\python.exe` (CPython 3.11/conda; netCDF4 OK). `HOME` = repo root.

## Progress by priority

| Priority | Status | Notes |
|----------|--------|-------|
| P0 refine_010_snow + mz | **Done** | scipy NSE refine after SCE-UA KGE medium |
| P0 rep budget {200,800,2000,5000} | **Partial** | 200+800 done both basins/models; **2000 for 01013500 done**; 5000 and 143@2000 **未运行** |
| P1 stratified freeze | **Done** | 80 basins frozen; paper target 500 documented |
| P2 batch paired calib | **Done (batch1)** | 14 CAMELS basins × 2 models @ rep=200 |
| P3 applicability | **Done** | CSV/MD/figures from batch1 |
| P4 factorial | **Skeleton only** | design doc; no code path change |

## Real numbers (sources cited)

### Refine @ camels_01013500 (test)

| model | NSE | KGE | RMSE | source |
|-------|----:|----:|-----:|--------|
| XAJ-Snow scipy refine | **0.8779** | **0.9374** | 0.7066 | `results/xaj_snow_go_nogo/camels_01013500_xaj_snow_refine_scipy/xaj_snow_scipy/evaluation_test/basins_metrics.csv` |
| XAJ-MZ scipy refine | **0.1393** | 0.0856 | 1.876 | `.../camels_01013500_xaj_mz_refine_scipy/xaj_mz_scipy/evaluation_test/basins_metrics.csv` |
| XAJ-Snow SCE-UA rep=800 | 0.7318 | 0.7764 | 1.0473 | go/no-go medium |
| XAJ-MZ SCE-UA rep=800 | −0.2321 | 0.2096 | 2.2446 | go/no-go medium |

### Rep budget (test NSE)

| basin | model | rep200 | rep800 | rep2000 | rep5000 |
|-------|-------|-------:|-------:|--------:|--------:|
| 01013500 | mz | −0.2321 | −0.2321 | **−0.3106** | 未运行 |
| 01013500 | snow | 0.5712 | 0.7318 | **0.7318** | 未运行 |
| 14306500 | mz | 0.7106 | 0.7106 | 未运行 | 未运行 |
| 14306500 | snow | 0.7043 | 0.7043 | 未运行 | 未运行 |

Source table: `results/diagnostics/rep_budget_sensitivity.csv`

Interpretation so far: on snowy 010, MZ plateaus at bad skill by rep=200 and remains poor at 2000; Snow improves 200→800 and does not further improve at 2000 under this protocol. On snow-free 143, Snow≈MZ and stable 200→800.

### Batch1 paired (rep=200, n=14)

Source: `results/diagnostics/batch1_paired_metrics.csv`

- snow≥0.1: n=9, **median ΔNSE = +0.546**
- snow<0.1: n=5, median ΔNSE = −0.007
- S2 (>0.3): n=5, **median ΔNSE = +0.584**

## Frozen sample

- Candidates: 15960 (all 7 regions, ts exists)
- Frozen: **80** (`results/sampling/sample_frozen.csv`, seed=20260816)
- Snow bins: S0=27, S1=35, S2=18
- Regions: hysets 38, camels 17, lamah 8, camelscl 7, camelsbr 6, camelsaus 2, camelsgb 2
- Batch1 executable subset: 14 CAMELS (`sample_batch1.csv`) — **all paired runs complete**

## New / modified files (this round)

Scripts/runners:
- `scripts/build_stratified_sample.py`
- `scripts/run_rep_budget_sensitivity.py`
- `scripts/run_batch_calibration.py`
- `scripts/analyze_applicability_first_look.py`
- `RUN_REP_BUDGET_SENSITIVITY.ps1`
- `RUN_BATCH_CALIBRATION.ps1`
- `RUN_P0_P2_FOLLOWON.ps1`
- `configs/xaj_mz_go_nogo_01013500_refine_scipy.yaml`
- `configs/xaj_snow_go_nogo_01013500_refine_scipy.yaml` (n_starts/maxiter trimmed)
- `RUN_GO_NOGO_XAJ_SNOW.ps1` (paired refine)
- `docs/local/factorial_optimizer_x_sharing_design.md`

Results:
- `results/sampling/*`
- `results/batch/metrics_summary.csv`, `results/batch/runs/**`, `results/batch/logs/**`
- `results/diagnostics/rep_budget_sensitivity.csv/.md`
- `results/diagnostics/applicability_first_look.csv/.md`
- `results/diagnostics/batch1_paired_metrics.csv`
- `results/diagnostics/large_n_long_run_commands.md`
- `results/diagnostics/large_n_round_delivery.md` (this file)
- `results/figures/fig_batch_delta_nse_*.png/.pdf`
- refine dirs under `results/xaj_snow_go_nogo/*_refine_scipy/`

Preserved: minicache overlap cleanup; `_deduplicate_basin_index`; no deletes of nc/zip/source.

## Incomplete + long-run commands

```powershell
cd d:\Projects\hydromodel-0.3.2\hydromodel-0.3.2
$env:HOME=$PWD; $env:USERPROFILE=$PWD
$env:HYDRO_SETTING_FILE=Join-Path $PWD hydro_setting.yml
$py='D:\miniforge3\envs\hydromodel\python.exe'

# Finish / extend rep budget
.\RUN_REP_BUDGET_SENSITIVITY.ps1 2000          # if 010 mid-run interrupted, resume-safe
.\RUN_REP_BUDGET_SENSITIVITY.ps1 5000

# Full freeze @ medium (hours–days)
.\RUN_BATCH_CALIBRATION.ps1 0 800 1

# Expand freeze toward 300–500
& $py scripts/build_stratified_sample.py --n-freeze 300 --seed 20260816 --per-region-cap 60
```

Details: `results/diagnostics/large_n_long_run_commands.md`

## Git

Public repo authorized for commit/push of code/docs/figures/publications/consultation and small diagnostics.
Exclude hydrodata / `_portable_data` / large NetCDF.
