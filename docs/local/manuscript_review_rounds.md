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
| R2-1 | RQ 清单应加 RQ4（适用域连续估计）并给出 RQ2 前瞻性中性判据 | 同意 | **采纳**：RQ 列表扩为 RQ1–RQ4；2.5 节定义 ±0.05 前瞻判据 |
| R2-2 | Methods 2.1 缺采样/分箱/batch1 来源说明 | 属实 | **采纳**：重写为采样设计段（含 batch1=2 pilot+12 站） |
| R2-3 | 参数搜索范围表缺失 | 属实 | **采纳**：新增 Table（SCE-UA 参数含义 + 17/15 参数区间） |
| R2-4 | Gthreshold 训练/测试独立性问题未披露 | 属实（代码逐期重算） | **采纳**：2.3 节显式披露 + 列为待做敏感性 |
| R2-5 | batch1 结果表述过强（像结论） | 属实 | **采纳**：统一为 "first-look evidence"，Results 重组为 3.1–3.4 |
| R2-6 | Discussion 存在循环论证风险 | 部分属实 | **采纳**：加"一致但非诊断"限定；替代解释清单显式化 |
| R2-7 | Abstract 含 SciPy refine 细节干扰主线 | 属实 | **采纳**：移至补充说明 |
| R2-8 | KGE 解读需引 Knoben 2019（无零基准） | 属实 | **采纳**：2.4 节补公式与引文 |

### 备份与提交

- 修改后备份：`results/publications/versions/v1.2_20260818_0320/`
- Commit：`3887bd7`（已 push 至 origin/master；commit hash 于后续提交回填：`8f96318`）

---

## Round 3（2026-08-18 03:30–03:50）：文字与学术表达润色

- ChatGPT 对话：https://chatgpt.com/c/6a835077-8718-83ea-9c3f-6a66b9c39b1c（续用同一会话）
- 原始回复：`docs/local/_chatgpt_raw_round4_wording_polish.txt`（37,690 字符，DOM 提取）
- 修改前状态：v1.2（即 Round 2 提交版 3887bd7）
- 修改后备份：`results/publications/versions/v1.3_20260818_0347/`

### 任务设定（发给 ChatGPT 的约束）

- 仅润色英文表达（句式、hedging、主动/被动、去口语化），**禁止**改动数字、符号、引文、事实边界与 pending 状态；每节给 OVERWRITE + CHANGES；末尾给全局 TERMINOLOGY LEDGER。

### 问题清单与处置

| ID | ChatGPT 意见 | 本地核验 | 处置 |
|----|--------------|----------|------|
| R3-1 | "engineering go/no-go pilot" 非期刊用语 | 属实 | **采纳**：全篇 → "pilot evaluation" |
| R3-2 | Abstract 先前文献单句信息密度过高 | 属实 | **采纳**：拆为两句 |
| R3-3 | Abstract 指标为冒号/分号堆叠 | 属实 | **采纳**：改完整陈述句 |
| R3-4 | Intro 文献综述长句堆砌；"unlocked the go decision" 口语 | 属实 | **采纳**：拆短句；删除口语 |
| R3-5 | Methods 片段式描述（属性/时期/变量）非完整散文 | 属实 | **采纳**：2.1 改完整句并分段 |
| R3-6 | 2.3 "prepends" 编程化动词 | 属实 | **采纳**：改 "places … upstream of" |
| R3-7 | 2.5 中性判据与理由混在一句 | 属实 | **采纳**：拆句，阈值不变 |
| R3-8 | 3.2 图解读含口语（"hug the diagonal"）与祈使句 | 属实 | **采纳**：改论文式描述 |
| R3-9 | "forbid population inference" 非常规搭配 | 属实 | **采纳**：→ "preclude population inference" |
| R3-10 | Discussion "parameters alone buy universal skill" 口语 | 属实 | **采纳**：改正式统计表述 |
| R3-11 | Conclusions "engineering GO" | 属实 | **采纳**：→ "decision to proceed" |
| R3-12 | Supplementary "headroom evidence" 工程俚语 | 属实 | **采纳**：→ "objective-sensitivity evidence" |
| R3-13 | 25 组术语台账统一（pilot evaluation / screening batch / matched nominal calibration budgets 等） | 与台账一致 | **采纳**：全篇执行 |

