# XAJ-Snow large-N: long-run commands

All commands from repo root `d:\Projects\hydromodel-0.3.2\hydromodel-0.3.2`.
Use hydromodel conda Python (or CPython 3.12 with netCDF4). Set `HOME` to repo root.

```powershell
cd d:\Projects\hydromodel-0.3.2\hydromodel-0.3.2
$env:HOME = $PWD
$env:USERPROFILE = $PWD
$env:HYDRO_SETTING_FILE = Join-Path $PWD "hydro_setting.yml"
$py = "D:\miniforge3\envs\hydromodel\python.exe"
```

## Already completed locally (this round)

- P0 refine: `.\RUN_GO_NOGO_XAJ_SNOW.ps1 refine` (snow+mz scipy)
- P1 freeze: `python scripts/build_stratified_sample.py --n-freeze 80`
- P0/P2 follow-on chain: `.\RUN_P0_P2_FOLLOWON.ps1` (rep=200 + batch1 limit6)

## Remaining long runs

### Rep budget higher tiers (may take many hours)

```powershell
.\RUN_REP_BUDGET_SENSITIVITY.ps1 2000
.\RUN_REP_BUDGET_SENSITIVITY.ps1 5000
# or both:
.\RUN_REP_BUDGET_SENSITIVITY.ps1 2000,5000
```

Estimated wall time (single worker, ~1.2 s/eval): rep=2000 ≈ 4 basins×models ≈ 4–6 h; rep=5000 ≈ 10–15 h.

### Full freeze sample @ medium budget (rep=800)

```powershell
.\RUN_BATCH_CALIBRATION.ps1 0 800 1
```

80 basins × 2 models × ~30 min ≈ **80 h** serial. Prefer workers=2 overnight if CPU allows:

```powershell
.\RUN_BATCH_CALIBRATION.ps1 0 800 2
```

### Expand freeze toward paper N (300–500)

```powershell
& $py scripts/build_stratified_sample.py --n-freeze 300 --seed 20260816 --per-region-cap 60
.\RUN_BATCH_CALIBRATION.ps1 0 800 2
```

### Finish rest of batch1 (14 CAMELS basins) at rep=200 or 800

```powershell
& $py scripts/run_batch_calibration.py --python $py --sample-csv results/sampling/sample_batch1.csv --rep 200 --workers 1 --skip-minicache
# or medium:
& $py scripts/run_batch_calibration.py --python $py --sample-csv results/sampling/sample_batch1.csv --rep 800 --workers 1 --skip-minicache
```

Resume is automatic when `evaluation_test/basins_metrics.csv` exists.
