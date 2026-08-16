# SCE-UA rep budget sensitivity

Purpose: show that XAJ-MZ underperformance on snowy `camels_01013500` is not from under-budgeting,
and that XAJ-Snow gains are not an artifact of the two extra snow degrees of freedom alone.

Protocol: SCE-UA + KGE; train 1985-10-01–1995-09-30; test 2005-10-01–2014-09-30; warmup=365.
All metrics from `evaluation_test/basins_metrics.csv` (no fabricated values).

| basin | model | rep | NSE | KGE | RMSE | status | source |
|---|---|---:|---:|---:|---:|---|---|
| camels_01013500 | xaj_mz | 200 | -0.2321245371072648 | 0.2096317130340879 | 2.244620266134258 | ok | existing_or_missing |
| camels_01013500 | xaj_mz | 800 | -0.2321245371072648 | 0.2096317130340879 | 2.244620266134258 | ok | reused:results/xaj_snow_go_nogo/camels_01013500_xaj_mz/xaj_mz_SCE_UA |
| camels_01013500 | xaj_mz | 2000 |  |  |  | 未运行 | existing_or_missing |
| camels_01013500 | xaj_mz | 5000 |  |  |  | 未运行 | existing_or_missing |
| camels_01013500 | xaj_snow | 200 | 0.5711896977031736 | 0.7105411778039608 | 1.3241835302517266 | ok | existing_or_missing |
| camels_01013500 | xaj_snow | 800 | 0.7317827747222032 | 0.7763659545980491 | 1.0472705938971414 | ok | reused:results/xaj_snow_go_nogo/camels_01013500_xaj_snow/xaj_snow_SCE_UA |
| camels_01013500 | xaj_snow | 2000 |  |  |  | 未运行 | existing_or_missing |
| camels_01013500 | xaj_snow | 5000 |  |  |  | 未运行 | existing_or_missing |
| camels_14306500 | xaj_mz | 200 | 0.710633808785872 | 0.7815253308984131 | 3.056478899381416 | ok | existing_or_missing |
| camels_14306500 | xaj_mz | 800 | 0.710633808785872 | 0.7815253308984131 | 3.056478899381416 | ok | reused:results/xaj_snow_go_nogo/camels_14306500_xaj_mz/xaj_mz_SCE_UA |
| camels_14306500 | xaj_mz | 2000 |  |  |  | 未运行 | existing_or_missing |
| camels_14306500 | xaj_mz | 5000 |  |  |  | 未运行 | existing_or_missing |
| camels_14306500 | xaj_snow | 200 | 0.7043457944069262 | 0.7795303849818098 | 3.0895095253500573 | ok | existing_or_missing |
| camels_14306500 | xaj_snow | 800 | 0.7043457944069262 | 0.7795303849818098 | 3.0895095253500573 | ok | reused:results/xaj_snow_go_nogo/camels_14306500_xaj_snow/xaj_snow_SCE_UA |
| camels_14306500 | xaj_snow | 2000 |  |  |  | 未运行 | existing_or_missing |
| camels_14306500 | xaj_snow | 5000 |  |  |  | 未运行 | existing_or_missing |

## Notes
- `rep=800` rows reuse the go/no-go medium runs when present.
- If higher `rep` cells are empty/`未运行`, see `RUN_REP_BUDGET_SENSITIVITY.ps1` long-run command.