### 否决/保留项

| ChatGPT 建议 | 处置 | 证据 |
|--------------|------|------|
| Fig.1 数据源标注含 "paired go/no-go basins_metrics.csv" | **保留原样**（非否决，属例外） | 这是仓库目录/文件名标识；ChatGPT 自己的 OVERWRITE 亦保留该行 |
| 报告中文正文中的 go/no-go/first-look | **保留** | 台账仅约束论文；报告允许工程语境（论文/报告边界规则） |

### 独立核验

- 润色稿与 OVERWRITE 逐节比对：数字（−0.2321/0.7318/0.7106/0.7043/0.5461/−0.0068/0.5835/0.0088/−0.3106 等）零改动；引文集合零增减；pending 清单与中性阈值（±0.05）原样保留。
- 重新生成 6 文件：HTML 校验 OK；manuscript.md 复查无 first-look/engineering GO/headroom 残留（唯一 "go/no-go" 为 Fig.1 文件标识）。

### 备份与提交

- 修改后备份：`results/publications/versions/v1.3_20260818_0347/`
- Commit：`6d56f19`（已 push 至 origin/master）

---

## Round 4（2026-08-18 03:50–04:25）：图片格式与 Figure 规范审查

- ChatGPT 对话：https://chatgpt.com/c/6a835077-8718-83ea-9c3f-6a66b9c39b1c（续用同一会话）
- 原始回复：`docs/local/_chatgpt_raw_round5_figure_audit.txt`（18,115 字符，DOM 提取）
- 交互方式：ChatGPT 无法读图 → 本地提供全部图注+图内容描述，ChatGPT 联网检索 HESS/Copernicus 现行规范逐条审计
- 修改前状态：v1.3（Round 3 提交版 6d56f19）
- 修改后备份：`results/publications/versions/v1.4_20260818_0420/`

### 问题清单与处置

| ID | ChatGPT 意见 | 本地核验 | 处置 |
|----|--------------|----------|------|
| R4-1 | 300 dpi / ≥8cm / PNG 格式 | 实测全部 PASS | **通过**，无需改 |
| R4-2 | Fig.5 缺 panel label (a)/(b) | 属实（代码无 text 标注） | **采纳**：重绘加粗体 (a)/(b) |
| R4-3 | Fig.5 缺 1:1 参考线图例 | 属实（代码 plot 无 label） | **采纳**：加 "1:1" 图例项 |
| R4-4 | Fig.2/3 春季阴影缺图内图例 | **误判**：`_shade_spring()` 已有 "Mar–May" label | **否决**（代码证据） |
| R4-5 | 图内标题与图注重复 | 属实 | **采纳**：Fig.1–4/6/7 删内部标题；Fig.5 简化为 panel 头 |
| R4-6 | 图注含仓库文件名/go-no-go 术语 | 属实 | **采纳**：7 条图注全部重写为自包含学术表述 |
| R4-7 | Fig.6/7 "dNSE (snow - mz)" 非规范记法 | 属实（代码如此） | **采纳**：改 "ΔNSE (XAJ-Snow − XAJ-MZ)"；分箱标签加 S0/S1/S2 |
| R4-8 | 单位 mm/d → mm d⁻¹ | 代码核验已是 mm d⁻¹（$^{-1}$ 上标） | **已合规**，无需改 |
| R4-9 | 字体 Times New Roman 非 Copernicus 偏好（建议 sans-serif） | 规范原文为 "consider"，非强制 | **延后**：单一字体族已满足；投稿前可选 |
| R4-10 | 生产文件命名 f01–f07 | 属实（投稿要求） | **延后**：投稿打包时执行；仓库保留描述名 |
| R4-11 | 图注缺流域角色/单位/时期 | 属实 | **采纳**：全部补齐 |

