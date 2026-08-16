# 本地数据源与重复副本说明

> 生成日期：2026-05-22（短期计划轮次 1 自我审查）

## CARAVAN：单一真源（运行用）

| 路径 | 角色 | 规模（约） | 说明 |
|------|------|------------|------|
| `_portable_data/datasets-origin/CARAVAN` | **真源（推荐）** | 16052 文件 / ~65 GB | 标准布局：`attributes/`、`timeseries/netcdf/camels/`。`hydro_setting.yml` 指向此处。 |
| `../hydrodata/Caravan/usr/local/.../Caravan-Jan25-nc` | 外部解压副本 | 16054 文件 / ~81 GB | 与真源 **内容一致**（抽样 `camels_01013500.nc` SHA256 前缀均为 `4DA8347FD7553CA5`），目录更深。 |
| `../hydrodata/Caravan/Caravan-nc.tar.xz` | 归档 | — | 未删除；仅作备份/再解压用。 |

**结论**：两处 NetCDF 为同一数据集的不同挂载/解压布局，**不要删除任一副本**。便携运行只读 `_portable_data/datasets-origin/CARAVAN`。

`RUN_CARAVAN_CAMELS_MULTI_BASIN_DIAG.ps1` 曾用 junction 将外部路径链到 `_portable_data/.../CARAVAN/Caravan/Caravan`；当前仓库内已是完整真源树，无需 junction 亦可运行。

### Windows 可选 junction（仅当只保留外部副本时）

```powershell
# 在仓库根目录执行；勿删除 hydrodata 副本
New-Item -ItemType Junction -Path "_portable_data\datasets-origin\CARAVAN\Caravan\Caravan" `
  -Target "..\hydrodata\Caravan\usr\local\google\home\kratzert\Data\Caravan-Jan25-nc"
```

## CAMELS-US

| 路径 | 状态 |
|------|------|
| `../hydrodata/camels_us/*.zip` | 已完整（含 `basin_timeseries_v1p2_metForcing_obsFlow.zip` ~3.17 GB） |
| `_portable_data/datasets-origin/CAMELS_US` | **未解压**（见 `docs/local/camels_us_next_steps.md`） |

## 结果与缓存

- 率定输出：`results/`（已 `.gitignore`）
- 迷你缓存：`_portable_data/.cache*`（已 `.gitignore`）
- **运行前**：`hydrodataset` 在 import 时只读 `Path.home()/hydro_setting.yml`，须像 `RUN_REAL_CARAVAN_EXTERNAL_CAMELS_01013500.ps1` 一样把 `HOME`/`USERPROFILE` 设为仓库根目录；并对目标流域执行 `build_caravan_minicache.py --cache-dir _portable_data/.cache_global_then_refine_v2`

## 父目录 `hydrodata/`

位于 `d:\Projects\hydromodel-0.3.2\hydrodata\`（仓库上一级），与项目内 `_portable_data` 并行存放多国 CAMELS 与 Caravan；**不纳入 git**。
