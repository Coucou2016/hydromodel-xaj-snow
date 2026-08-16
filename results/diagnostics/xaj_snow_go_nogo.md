# XAJ-Snow go/no-go 诊断

- 生成时间：2026-08-16 11:11（表内 medium 指标）；2026-08-17 复核 refine 行
- 指标均来自 `evaluation_test/basins_metrics.csv`，禁止口算编造。
- 训练期 1985-10-01–1995-09-30；测试期 2005-10-01–2014-09-30；warmup=365。
- 主线目标函数：SCE-UA + KGE。historical 对照为 v2 scipy(NSE) 精修。
- 绘图样式：SciencePlots styles: science + no-latex; serif font in use: Times New Roman; PNG dpi>=300; PDF fonttype=42 (editable).

## 假说

01013500（frac_snow≈0.37）XAJ-MZ 差是因为无融雪、降雪被当降雨立刻产流；
14306500（frac_snow≈0）为负对照。人类活动解释已否定（hft 30.6 vs 34.3）。

## 测试期指标

| key | basin | model | rep | NSE | KGE | RMSE | 来源 |
|-----|-------|-------|-----|-----|-----|------|------|
| hist_010_mz_scipy | camels_01013500 | XAJ-MZ (historical scipy) | v2 refine | 0.1393 | 0.0856 | 1.8760 | `results/multi_basin_global_then_refine_v2/camels_01013500/xaj_mz_scipy/evaluation_test/basins_metrics.csv` |
| smoke_010_mz | camels_01013500 | XAJ-MZ smoke | 120 | -0.2321 | 0.2096 | 2.2446 | `results/xaj_snow_go_nogo/smoke_camels_01013500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/basins_metrics.csv` |
| smoke_010_snow | camels_01013500 | XAJ-Snow smoke | 120 | 0.4364 | 0.7059 | 1.5181 | `results/xaj_snow_go_nogo/smoke_camels_01013500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/basins_metrics.csv` |
| med_010_mz | camels_01013500 | XAJ-MZ | 800 | -0.2321 | 0.2096 | 2.2446 | `results/xaj_snow_go_nogo/camels_01013500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/basins_metrics.csv` |
| med_010_snow | camels_01013500 | XAJ-Snow | 800 | 0.7318 | 0.7764 | 1.0473 | `results/xaj_snow_go_nogo/camels_01013500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/basins_metrics.csv` |
| refine_010_snow | camels_01013500 | XAJ-Snow scipy refine | scipy | 0.8779 | 0.9374 | 0.7066 | `results/xaj_snow_go_nogo/camels_01013500_xaj_snow_refine_scipy/xaj_snow_scipy/evaluation_test/basins_metrics.csv` |
| refine_010_mz | camels_01013500 | XAJ-MZ scipy refine | scipy | 0.1393 | 0.0856 | 1.8760 | `results/xaj_snow_go_nogo/camels_01013500_xaj_mz_refine_scipy/xaj_mz_scipy/evaluation_test/basins_metrics.csv` |
| hist_143_mz_scipy | camels_14306500 | XAJ-MZ (historical scipy) | v2 refine | 0.8014 | 0.6598 | 2.5323 | `results/multi_basin_global_then_refine_v2/camels_14306500/xaj_mz_scipy/evaluation_test/basins_metrics.csv` |
| med_143_mz | camels_14306500 | XAJ-MZ | 800 | 0.7106 | 0.7815 | 3.0565 | `results/xaj_snow_go_nogo/camels_14306500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/basins_metrics.csv` |
| med_143_snow | camels_14306500 | XAJ-Snow | 800 | 0.7043 | 0.7795 | 3.0895 | `results/xaj_snow_go_nogo/camels_14306500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/basins_metrics.csv` |

## 判据结论

**GO（全速推进 XAJ-Snow）**：01013500 XAJ-Snow NSE=0.732，对照 XAJ-MZ NSE=-0.232（Δ=+0.964），达到 >0.5 且明显提升。 负对照 14306500：XAJ-Snow NSE=0.704 vs XAJ-MZ 0.711（Δ=-0.006），无明显虚假提升。

## 下一步命令

见 `results/diagnostics/large_n_long_run_commands.md`（报告可记工程命令；论文勿堆砌）。
