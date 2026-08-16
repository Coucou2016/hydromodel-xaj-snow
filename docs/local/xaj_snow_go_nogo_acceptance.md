# 最终验收报告：XAJ-Snow go/no-go

日期：2026-08-16  
执行者：Cursor 本地代理（唯一落地）  
顾问：ChatGPT Pro（仅文本粘贴，无附件）

## 1. 仓库基线

| 项 | 值 |
|----|-----|
| 工作区 | `d:\Projects\hydromodel-0.3.2\hydromodel-0.3.2` |
| 分支 | `master` |
| Commit | **尚无首次 commit**（`fatal: no commits yet`） |
| Git 状态 | **仅本地未提交**：大量 untracked + 少量 staged；**未** commit / push / PR |
| HOME / 配置 | 运行时 `HOME`=仓库根，`hydro_setting.yml` → `_portable_data` |

## 2. 任务完成对照

| 验收项 | 状态 | 证据 |
|--------|------|------|
| xaj_mz 向后兼容 | PASS | medium 010/143 均可率定评价；2 特征路径保留 |
| xaj_snow 加载气温并率定 | PASS | minicache `temperature_2m_mean`；smoke+medium |
| 010 / 143 真实对比数字 | PASS | 见下表；CSV 在 `results/xaj_snow_go_nogo/**/evaluation_test/` |
| 单元测试 | PASS | `pytest test/test_snow.py` → **8 passed**（两次复跑） |
| docs/local 笔记 | PASS | `paper_plan_xaj_snow.md`、`chatgpt_consultation_xaj_snow.md` |
| HTML/MD 报告真实数字 | PASS | `results/diagnostics/xaj_snow_go_nogo.md`、`results/reports/xaj_snow_go_nogo_report.html` |

## 3. 真实测试期指标（SCE-UA + KGE，rep=800）

协议：train 1985-10-01–1995-09-30；test 2005-10-01–2014-09-30；warmup=365。

| basin | model | NSE | KGE | RMSE |
|-------|-------|-----|-----|------|
| 01013500 | XAJ-MZ | **-0.2321** | 0.2096 | 2.2446 |
| 01013500 | XAJ-Snow | **0.7318** | 0.7764 | 1.0473 |
| 14306500 | XAJ-MZ | 0.7106 | 0.7815 | 3.0565 |
| 14306500 | XAJ-Snow | 0.7043 | 0.7795 | 3.0895 |

- 010 ΔNSE ≈ **+0.964**；最优 **Kf≈3.50**，**CTG≈0.116**（未贴边）。
- 143 ΔNSE ≈ **-0.006**（负对照无虚假大增益）。
- smoke（rep=120）010 snow NSE=0.436 已预示方向；medium 进一步放大。
- **勿**把历史 v2 scipy NSE（010=0.139 / 143=0.801）与本表混算 Δ。

## 4. 判据结论

**工程 GO（全速推进 XAJ-Snow 分层/批量）**。  
融雪假说在本成对协议下获**强支持**；论文总体泛化结论仍须分层多流域。

## 5. ChatGPT 对话

| 对话 | URL | 用途 |
|------|-----|------|
| A+B（同线程） | https://chatgpt.com/c/6a809e28-e688-83ea-b69d-17f7826ecf72 | 公式/接口审阅；medium 解读与审稿风险 |
| 本地核验笔记 | `docs/local/chatgpt_consultation_xaj_snow.md` | 顾问建议 vs 源码对照；否决项 |

## 6. 否决 / 未做项

| 项 | 原因 |
|----|------|
| git commit / push / PR | 硬性禁止 |
| 改雨雪带为 airGR −1～+3°C | 破坏与 smoke/medium 可比；改用 *CemaNeige-style* 措辞 |
| 本轮 300 流域长率定 | 计划禁止；先分层名单 |
| scipy refine | 可选未跑；命令见下 |
| 上传附件到 ChatGPT | 禁止 |

## 7. 本轮关键关键修复

- `RUN_GO_NOGO_XAJ_SNOW.ps1`：`$ErrorActionPreference=Continue` + `Invoke-Py`，避免 Python stderr `UserWarning` 被 PowerShell 当成致命错误中断 medium。
- 报告判据加入 143 负对照 ΔNSE 叙述。

## 8. 测试命令（可复现）

```powershell
cd d:\Projects\hydromodel-0.3.2\hydromodel-0.3.2
$env:HOME = (Get-Location).Path
$env:HYDRO_SETTING_FILE = Join-Path $env:HOME "hydro_setting.yml"
D:\miniforge3\envs\hydromodel\python.exe -m pytest test/test_snow.py -v
.\RUN_GO_NOGO_XAJ_SNOW.ps1 smoke
.\RUN_GO_NOGO_XAJ_SNOW.ps1 medium
.\RUN_GO_NOGO_XAJ_SNOW.ps1 refine   # 可选长跑
D:\miniforge3\envs\hydromodel\python.exe scripts/generate_xaj_snow_go_nogo_report.py
D:\miniforge3\envs\hydromodel\python.exe scripts/build_xaj_snow_stratified_sample.py
```

## 9. 建议下一步（不自动执行）

1. 分层抽样骨架 → 少量 0/低/中/高雪 gate  
2. 可选 `refine`（scipy NSE）作补充展示  
3. 论文 Methods 固定 *single-band CemaNeige-style* 措辞  
4. 用户明确要求后再 git commit
