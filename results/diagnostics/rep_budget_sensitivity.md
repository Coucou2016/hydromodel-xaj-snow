# SCE-UA rep budget sensitivity

Purpose: show that XAJ-MZ underperformance on snowy `camels_01013500` is not from under-budgeting,
and that XAJ-Snow gains are not an artifact of the two extra snow degrees of freedom alone.

Protocol: SCE-UA + KGE; train 1985-10-01–1995-09-30; test 2005-10-01–2014-09-30; warmup=365.
All metrics from `evaluation_test/basins_metrics.csv` (no fabricated values).

| basin | model | rep | NSE | KGE | RMSE | status | source |
|---|---|---:|---:|---:|---:|---|---|
| camels_01013500 | xaj_mz | 2000 | -0.3105604076749977 | 0.2071252384913505 | 2.314963236077462 | ok | new_run |
| camels_01013500 | xaj_snow | 2000 | 0.7317827747222032 | 0.7763659545980491 | 1.0472705938971414 | ok | new_run |

## Notes
- `rep=800` rows reuse the go/no-go medium runs when present.
- If higher `rep` cells are empty/`未运行`, see `RUN_REP_BUDGET_SENSITIVITY.ps1` long-run command.