### 数据防回归事件（重要）

- 重跑 `analyze_applicability_first_look.py` 时默认 `--sample` 指向 `sample_frozen.csv`（80 站冻结样本，不含 2 pilot 站），导致 `applicability_first_look.csv` 中 01013500/14306500 属性列丢失。
- **立即修复**：改用 `--sample results/sampling/sample_batch1.csv` 重跑，CSV 与已发布版逐字节一致；重跑生成的 `applicability_first_look.md` 含本地绝对路径，用 `git checkout` 恢复手工润色版。
- 结论：任何诊断文件重跑后必须 diff 核验；本轮所有指标数字零改动。

### 备份与提交

- 修改后备份：`results/publications/versions/v1.4_20260818_0420/`
- Commit：`212b697`（已 push 至 origin/master）

---

## Round 5（2026-08-18 04:25–05:30）：综合终审（模拟 HESS 审稿人）

- ChatGPT 对话：https://chatgpt.com/c/6a835077-8718-83ea-9c3f-6a66b9c39b1c（续用同一会话）
- 原始回复：`docs/local/_chatgpt_raw_round6_final_review.txt`（25,660 字符，DOM 提取）
- 审查对象：master @ `212b697` 全文（ChatGPT 从 GitHub raw 读取）
- 修改前备份：`results/publications/versions/v1.5_20260818_0505/`（与 v1.4 逐字节一致，即 ChatGPT 所审对象的本地副本）
- 修改后备份：`results/publications/versions/v2.0_20260818_0525/`（**最终版**）

### ChatGPT 总体裁决

- **推荐**：Major Revision —— 不是要求新主张，而是要求把论文自己承诺的分析（RQ1–RQ4）做完后再投；框架、文字、数字纪律、图注已达近投稿质量，剩余障碍是**证据完备性与可复现性**，不是呈现。
- 数字一致性核查：**PASS**（Abstract/Table/Results 全部对照公开 CSV 复核；rep=200 vs rep=800 区分正确）；证据边界：MOSTLY PASS（3 处修正）；术语台账：全 PASS（除 applicability map → applicability domain）；图注自足性：**PASS**（无需再大改）。

### 问题清单与处置（Major）

| ID | ChatGPT 意见 | 本地核验 | 处置 |
|----|--------------|----------|------|
| R5-M1 | 核心 HESS 贡献依赖的实验（RQ1–RQ4）未完成 | 属实（Sect. 2.6 本就如此声明） | **延后为提交前门槛**：文字不虚构完成；继续按既定协议补齐 medium 全量/rep=5000/多 seed/factorial/SWE/适用域后再投 |
| R5-M2 | 测试期 Gthreshold 削弱"独立测试期"纯度 | 属实（代码逐期重算；已披露） | **保留披露 + 延后**：训练期冻结 Gthreshold 敏感性列入待做；不虚构冻结结果 |
| R5-M3 | 校准公平性未闭环（17 vs 15 参数；rep 名义相等≠实现工作量相等；SPOTPY 收敛控制使 rep 不能完全刻画工作量） | 属实 | **延后为待做 factorial**；正文保留 "matched nominal calibration budgets" 措辞；补报告 realized evaluation counts 的义务 |
| R5-M4 | 冻结分层设计未完全可复现（七区域未列名、干旱/调节分箱阈值缺失、全样本 seed、层内分配、Caravan 版本、frac_snow 来源字段缺失） | 属实（信息在本地 `results/sampling/` 但未公开） | **采纳**：Methods 2.1 补七区域名单+三组分箱阈值+seed 20260816；发布脱敏 `sample_frozen_attributes.csv`（80 行，无本地路径）与 `sample_frozen_manifest.json`（设计清单）至 `results/diagnostics/`；新增 `scripts/sanitize_frozen_sample_publication.py` 固化脱敏流程 |
| R5-M5 | 14 站筛查非独立于 pilot（含 2 个 pilot 站）："reproduces the directional specificity" 过强 | 属实（sample_batch1.csv 确认含 01013500/14306500） | **采纳**：改 "extends the pilot pattern across the partially overlapping screening sample"，并显式标注"佐证性筛查证据而非独立确认" |
| R5-M6 | 雪模块部分图示化：partition 精确式、等温条件、Gthreshold 极小地板未写明 | 属实（snow.py 源码核对） | **采纳**：2.3 节写精确式 f_snow=clip((Ts+Tr−T)/(2Tr),0,1)、等温判据 G≥−1e−8 °C、地板 1e−6 mm |
| R5-M7 | 数据/指标可追溯性未定稿（Table 内源路径、指向 mutable master、生成器快照提交滞后、Zenodo DOI pending） | 属实 | **采纳**：Code/Data 段改"生成时快照提交 + 投稿前以最终提交铸造 Zenodo 不可变存档"；删除 Table 内 `basins_metrics.csv` 文件路径 |

