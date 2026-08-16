# camels_01013500 率定迭代记录

更新：2026-05-22（短期计划轮次 3）

## 配置与 dry-run

| 配置 | 状态 |
|------|------|
| `configs/real_caravan_camels_01013500_extended_sceua.yaml` | **新建**（rep=3500, loss=KGE）；`run_xaj_calibration.py --dry-run` 通过 |
| `configs/real_caravan_camels_01013500_extended_refine_scipy.yaml` | **新建**（n_starts=3, warm-start 自 extended SCE-UA） |
| `configs/real_caravan_camels_01013500_stronger.yaml` | 已有（rep=3000）；**尚无** `results/real_caravan_camels_01013500_stronger/` 输出 |

## 测试期 NSE / KGE 对比（已有结果，未编造新跑）

| 实验目录 | 算法 | NSE | KGE |
|----------|------|-----|-----|
| `multi_basin_quick_diag/.../xaj_mz_scipy` | scipy NSE (30 iter) | 0.138 | 0.083 |
| `multi_basin_global_then_refine_v2/.../xaj_mz_SCE_UA` | SCE-UA → | （见同目录 scipy） | |
| `multi_basin_global_then_refine_v2/.../xaj_mz_scipy` | scipy refine | **0.139** | 0.086 |
| `real_caravan_camels_01013500/.../xaj_mz_SCE_UA` | SCE-UA | 0.138 | 0.083 |
| `real_caravan_camels_01013500_kge_medium/.../xaj_mz_SCE_UA` | SCE-UA KGE | **-0.232** | 0.210 |
| `real_caravan_camels_01013500_refine_scipy/.../xaj_mz_scipy` | scipy NSE | **0.139** | 0.086 |
| `real_caravan_camels_01013500_refine_scipy_nsekge/...` | scipy NSEKGE | 0.133 | 0.090 |
| `real_caravan_camels_01013500_refine_scipy_lognse/...` | logNSE | 0.041 | -0.014 |
| `real_caravan_camels_01013500_refine_scipy_era5pet/...` | ERA5 PET | 0.106 | 0.069 |
| `extended_sceua_smoke/.../xaj_mz_SCE_UA` | SCE-UA KGE rep=80（pipeline 验证） | **-0.381** | 0.183 |

**Best 已有 NSE**：约 **0.139**（`multi_basin_global_then_refine_v2` Stage-2 scipy）。smoke 仅验证闭环，指标不代表 full rep。（`multi_basin_global_then_refine_v2` Stage-2 scipy）。KGE 单独优化未改善 NSE。

## 率定运行说明（2026-05-22 更新）

1. minicache：`hydro_setting.yml` → `cache: ./_portable_data/.cache_global_then_refine_v2`
2. **InvalidIndexError 根因（已修复）**：多个 `caravan_camels_timeseries_batch_*.nc` 被 hydrodataset 沿 `basin` 拼接，同一测站出现两次 → `sel(basin=...)` 失败。
   - 修复：`scripts/build_caravan_minicache.py` 构建后删除含重叠 basin 的旧 batch；`unified_data_loader._deduplicate_basin_index` 防御性去重。
3. **pipeline 验证**：`configs/*_smoke.yaml`（SCE-UA rep=80 → scipy）+ `run_xaj_evaluate.py`；日志 `results/diagnostics/smoke_*.log`
4. 长跑（rep=3500）：

```powershell
cd d:\Projects\hydromodel-0.3.2\hydromodel-0.3.2
.\RUN_EXTENDED_01013500_SCEUA.ps1
```

脚本已含 minicache 重建、率定、**evaluate 测试期**、HTML 报告生成命令见 `scripts/generate_iteration_html_report.py`。

## 对照流域（14306500）

- 同配置族下测试 NSE ≈ **0.80**（`multi_basin_global_then_refine_v2`），见 `basin_alignment_01013500_vs_14306500.md`。
