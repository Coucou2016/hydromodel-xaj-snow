# XAJ-Snow 论文五轮审稿迭代 — 最终交付报告

- **日期**: 2026-08-18（UTC+8）
- **工作区**: `d:\Projects\hydromodel-0.3.2\hydromodel-0.3.2`
- **公开仓**: https://github.com/Coucou2016/hydromodel-xaj-snow （master，已 push，无 force push）
- **ChatGPT 协作**: pjn xdq（Pro），网页搜索已启用；全程文本交互，未上传附件；5 轮全部与 ChatGPT 完成，无限流替代轮。

---

## 1. 五轮总览（每轮做了什么、发现什么、如何解决）

| 轮次 | 主题 | 关键发现 | 解决方式 | Commit |
|------|------|----------|----------|--------|
| R1 | 创新性与定位 | 组件级新颖性已被 Chen 2025（dMXAJ, 531 CAMELS）等消除；"diagnosis-first" 被 Wang 2026 部分占用；Ouyang dXAJ 年份写错（2024→2025） | 贡献改写为"受控过程必要性实验"（配对干预+负对照+匹配预算）；新增 4 条经 DOI 核验的文献；禁止措辞（首次 XAJ 融雪/全球评估）全部不出现 | `8ee24ad` |
| R2 | 内容逻辑与结构 | RQ 缺适用域问题；Methods 缺采样/分箱/参数区间；Gthreshold 逐期重算未披露；batch1 表述像结论 | RQ 扩为 RQ1–RQ4 + 前瞻中性判据（±0.05）；重写 2.1 采样段 + 参数区间表；Gthreshold 披露+列待做敏感性；Results 重组 3.1–3.4，batch1 统一为 first-look evidence | `3887bd7` |
| R3 | 文字与学术表达 | 工程语（go/no-go、headroom）、口语（hug the diagonal）、片段句、斜杠堆叠、术语不统一 | 全篇 OVERWRITE 润色：pilot evaluation / exploratory screening / objective-sensitivity；25 组术语台账全篇执行；数字零改动 | `6d56f19` |
| R4 | 图片格式与 Figure 规范 | Fig.5 缺 (a)(b) panel label 与 1:1 图例；图内标题与图注重复；图注含仓库文件名/工程语 | 重绘 Fig.1–7（300 dpi、Okabe-Ito、Times New Roman 嵌入）；7 条图注重写为自包含学术表述；发现并修复重跑脚本导致的 CSV 数据回归 | `212b697` |
| R5 | 综合终审（模拟 HESS 审稿人） | 裁决 Major Revision：框架/文字/数字/图注近投稿质量，剩余障碍是证据完备性；Table Bias 未定义；5 条参考文献错误/意译；雪模块方程图示化；冻结样本未公开；14 站筛查非独立 | Bias 复算定义入 Methods；参考文献逐条联网核验修正；精确方程按源码写入；公开脱敏 80 站冻结样本+设计清单；筛查表述降级为"佐证性证据" | `060f393` + `1426d7d` |

## 2. 备份路径与 CHANGELOG 摘要

| 版本 | 路径 | 内容 |
|------|------|------|
| v1.0 | `results/publications/versions/v1.0_20260818_0210/` | 初始版（git tip 2a464aa） |
| v1.1 | `results/publications/versions/v1.1_20260818_0239/` | Round 2 修改前快照 |
| v1.2 | `results/publications/versions/v1.2_20260818_0320/` | Round 2 完成版 |
| v1.3 | `results/publications/versions/v1.3_20260818_0347/` | Round 3 润色完成版 |
| v1.4 | `results/publications/versions/v1.4_20260818_0420/` | Round 4 图片规范完成版 |
| v1.5 | `results/publications/versions/v1.5_20260818_0505/` | Round 5 修改前基线（与 v1.4 逐字节一致，即 ChatGPT 终审对象） |
| **v2.0** | `results/publications/versions/v2.0_20260818_0525/` | **最终版**（Round 5 全部修正落地） |

