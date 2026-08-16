# Applicability first look (batch)

- Source metrics: `results/batch/metrics_summary.csv`（真实 SCE-UA rep=200 小批次）
- Paired basins with both models: **6**（`sample_batch1.csv` 的前 6 站；偏无雪/中雪，尚未含 S2_gt0.3）
- Median ΔNSE (snow−mz) overall: `-0.0640`
- Snowy (frac_snow≥0.1) n=2 median ΔNSE=`-0.8653` median NSE_snow=`-1.2726` median NSE_mz=`-0.4074`
- Low-snow (frac_snow<0.1) n=4 median ΔNSE=`-0.0640` median NSE_snow=`0.2037` median NSE_mz=`0.2674`

## 单站要点（来自同一 CSV）

| basin | frac_snow | NSE_mz | NSE_snow | ΔNSE |
|-------|----------:|-------:|---------:|-----:|
| camels_04057800 | 0.291 | 0.042 | 0.689 | **+0.647** |
| camels_03368000 | 0.071 | 0.474 | 0.470 | -0.004 |
| camels_02149000 | 0.000 | 0.475 | 0.353 | -0.121 |
| camels_08086290 | 0.000 | 0.061 | 0.054 | -0.007 |
| camels_05123400 | 0.216 | -0.856 | -3.234 | -2.377（两模型均失败） |
| camels_14362250 | 0.000 | -20.4 | -27.0 | -6.55（两模型均崩溃） |

解读：中雪站 `04057800` 出现与 pilot 同向的大幅增益；无雪站大体中性/略负；整体中位数被两失败站拉低——需在后续批次强制纳入 S2 并提高 rep（800）后再下结论。

## Region counts

region_folder
camels    6

## Figures

- `results/figures/fig_batch_delta_nse_vs_frac_snow.png`
- `results/figures/fig_batch_delta_nse_by_snow_bin.png`

## Data table
`results/diagnostics/applicability_first_look.csv`
