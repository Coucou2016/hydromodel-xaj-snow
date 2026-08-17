# XAJ-Snow 论文多轮审稿记录（manuscript_review_rounds）

- 起始：2026-08-18（本地 UTC+8）
- 基线版本：v1.0（备份于 `results/publications/versions/v1.0_20260818_0210/`，git tip 2a464aa）
- ChatGPT 协作账号：pjn xdq（Pro），网页搜索已启用；全程文本交互，未上传附件。
- 备份规范：每轮修改前在 `results/publications/versions/` 建立 `vX.Y_YYYYMMDD_HHMM/`（6 文件 + CHANGELOG.md）；该目录为本地保留（已加入 .gitignore，避免公开仓 PDF 膨胀）。

---

## Round 1（2026-08-18 02:10–03:30）：创新性与定位审查

- ChatGPT 对话：https://chatgpt.com/c/6a835077-8718-83ea-9c3f-6a66b9c39b1c
- 原始回复：`docs/local/_chatgpt_raw_round2_novelty_positioning.txt`
- 备份：`results/publications/versions/v1.0_20260818_0210/`（修改前快照）

### 问题清单（ChatGPT 联网检索结论）

| ID | 问题 | 本地核验 | 处置 |
|----|------|----------|------|
| R1-1 | "minimal XAJ snow extension" 组件级新颖性已被 Chen 2025（dMXAJ, 531 CAMELS）消除 | 同意；与既有 L3c 核验一致 | **采纳**：Intro/Discussion 贡献改写为"受控过程必要性实验" |
| R1-2 | Wu 2025 已占用 "appropriate model complexity" 措辞 | 同意 | **采纳**：避免该措辞作为新颖性旗帜 |
| R1-3 | "diagnosis-first" 本身不再足够新颖（Wang 2026 WRR 事件型诊断已存在） | DOI 10.1029/2025WR040264 经 UFZ 索引页核验通过 | **采纳**：新增引用 N3；Intro 强调"配对干预实验+负对照"为其未覆盖要素 |
| R1-4 | 大样本雪梯度诊断已有先例（Liu 2025 WRR：640+171 CAMELS，雪比例分层） | DOI 10.1029/2024WR038873 核验通过（摘要含 snow fraction 退化） | **采纳**：新增引用 N4 |
| R1-5 | 多流域 CemaNeige 对比已是常规题材（Muñoz-Castro 2026 HESS 30, 825–848） | DOI 10.5194/hess-30-825-2026 核验通过（出版社页面） | **采纳**：新增引用 N2 |
| R1-6 | 暖期泛化/雪区诊断（Bohl 2026 HESS 30, 4667–4698）收窄"雪控制适用性"宽主张 | DOI 10.5194/hess-30-4667-2026 核验通过（出版社页面） | **采纳**：新增引用 N1 |
| R1-7 | Ouyang dXAJ 版本记录为 **2025**（JoH vol 649），正文原写 2024 | ScienceDirect vol 649 March 2025 核验 | **采纳**：引用年份改 2025（DOI 字符串保留 2024.132471） |
| R1-8 | Abstract/Intro 不应写 "publishes an applicability boundary"（回归未完成） | 同意（框架本就要求 pending 明示） | **采纳**：改为 "designs an applicability-domain estimate"；RQ3 改 "estimate applicability domain (continuous, with uncertainty)" |
| R1-9 | 负对照需统计化定义而非"目测接近零" | 同意；80 站完成后落地 | **采纳为承诺**：Discussion/Methods 措辞保留；统计定义列入待补充 |
| R1-10 | frac_snow=0.1 不得事后选为适用边界 | 同意 | **采纳**：正文仅作为 first-look 分层描述，边界估计待连续回归 |
| R1-11 | SciPy refine 是目标函数/优化器敏感性检查，非匹配实验副本 | 同意 | **采纳**：既有措辞已符合（"supplementary illustration"），保持 |
| R1-12 | Wang & Gupta 2026 arXiv 预印本（513 CAMELS-US 雪复杂度选择）投稿前需复查 | 无法本地核验全文（预印本） | **监控项**：不入引用，记入文献清单 N7 |

### 已落地修改

- `scripts/generate_publication_outputs.py`：Intro 定位段重写（新增 N1–N4 引用 + 贡献声明改写）；Discussion 定位段改写；Abstract 主张强度降级；RQ3 措辞；refs 新增 Bohl/Muñoz-Castro/Wang/Liu 4 条、Ouyang 年份修正为 2025。
- 重新生成 6 文件（HTML 校验 OK；PDF 经 headless Chrome 输出）。

### 否决项

| 顾问建议倾向 | 否决理由 |
|--------------|----------|
| 将 Mohammadi 2025（N5）加入正文引用 | 与本文问题域关联弱（混合 ML 预报），仅作背景核验记录，避免引用堆砌 |
| 因 Chen 2025 存在而进一步弱化 pilot 结果呈现 | 证据层级未变；pilot 表与图保持，仅贡献叙事收窄 |

### 备份与提交

- 修改前备份：`results/publications/versions/v1.0_20260818_0210/`
- Commit：（本轮提交后回填 hash）