### 问题清单与处置（Minor）

| ID | ChatGPT 意见 | 本地核验 | 处置 |
|----|--------------|----------|------|
| R5-m1 | "motivating the completed multi-basin assessment" 暗示完成 | 属实 | **采纳**：→ "motivating completion of the planned multi-basin assessment" |
| R5-m2 | PET "attributes" 措辞不精确 | 属实（Caravan ≥v1.5 提供 FAO-PM 强迫序列） | **采纳**：2.1 明确为 FAO Penman–Monteith 强迫序列及替换 ERA5-Land 原始序列的原因（联网核验 Caravan v1.5 变更） |
| R5-m3 | 属性句为片段非完整句 | 属实 | **采纳**：并入 2.1 完整散文 |
| R5-m4 | 表编号乱序（参数 Table 2 先于指标 Table 1 被引） | 属实 | **采纳**：参数表 → Table 1，指标表 → Table 2 |
| R5-m5 | Table Bias 未定义；配置用 PBIAS | 属实且可复算（见下） | **采纳**：2.4 节定义 Bias = mean(Q_sim−Q_obs)（mm d⁻¹），并区分 KGE 的 β |
| R5-m6 | Kf "commonly reported ~2–6" 无引文 | 属实（无对应引文） | **采纳**：删除比较区间 |
| R5-m7 | 中性阈值缺理由/冻结记录 | 属实 | **采纳**：补理由句 + 声明 Methods 内冻结 |
| R5-m8 | "Reading Figure X" 研究报风格 | 部分属实 | **部分采纳**：保留结构，压缩为正式散文句式 |
| R5-m9 | Fig.5 "higher correlation / lower error" 斜杠结构 | 属实 | **采纳**：展开为完整句 |
| R5-m10 | Discussion footprint "less likely" 因果排序过强 | 属实 | **采纳**：改描述性表述 |
| R5-m11 | Conclusions "multi-region/global applicability map" 违反台账 | 属实 | **采纳**：→ applicability domain（两处） |
| R5-m12 | 参考文献：Ju 卷号、Tan/Premier 标题意译、Valéry 标题不全、Ouyang 2021/Yeste 2024 未被引用 | 逐条联网核验属实（见下） | **采纳**：全部修正；Ouyang 2021、Yeste 2024 在 Discussion 对应论点补真实引用 |
| R5-m13 | 徽章连排渲染为 "pilot completescreening" | 属实（HTML 无空格） | **采纳**：badge 间加空格（英文+中文报告） |
| R5-m14 | 作者信息/致谢占位 | 属实 | **保留**：投稿前必填项已记录 |

### 关键独立核验记录

