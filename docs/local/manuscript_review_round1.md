# XAJ-Snow 文稿审稿第 1 轮（HESS 视角）

- 日期：2026-08-16
- ChatGPT 对话：https://chatgpt.com/c/6a815caf-d6ac-83ea-8e50-9d8250f07bba（标题：网页检索与评审准备）
- 原始摘录：`docs/local/_chatgpt_raw_hess_review_round1.txt`
- 本地执行：nature-reviewer 立场 + 独立 WebSearch/出版社核验；仅落地修订文稿/框架，未动批量率定

## 顾问总体判定（摘要）

Overall：以当前双站 pilot 形态 **reconsider / reject-and-resubmit**；工程 go/no-go 信号强，但不足以支撑 Introduction 所承诺的“多区域失效诊断 + 适用边界”。
新颖性关键校正：Chen et al. 2025（水科学进展）已在 531 CAMELS 上做 XAJ+CemaNeige（及可微参数学习）。

## 逐条处置

| ID | 关切 | 本地核验 | 处置 |
|----|------|----------|------|
| M1 | 双站不足以支撑多区域诊断/适用边界主结论 | 同意；框架与 go/no-go 文档一致 | **采纳**：Abstract/Results 强化 “engineering pilot”；Pending 块保留；禁止外推措辞加强 |
| M2 | Chen et al. 2025 削弱 “大样本 XAJ+CemaNeige” 新颖性 | DOI `10.14042/j.cnki.32.1309.2025.02.003` **已核验**（陈泽鑫等；通讯赵铜铁钢）。ChatGPT 口头 “Chen & Zhao” 可作通讯缩写，正式用 Chen et al. | **采纳并修正作者写法**；Intro/Discussion/报告/文献清单全面正面处理；收窄贡献为诊断+最小非 ML 修正+负对照+公平性 |
| M3 | rep=800 不能当成公平基线 | 配置确认两模型同为 rep=800/ngs=15；公平性实验未跑 | **采纳**：Methods 明确 matched budget ≠ fair/converged；标“待补充” |
| M4 | 17 vs 15 / 单负对照不足以排除自由度解释 | 同意 | **采纳措辞**：Discussion 写“降低但未消除”；单对照≠分层零雪队列 |
| M5 | Kf/CTG 物理合理性过度解读风险 | 源码为有效参数；Kf≈3.5 在常见 2–6 量级且未贴边，但无 SWE 约束 | **采纳**：写 effective parameters；禁止写“已物理解识” |
| M6 | Methods 方程省略等温门控与 Gratio | 对照 `snow.py`：确有 isothermal 与 (0.9G+0.1) | **采纳**：Methods/报告补全方程 |
| M7 | 与 Tan/Ju/Wu 区分度不够 | 同意；另补 Dong 2024 | **采纳**：Intro 重写区分段 |
| m1 | Wu 作者误写 | Lund/HESS：Nan Wu 等，非 Wu H. | **已修正** refs |
| m2 | 图 1–5 仅支持 pilot 论点 | 同意 | **保持**；不增图伪装大样本（大样本图待补充） |
| m3 | Abstract 像在卖已完成大样本结果 | 框架本就禁止 | **已改**：明确 engineering pilot + Pending |
| — | ChatGPT 引 `10.1007/s11269-024-03909-6` | 见下方 DOI 核验表 | 按核验结果决定是否入文 |

## DOI 核验（本轮顾问文中出现）

| DOI | 状态 |
|-----|------|
| 10.14042/j.cnki.32.1309.2025.02.003 | **通过**（Chen et al. 2025 dMXAJ） |
| 10.5194/hess-29-3703-2025 | **通过**（Wu et al. 2025） |
| 10.1016/j.ejrh.2023.101638 | **通过**（Ju / DD-XAJ） |
| 10.3390/w15193401 | **通过**（Tan 2023） |
| 10.5194/hess-29-683-2025 | **通过**（Santos 2025） |
| 10.5194/hess-29-4457-2025 | **通过**（Husic 2025，页 4457–4472） |
| 10.5194/hess-30-1189-2026 | **通过**（Premier 2026） |
| 10.1016/j.jhydrol.2024.132471 | **通过**（dXAJ） |
| 10.1016/j.jhydrol.2014.04.058 / .059 | **通过**（Valéry） |
| 10.14042/j.cnki.32.1309.2024.04.002 | **通过**（Dong 2024；本轮本地补入） |
| 10.1007/s11269-024-03909-6 | **通过**（Ke et al. 2024 WRM；XAJ+融雪区间预报；已入文献清单 L3d） |

## 否决项

| 顾问建议 | 否决理由 |
|----------|----------|
| 把当前双站结果写成 HESS 主 Results 人口诊断 | 与已确立叙事及证据层级冲突；大样本未完成 |
| 因 Chen 2025 而放弃诊断叙事 | 相反：应**收窄并强化**诊断/负对照/公平性 niche |
| 改动批量率定/分层实验 | 本轮任务禁止；由另一路负责 |

## 已落地修订（源）

- `scripts/generate_publication_outputs.py`（论文+报告内容源）
- `docs/local/paper_framework_xaj_snow.md`
- `docs/local/literature_review_xaj_snow.md`
- `docs/local/chatgpt_consultation_xaj_snow.md`
- 重新生成 `results/publications/*`

---

## 第 1 轮续：公开 GitHub 快照 FOLLOW-UP（2026-08-16）

- 事实：https://github.com/Coucou2016/hydromodel-xaj-snow @ `master` / `5da6a04`（含源码/docs/figures/publications；不含 hydrodata/_portable_data/大 nc）
- ChatGPT：同线程 FOLLOW-UP + CONTINUE；网页搜索开启；最终 Major/Minor **正文被限流截断**；思考面板与本地核验见 `docs/local/_chatgpt_raw_hess_followup_github.txt`

### 增量处置

| 关切 | 核验 | 处置 |
|------|------|------|
| 公开仓是否撤销既有 Major | 否：仍是双站 pilot；Chen 2025 / fair budget / 17vs15 未因开源消失 | **保持** M1–M5 |
| 可复现性是否改善 | 是：pinned 源码/配置/测试/生成脚本在仓 | **采纳**：Availability 指向 GitHub + `5da6a04` |
| 剩余 Availability gaps | 无大 nc / `_portable_data` / hydrodata；无完整 SpotPy dump；Zenodo pending | **写入** Code/data availability 与报告 §12 |
| `g_threshold` 按序列估计 | `snow.py` 缺省从当次 snowfall 估计；train/test 分段 → 各自重算 | **披露** Methods（英）+ 报告方法/局限（中）；**不改**实现 |

### 否决

| 建议倾向 | 否决理由 |
|----------|----------|
| 因开源仓而把 pilot 升格为 HESS-ready | 证据层级未变 |
| 本轮立刻改冻结 Gthreshold 逻辑 | 会破坏与既有 medium 协议可比；属后续 paper-grade 增强 |
