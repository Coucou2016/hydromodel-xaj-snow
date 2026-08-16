# XAJ-Snow 论文方案追踪笔记

更新时间：2026-08-16（medium go/no-go 完成后刷新）。

## 1. 问题与假说

- 难流域 `camels_01013500`：`frac_snow≈0.37`，既有 XAJ-MZ 测试 NSE≈**0.139**（`results/multi_basin_global_then_refine_v2/.../xaj_mz_scipy`）。
- 好流域 `camels_14306500`：`frac_snow≈0`，NSE≈**0.801**（同协议族 scipy）。
- 人类活动解释已否定：hft 30.6 vs 34.3。
- **假说**：01013500 失效是因为 XAJ **无融雪**，降雪被当降雨立刻产流。
- **判据**：同一率定协议下 XAJ-Snow vs XAJ-MZ；若 NSE 明显提升（理想 >0.5）则全速推进；若几乎无增益则转向率定协议/区域化。

## 2. 本轮代码改动

| 文件 | 作用 |
|------|------|
| `hydromodel/datasets/unified_data_loader.py` | VAR_MAPPING 增加 temperature；有 T 时 p_and_e 为 3 特征，无 T 仍为 2 特征 |
| `scripts/build_caravan_minicache.py` | 写入 `temperature_2m_mean`；保留 basin 去重 |
| `hydromodel/models/snow.py` | CemaNeige **式**度日模块（Valéry 2014 / airGR；日尺度、集总 1 带） |
| `hydromodel/models/xaj_snow.py` | 融雪后调用 `xaj(..., name="xaj_mz")`；无 T 报错 |
| `hydromodel/models/model_dict.py` / `model_config.py` | 注册 `xaj_snow`（15+Kf+CTG） |
| `configs/xaj_*_go_nogo_*.yaml` | 01013500 / 14306500 成对配置 |
| `RUN_GO_NOGO_XAJ_SNOW.ps1` | HOME=仓库根；smoke → medium → 可选 refine；容忍 Python stderr 警告 |
| `test/test_snow.py` | 质量守恒、无雪、全雪、单峰融雪、无 T 报错（8 PASSED） |
| `scripts/generate_xaj_snow_go_nogo_report.py` | 从真实 CSV 写 md/html，含负对照判据 |
| `scripts/build_xaj_snow_stratified_sample.py` | 分层抽样骨架，不跑 300 流域率定 |
| `docs/local/chatgpt_consultation_xaj_snow.md` | 顾问对话 A 记录 + 本地核验 |

## 3. 率定协议

- train: 1985-10-01–1995-09-30；test: 2005-10-01–2014-09-30；warmup 365
- smoke：SCE-UA KGE rep=120（只验证 pipeline）
- medium（go/no-go 数字）：SCE-UA KGE **rep=800**, ngs=15（与 v2 stage-1 同级）
- 可选：scipy NSE 精修（`configs/xaj_snow_go_nogo_01013500_refine_scipy.yaml`）

## 4. Go/no-go 真实指标（medium，禁止混比不同协议）

数字以 `results/diagnostics/xaj_snow_go_nogo.md` 为准。

| 流域 | 模型 | rep | NSE | KGE | RMSE |
|------|------|-----|-----|-----|------|
| 01013500 | XAJ-MZ | 800 | **-0.2321** | 0.2096 | 2.2446 |
| 01013500 | XAJ-Snow | 800 | **0.7318** | 0.7764 | 1.0473 |
| 14306500 | XAJ-MZ | 800 | 0.7106 | 0.7815 | 3.0565 |
| 14306500 | XAJ-Snow | 800 | 0.7043 | 0.7795 | 3.0895 |

01013500 最优雪参（denorm）：**Kf≈3.50** mm/°C/day（典型 2–6 内），**CTG≈0.116**（未贴 0/1 边）。

历史对照（不同协议，仅背景，不作 Δ）：v2 scipy 010 mz NSE=0.139；143 mz NSE=0.801。

## 5. 结论与建议

- **工程 GO**：同一 SCE-UA+KGE 协议下，雪区 ΔNSE≈+0.96；无雪负对照 ΔNSE≈−0.006。
- **论文措辞**：写 *CemaNeige-style / single-band*，勿写严格复现 airGR（雨雪带 Ts=0/Tr=1 ≠ airGR 默认 −1～+3）。
- **下一步**：`python scripts/build_xaj_snow_stratified_sample.py` 做分层名单；可选 `.\RUN_GO_NOGO_XAJ_SNOW.ps1 refine`；再规划批量，不要本轮强行 300 流域长率定。
- 仍须诚实：17 vs 15 参数；无 SWE 观测时 Kf/CTG 为有效参数。

## 6. 局限（诚实记录）

- 本实现是 **集总 1 个高程带**，不是 airGR 默认 5 带。Caravan 提供流域平均气温。
- 雨雪分割用 Ts=0°C、线性带宽 Tr=1°C（仅 Tmean 时的常用做法，非 airGR 默认）。
- Kf 搜索 [0, 10] mm/°C/day，CTG [0, 1]。
- Gthreshold 由当前 forcing 序列估计（未从率定期冻结到验证期）。

## 7. 命令

```powershell
cd d:\Projects\hydromodel-0.3.2\hydromodel-0.3.2
$env:HOME = (Get-Location).Path
$env:HYDRO_SETTING_FILE = Join-Path $env:HOME "hydro_setting.yml"
.\RUN_GO_NOGO_XAJ_SNOW.ps1 smoke
.\RUN_GO_NOGO_XAJ_SNOW.ps1 medium
.\RUN_GO_NOGO_XAJ_SNOW.ps1 refine   # 可选长跑
python scripts/generate_xaj_snow_go_nogo_report.py
python -m pytest test/test_snow.py -v
```

ChatGPT 对话 A：https://chatgpt.com/c/6a809e28-e688-83ea-b69d-17f7826ecf72