每份含 6 文件（manuscript html/md/pdf + report html/md/pdf）+ CHANGELOG.md（备份目录已 .gitignore，本地保留）。

## 3. ChatGPT 对话链接

- 唯一会话（5 轮续用）: https://chatgpt.com/c/6a835077-8718-83ea-9c3f-6a66b9c39b1c
- 原始回复存档: `docs/local/_chatgpt_raw_round2_novelty_positioning.txt`、`_chatgpt_raw_round3_content_logic.txt`、`_chatgpt_raw_round4_wording_polish.txt`、`_chatgpt_raw_round5_figure_audit.txt`、`_chatgpt_raw_round6_final_review.txt`

## 4. 被否决/修正的 ChatGPT 建议及证据

| 轮次 | 建议 | 处置 | 证据 |
|------|------|------|------|
| R1 | 引入 Mohammadi 2025 混合 ML 预报引用 | 否决 | 与问题域关联弱，避免引用堆砌 |
| R1 | 因 Chen 2025 进一步弱化 pilot 呈现 | 否决 | 证据层级未变；仅收窄叙事，表图保留 |
| R3 | 报告中文正文也改用英文术语台账 | 否决 | 台账仅约束论文；论文/报告边界规则 |
| R4 | Fig.2/3 春季阴影缺图内图例 | 否决（误判） | `_shade_spring()` 代码已有 "Mar–May" label；ChatGPT 无法读图 |
| R4 | 字体改 sans-serif；图文件改 f01–f07 | 延后 | Copernicus 原文仅 "consider"；命名是投稿打包动作 |
| R5 | 立即补完 RQ1–RQ4 全部实验/改投短文 | 延后为提交前门槛 | 属计算资源与时间约束；论文已如实声明 pending，不虚构完成 |
| R5 | Gthreshold 测试期协议改为已冻结 | 保留披露 | 冻结模型评价未完成，不得写成已完成（硬性约束） |

## 5. 最终版文件与 commit

- 论文: `results/publications/xaj_snow_manuscript.{html,md,pdf}`
- 报告: `results/publications/report.{html,md,pdf}`
- 备份: `results/publications/versions/v2.0_20260818_0525/`
- Commit: `060f393`（Round 5 主提交）+ `1426d7d`（日志 hash 回填），均已 push；工作树 clean。

## 6. 真实性确认

所有指标数字均来自真实 CSV/NetCDF，未编造：

- Table 2 全部 20 个指标值 ← 4 个 `basins_metrics.csv`（逐一比对一致）
- batch1 分层中位 +0.5461 / −0.0068 ← `results/diagnostics/batch1_paired_metrics.csv`
- rep=2000 敏感性 −0.3106 / 0.7318 ← `results/diagnostics/rep_budget_sensitivity.csv`
- Bias 定义经 NetCDF 反推 + 单位换算复算验证（mm d⁻¹ 均值偏差）
- Round 5 修改未新增/改动任何数值（仅措辞、定义、引用、可复现性文件）

## 7. 未验证风险

1. Wang & Gupta 2026 arXiv 预印本（513 CAMELS-US 雪复杂度选择）无法核验全文，未入引用，投稿前需复查。
2. Zenodo DOI 未铸造；Code/Data 段以"生成时快照提交"表述，投稿前必须铸造不可变存档。
3. 作者贡献/利益冲突/致谢为占位，投稿前必填。
4. ChatGPT 无法读图：Round 4 图规范审计基于本地图注+图内容描述转述，已用本地脚本（dpi/尺寸/字体）独立复验，但像素级视觉复核仍为人工抽查。
5. 证据完备性（R5 裁决核心）：80 站全量 medium、rep=5000、多 seed、固定雪参消融、SWE 一致性、适用域回归均未完成 —— 论文已如实标注 pending，这是投稿前的真正门槛。

## 8. Git 状态

- 分支 master，与 origin/master 同步（`Your branch is up to date`），工作树 clean。
- 本轮推送提交链: `2a464aa → 8ee24ad → 3887bd7 → 8f96318 → 6d56f19 → 212b697 → 060f393 → 1426d7d`（全部正常 push，无 force push）。
