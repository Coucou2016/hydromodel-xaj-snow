# XAJ-Snow 文献清单与核验状态

更新日期：2026-08-16  
检索来源：ChatGPT 联网对话（URL 见 `chatgpt_consultation_xaj_snow.md`）+ Cursor 独立 WebSearch/出版社页面核验  
工作流：`nature-academic-search` 意图 = citation-verification + multi-source-search（本机 Crossref/OpenAlex SSL 失败，以出版社/DOI 解析与检索摘要交叉核验）

图例：

- **已核验**：DOI 可解析到一手题名/期刊/年份，与引用用途一致  
- **存疑/慎用**：DOI 存在但用途被过度引申，或元数据细节有偏差  
- **否决入文**：不应作为本主张的支撑（本清单暂无整篇伪造 DOI）

---

## A. 必须正面处理的 XAJ / 融雪先例

| ID | 文献（一句话作用） | 年 | DOI | 核验 |
|----|-------------------|----|-----|------|
| L1 | Tan et al.：西北流域 XAJ **耦合融雪** + SCE-UA —— 否定“首次 XAJ+snow / 首次 SCE-UA 校准” | 2023 | [10.3390/w15193401](https://doi.org/10.3390/w15193401) | **已核验**（MDPI Water） |
| L2 | Ju et al.：青藏高原流域 **DD-XAJ**（分布式度日冰雪）—— 否定“首次 degree-day XAJ” | 2024* | [10.1016/j.ejrh.2023.101638](https://doi.org/10.1016/j.ejrh.2023.101638) | **已核验**（JoH: Regional Studies；*在线 2023-12，卷期常标 2024） |
| L3 | Wu et al.（Nan Wu 等）：GXAJ→GXAJ-S→GXAJ-S-SF，SNOW17 —— **最接近寒区复杂度竞品** | 2025 | [10.5194/hess-29-3703-2025](https://doi.org/10.5194/hess-29-3703-2025) | **已核验**（HESS；作者姓 Wu 名 Nan，勿写 Wu H.） |
| L3b | Dong et al.：雅砻江上游 XAJ+融雪+冻融 —— 中文区域先例 | 2024 | [10.14042/j.cnki.32.1309.2024.04.002](https://doi.org/10.14042/j.cnki.32.1309.2024.04.002) | **已核验**（水科学进展） |
| L3c | Chen et al.（陈泽鑫；通讯赵铜铁钢）：dMXAJ=可微参数学习+CemaNeige；**531 CAMELS**；中位 KGE 0.58→0.68（加雪）→0.72（区域可微） —— **削弱“大样本 XAJ+CemaNeige”新颖性** | 2025 | [10.14042/j.cnki.32.1309.2025.02.003](https://doi.org/10.14042/j.cnki.32.1309.2025.02.003) | **已核验**（水科学进展；ChatGPT 口头 “Chen & Zhao” 可作通讯缩写，正式引用用 Chen et al.） |
| L3d | Ke et al.：XAJ+融雪模块的区间预报（黄河源） —— 又一区域 XAJ-snow 先例，非大样本诊断 | 2024 | [10.1007/s11269-024-03909-6](https://doi.org/10.1007/s11269-024-03909-6) | **已核验**（Water Resources Management；ChatGPT 本轮审稿提到） |
| L4 | Ouyang et al.：dXAJ/dXAJnn vs eXAJ；小样本 CAMELS+三峡 —— 上游可微 XAJ；勿误写“未讨论 optimizer” | 2024 | [10.1016/j.jhydrol.2024.132471](https://doi.org/10.1016/j.jhydrol.2024.132471) | **已核验**（ChatGPT 标 2025 为出版滞后口误，DOI 年 2024） |
| L5 | Ouyang et al.：含水库大陆尺度 LSTM；DOR 等混杂 —— 支撑 dor/hft 入筛选/回归 | 2021 | [10.1016/j.jhydrol.2021.126455](https://doi.org/10.1016/j.jhydrol.2021.126455) | **已核验** |

---

## B. CemaNeige / 极简融雪

| ID | 文献（一句话作用） | 年 | DOI | 核验 |
|----|-------------------|----|-----|------|
| L6 | Valéry et al. Part 1：380 流域比较雪核算结构 | 2014 | [10.1016/j.jhydrol.2014.04.059](https://doi.org/10.1016/j.jhydrol.2014.04.059) | **已核验** |
| L7 | Valéry et al. Part 2：CemaNeige 敏感性 —— Methods *style* 措辞依据 | 2014 | [10.1016/j.jhydrol.2014.04.058](https://doi.org/10.1016/j.jhydrol.2014.04.058) | **已核验** |
| L8 | Ruelland：SIAR；参数自由度与雪状态/流量联合 —— 支持“少自由参数”叙事 | 2023 | [10.1016/j.jhydrol.2023.129867](https://doi.org/10.1016/j.jhydrol.2023.129867) | **已核验** |
| L9 | Ruelland：雪数据提升半分布式模型一致性/稳健 —— 多目标/雪状态约束先例 | 2024 | [10.1016/j.jhydrol.2024.130820](https://doi.org/10.1016/j.jhydrol.2024.130820) | **已核验**（题名经他引交叉确认） |

---

## C. 大样本诊断 / 适用性 / 数据

| ID | 文献（一句话作用） | 年 | DOI | 核验 |
|----|-------------------|----|-----|------|
| L10 | Knoben et al.：36 模型×559 流域结构不确定性 —— 大样本比较范式；雪区难点背景 | 2020 | [10.1029/2019WR025975](https://doi.org/10.1029/2019WR025975) | **已核验**（WRR） |
| L11 | Premier et al.：仅校准融雪系数、其余固定 —— **机制隔离**模板 | 2026 | [10.5194/hess-30-1189-2026](https://doi.org/10.5194/hess-30-1189-2026) | **已核验** |
| L12 | Kratzert et al.：Caravan 数据集描述 | 2023 | [10.1038/s41597-023-01975-w](https://doi.org/10.1038/s41597-023-01975-w) | **已核验**（Scientific Data） |
| L13 | Clerc-Schwarzenbach et al.：Caravan vs 原始 CAMELS forcing 改变概念模型表现 —— **Methods 必写局限** | 2024 | [10.5194/hess-28-4219-2024](https://doi.org/10.5194/hess-28-4219-2024) | **已核验** |
| L14 | Tong et al.：卫星雪盖/土壤湿度多目标率定与区域化 | 2022 | [10.5194/hess-26-1779-2022](https://doi.org/10.5194/hess-26-1779-2022) | **已核验** |
| L15 | Clerc-Schwarzenbach & do Nascimento：大样本 forcing 诊断（E-OBS）—— forcing 敏感性写作参考 | 2026 | [10.5194/hess-30-119-2026](https://doi.org/10.5194/hess-30-119-2026) | **已核验** |
| L16 | Santos et al.：大样本 robustness 诊断 + 驱动因素 —— **全文主骨架模板** | 2025 | [10.5194/hess-29-683-2025](https://doi.org/10.5194/hess-29-683-2025) | **已核验** |
| L17 | Husic et al.：可解释 ML 诊断大尺度模型过程不足 —— **适用边界回归模板** | 2025 | [10.5194/hess-29-4457-2025](https://doi.org/10.5194/hess-29-4457-2025) | **已核验** |
| L18 | Yeste et al.：流量+蒸发多目标大样本 VIC —— Methods–Results 镜像模板 | 2024 | [10.5194/hess-28-5331-2024](https://doi.org/10.5194/hess-28-5331-2024) | **已核验** |

---

## D. 写作架构模板（精读 5 篇）

见 `paper_framework_xaj_snow.md` §2：L16 Santos、L3 Wu、L11 Premier、L17 Husic、L18 Yeste。

---

## E. 存疑 / 需写作时再收紧的点

| 项 | 说明 |
|----|------|
| “全球多区域大样本 XAJ 评估空白” | **相对空白可写**，但勿绝对“first-ever / 无人做过”；检索未穷尽中文与灰色文献 |
| dXAJ 年份 | 用 DOI `2024.132471`；正文可写 Journal of Hydrology (2024/2025) |
| Caravan“约 1.6 万流域” | 版本依赖；论文须**冻结 Zenodo/版本号**并报告筛选后 N |
| ERA5-Land SWE | 可作辅助状态一致性；**不宜**称独立地面观测验证 |
| Valéry Part1 ScienceDirect PII | DOI 已核验即可；PII 字符串不必强依赖 ChatGPT 粘贴 |

---

## F. 本轮未纳入但可选补充（未强制核验全文）

- Kratzert et al. 2018/2019 LSTM-HESS（大样本 DL 叙事，非 XAJ 核心）  
- Riboust et al. 2019 CemaNeige 滞回扩展（若讨论 SCA–SWE）  
- airGR/Coron 软件论文（实现对照，非科学主证）

---

## G. 对本地缺口的修正后表述

| 原表述风险 | 修正后 |
|------------|--------|
| 首次 XAJ 融雪扩展 | 区域先例已存在；本文贡献是**多区域诊断+最小修正+负对照+边界** |
| dXAJ 未研究优化机制 | dXAJ **已讨论** optimizer；缺口是**非因子设计**，未干净分离 optimizer vs sharing |
| SWE 独立验证 | 改为 **snow-state consistency / auxiliary evaluation** |
| 全球 XAJ 空白 | 改为 **缺乏统一多区域协议下的 XAJ 结构失效—修正—边界评估** |
