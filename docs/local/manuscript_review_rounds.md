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
- Commit：`8ee24ad`（已 push 至 origin/master）

---

## Round 2（2026-08-18 02:39–03:30）：内容逻辑与结构审查

- ChatGPT 对话：https://chatgpt.com/c/6a835077-8718-83ea-9c3f-6a66b9c39b1c（续用同一会话）
- 原始回复：`docs/local/_chatgpt_raw_round3_content_logic.txt`
- 修改前备份：`results/publications/versions/v1.1_20260818_0239/`（git tip 8ee24ad）
- 修改后备份：`results/publications/versions/v1.2_20260818_0320/`

### 问题清单与处置

| ID | ChatGPT 意见 | 本地核验 | 处置 |
|----|--------------|----------|------|
| R2-1 | Intro 缺口后重复定位（L55/L58/L63–65 三次表达同一区分） | 属实 | **采纳**：三段 "Relative to..." 压缩为一句 |
| R2-2 | Intro "mis-time spring peaks" 无对应定量时序诊断 | 属实（无峰值时序指标） | **采纳**：改 "can misrepresent seasonal storage and runoff timing" |
| R2-3 | "necessary for structural adequacy" 过强；"high-capacity learner" 对比多余 | 属实 | **采纳**：删除，定位句重写 |
| R2-4 | RQ2 无操作性中立定义；RQ3 混合两个推断问题 | 属实 | **采纳**：新增先验中立判据（\|ΔNSE\|≤0.05 且 \|ΔKGE\|≤0.05，§2.5）；RQ3 拆为 RQ3（预算/参数稳健）+ RQ4（适用域） |
| R2-5 | Methods 缺 14 站采样协议；sample_batch1.csv 公开路径缺失（复现性缺口） | 属实：文件仅在本地 results/sampling/（被 .gitignore deny 规则排除） | **采纳**：§2.1 补采样设计；发布去本地路径的 `results/diagnostics/batch1_sample_attributes.csv` |
| R2-6 | S2 分箱在 Results 才定义，太晚 | 属实 | **采纳**：S0/S1/S2 定义移入 Methods §2.1 |
| R2-7 | Gthreshold 用测试期全段气候统计，train/test 独立性问题 | 代码核验属实（snow.py L159-160：g_threshold 为 None 时按当次调用序列估计） | **采纳**：如实披露 + 将"训练派生/冻结 Gthreshold"列为待做敏感性 |
| R2-8 | rep/ngs/seed/停机规则无白话定义 | 属实（configs 有 rep/ngs/kstop=40/peps=0.1/pcento=0.1/seed=1234，正文未写） | **采纳**：§2.4 补全 |
| R2-9 | 15 个基线参数及范围未列 | 属实（model_config.py 有全表） | **采纳**：新增 Table 2 |
| R2-10 | 雪状态初始化/warm-up 未说明 | 代码核验：SWE/G 零初始化（snow.py L169-170），365d warm-up | **采纳**：§2.3 补写 |
| R2-11 | Methods 混入完成结果（rep=2000 数值）；Results 中 refine 叙事权重过大 | 属实 | **采纳**：rep=2000 移至新 §3.4；refine 移入补充材料 |
| R2-12 | §2.5 内"human footprint falsified human-disturbance explanation"是解释而非方法，且因果过强 | 属实 | **采纳**：移出 Methods；Discussion 改"降低但不排除" |
| R2-13 | "KGE≈0 表示严重退化"是 NSE 式零基准误用 | 属实；Knoben et al. 2019 (HESS 23:4323–4331) 证明均值流基准 KGE=1−√2≈−0.41（DOI 已核验） | **采纳**：改写 KGE 解释并新增 Knoben 2019 引用 |
| R2-14 | Results 顺序不利；batch1 标题未显示探索性+降预算 | 属实 | **采纳**：重排 3.1–3.4；新标题 "First-look multi-basin screening under a reduced calibration budget" + 改写引导段 |
| R2-15 | "emphasis therefore stays on stratified summaries" 是结果导向论证 | 属实 | **采纳**：删除；分层依据改为预设雪暴露假设，全样本中位数并列报告 |
| R2-16 | Fig.2 "systematically misplaces" 超出完成证据 | 属实 | **采纳**：改为定性过程线描述 |
| R2-17 | "Pending Results" 不应留在 Results | 同意框架要求 | **采纳**：移入 Methods §2.6 "Planned full-sample analyses" |
| R2-18 | Discussion 循环论证（改善→归因缺雪）；缺 batch1 与 rep=2000 两段 | 属实 | **采纳**：改写首段为 "consistent with, but not diagnostic of"；新增两段证据讨论 |
| R2-19 | "Interior values support numerical stability" 过度推断 | 属实 | **采纳**：改为"未触及边界；稳定性需多 seed/收敛证据（待做）" |
| R2-20 | Abstract "matched budgets" 可读成公平性问题已解决；refine 句应随移补充材料 | 属实 | **采纳**："matched nominal calibration budgets"；Abstract 删 refine 句；interior 句加限定 |
| R2-21 | Fig.5 冗余，建议终稿只留最具诊断图 | 部分同意 | **延后**：batch1/80 站完成后再定图取舍（当前 7 图均有明确角色） |
| R2-22 | Gthreshold 训练派生冻结版应作为主协议 | 合理但需新实验 | **延后**：列入 §2.6 待做敏感性；不虚构已完成 |

### 数据核验记录（全部通过）

- batch1 分层中位数复算：snow≥0.1 med ΔNSE +0.5461（n=9）；<0.1 −0.0068（n=5）；S2 +0.5835（n=5）；全样本 0.0088 —— 与 `batch1_paired_metrics.csv` 一致。
- batch1 与冻结样本关系：14 站 = 2 pilot + 12 冻结 CAMELS（脚本核验）。
- 冻结样本：80 站、seed=20260816、snow 分档 S0=27/S1=35/S2=18 —— 与 `large_n_round_delivery.md` 一致。
- rep=2000@010：mz −0.3106 / snow 0.7318 —— 与 `rep_budget_sensitivity.csv` 一致。

### 备份与提交

- Commit：（本轮提交后回填 hash）