1. **Bias 定义复算**（R5-m5）：用 4 个评估 NetCDF 反推，`mean(Q_sim−Q_obs)` 与 CSV Bias 不等 → 进一步发现公开 NetCDF 已换算为 m³/s，除以流域面积换算因子（01013500：7.382247/26.6 ≈ 0.2776；14306500：−3.733473/9.9421 ≈ −0.3755）与 CSV 精确匹配 → 确认 Bias = mean(Q_sim−Q_obs)，单位 mm d⁻¹，非 PBIAS。
2. **参考文献核验**（R5-m12，联网逐条）：
   - Ju et al.：J. Hydrol. Reg. Stud. **51**, 101638（原写 42）；
   - Premier et al. 2026：HESS 30, 1189–1220，正式标题 "Assessing the impact of Earth Observation data-driven calibration of the melting coefficient on the LISFLOOD snow module"（原为意译）；
   - Tan et al. 2023：Water 15(19), 3401 正式标题（原为意译）；
   - Valéry et al. 2014a/b：标题补全 + 页码 1166–1175 / 1176–1187；
   - Ouyang et al. 2021：JoH 599, 126455 标题补全；Tong et al. 2022：HESS 26, 1779–1799 标题补全。
3. **雪模块方程**（R5-M6）：对照 `hydromodel/models/snow.py`（`partition_rain_snow`、`cema_neige`、`_GTHR_MIN=1e-6`、`_G_ISOTHERMAL=1e-8`）逐式核对后写入正文。
4. **数字零改动复核**：修改后 Table 2 全 20 值、batch1 中位（+0.5461/−0.0068）、rep=2000（−0.3106/0.7318）与 CSV 一致；本轮未新增/修改任何数值。

### 否决/延后项（ChatGPT VERDICT 五条最弱点的应对）

| ChatGPT 弱点 | 处置 | 理由 |
|--------------|------|------|
| 1. 实验未完成为何投稿 | **延后（提交门槛）** | 论文本就声明协议未完成；不在文字上虚构完成 |
| 2. 测试期 Gthreshold 独立性 | **保留披露 + 待做敏感性** | 无流量泄漏；冻结模型评价列入待做 |
| 3. 过程修正 vs 优化自由度（17 vs 15） | **待做 factorial** | 多 seed/固定雪参/高预算因子实验列入 Sect. 2.6 |
| 4. 大样本适用性实验可复现性 | **本轮部分闭环** | 已公开冻结样本+设计清单；全量结果仍待计算 |
| 5. 14 站筛查含 pilot 对、rep=200 | **措辞修正** | 明确为佐证性筛查证据，非独立确认 |

### 备份与提交

- 修改前备份：`results/publications/versions/v1.5_20260818_0505/`
- 修改后备份（最终版）：`results/publications/versions/v2.0_20260818_0525/`
- Commit：`060f393`（已 push 至 origin/master）

---

## 五轮汇总（截至 Round 5）

| 轮次 | 主题 | 修改前备份 | 修改后备份 | Commit |
|------|------|-----------|-----------|--------|
| Round 1 | 创新性与定位 | v1.0_20260818_0210 | — | 8ee24ad |
| Round 2 | 内容逻辑与结构 | v1.1_20260818_0239 | v1.2_20260818_0320 | 3887bd7 |
| Round 3 | 文字与学术表达 | — | v1.3_20260818_0347 | 6d56f19 |
| Round 4 | 图片格式与 Figure 规范 | — | v1.4_20260818_0420 | 212b697 |
| Round 5 | 综合终审（模拟 HESS 审稿人） | v1.5_20260818_0505 | v2.0_20260818_0525（最终版） | 060f393 |

- 全部 5 轮均与 ChatGPT 完成（对话：https://chatgpt.com/c/6a835077-8718-83ea-9c3f-6a66b9c39b1c），无限流替代轮。
- 最终产物：`results/publications/xaj_snow_manuscript.{html,md,pdf}` + `report.{html,md,pdf}`（v2.0）。
