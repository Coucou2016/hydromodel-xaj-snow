# Applicability first look (batch1, n=14 paired)

- Source: `results/batch/metrics_summary.csv`（SCE-UA + KGE, **rep=200**, train/test 与 pilot 相同）
- Sample: `results/sampling/sample_batch1.csv`（CAMELS-US 14 站，含雪/无雪）
- Paired table: `results/diagnostics/batch1_paired_metrics.csv`

## 汇总（真实中位数）

| 分组 | n | med ΔNSE (snow−mz) | med NSE_snow | med NSE_mz |
|------|--:|-------------------:|-------------:|-----------:|
| 全部 | 14 | 0.0088 | 0.4118 | 0.0119 |
| frac_snow≥0.1 | 9 | **0.5461** | 0.5468 | −0.0734 |
| frac_snow<0.1 | 5 | −0.0068 | 0.3534 | 0.4739 |
| S2 (frac_snow>0.3) | 5 | **0.5835** | 0.5712 | 0.0119 |
| S0 (frac_snow<0.1) | 5 | −0.0068 | 0.3534 | 0.4739 |

## 解读

- 高雪档（S2）与中雪档中，多数站出现与 pilot 同向的大幅 ΔNSE（如 `10348850` +0.62、`09223000` +0.55、`04057800` +0.65、`01031500` +0.58、`01013500` +0.80 @rep=200）。
- 无雪对照 ΔNSE 接近 0 或略负，未见系统性虚假增益。
- 少数站两模型均失败（如 `14362250`、`05123400`），会拉低全样本中位数；论文主文应以分层中位数 + 失败筛除规则报告。

## Figures

- `results/figures/fig_batch_delta_nse_vs_frac_snow.png/.pdf`
- `results/figures/fig_batch_delta_nse_by_snow_bin.png/.pdf`
