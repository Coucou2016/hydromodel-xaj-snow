# 轮 A：InvalidIndexError 修复记录

**日期**：2026-05-22

## 现象

```
pandas.errors.InvalidIndexError: Reindexing only valid with uniquely valued Index objects
```

堆栈：`hydrodataset.Caravan._load_ts_dataset` → `open_mfdataset(..., concat_dim="basin")` → `read_ts_xrdataset` → `sel(basin=...)`

## 根因

`._cache_global_then_refine_v2/` 下存在多个 `caravan_camels_timeseries_batch_*.nc`，且**共享同一 basin**（例如 `camels_01013500` 同时出现在单站 batch 与 `01013500_14308990` 多站 batch）。沿 `basin` 拼接后 basin 坐标重复，`sel(basin=['camels_01013500'])` 失败。

验证（合并 3 个 batch 后）：

- `basin` 列表含重复 `camels_01013500`
- `ds.sel(basin=['camels_01013500'], ...)` → InvalidIndexError

## 修复

1. `scripts/build_caravan_minicache.py`：写入新 batch 后，删除 cache 目录中**任意 basin 与本次构建重叠**的旧 batch 文件。
2. `hydromodel/datasets/unified_data_loader.py`：`_deduplicate_basin_index()`，对合并结果按 basin 保留首次出现。
3. 重建 `camels_01013500` minicache；`load_data()` train/test 形状验证通过。

## 验证命令

```powershell
cd d:\Projects\hydromodel-0.3.2\hydromodel-0.3.2
$env:HOME = (Get-Location).Path
$env:HYDRO_SETTING_FILE = "$PWD\hydro_setting.yml"
python scripts/build_caravan_minicache.py --data-root "_portable_data/datasets-origin" --region-folder camels --basin-id camels_01013500 --cache-dir "_portable_data/.cache_global_then_refine_v2"
```
