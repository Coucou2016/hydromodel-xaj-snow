# CAMELS-US 解压与对照实验（轮次 4）

## 当前状态

- Zip 完整目录：`d:\Projects\hydromodel-0.3.2\hydrodata\camels_us\`
- 关键包：`basin_timeseries_v1p2_metForcing_obsFlow.zip`（~3.17 GB）及其他 `basin_timeseries_v1p2_modelOutput_*.zip`
- **未**解压到 `_portable_data/datasets-origin/CAMELS_US`（本轮未执行，避免长时间 IO 占用）

## 阻塞原因

- 解压约需数 GB 额外磁盘与 10–30+ 分钟（视磁盘而定）
- 便携率定主线已用 CARAVAN 内嵌 CAMELS 子集，CAMELS-US 原生 zip 为 **可选对照**

## 建议命令（不删除 zip）

```powershell
$repo = "d:\Projects\hydromodel-0.3.2\hydromodel-0.3.2"
$dest = Join-Path $repo "_portable_data\datasets-origin\CAMELS_US"
New-Item -ItemType Directory -Path $dest -Force
Expand-Archive -Path "d:\Projects\hydromodel-0.3.2\hydrodata\camels_us\basin_timeseries_v1p2_metForcing_obsFlow.zip" -DestinationPath $dest
# 其余 modelOutput zip 同理，或运行：
# conda run -n hydromodel python scripts/portable_download_camels_us.py --extract-only
```

解压后可在 `hydro_setting.yml` 增加 `CAMAVAN_US` 路径注释，并新建 `configs/portable_camels_us_quick.yaml` 对照跑 01013500。
