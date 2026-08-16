# XAJ-Snow 论文框架（落地稿）

更新日期：2026-08-16  
写作技能轴：`nature-writing` → task=manuscript, paper_type=methods, journal=generic（目标 HESS）, language=zh-to-en 规划  
图件：仅约定 `results/figures/` 命名；**不**改绘图脚本（另一 workstream）。

## 0. 一句话论证（nature-writing stance）

> 在多区域大样本概念模型评估中，我们表明标准 XAJ-MZ 存在雪相关的**结构性失效区间**；用**故意极简**的双参数、单带、CemaNeige-inspired 修正可在雪影响流域选择性提升样本外技巧，并在无雪负对照中保持中性；由此导出 XAJ-Snow 的**适用边界**，并把增益与优化预算/额外自由度区分开——边界止于：非 airGR 严格复现、非“首个 XAJ 融雪”、ERA5-Land SWE 仅为辅助状态一致性、大样本结果未完成前不得把双站 pilot 外推为全局结论。

## 1. 目标期刊

| 优先级 | 期刊 | 理由 |
|--------|------|------|
| **首选** | **HESS** | 近年大量“大样本失效诊断 / 过程不足诊断 / 寒区 XAJ 复杂度 / 多状态约束”叙事；与本主线最贴 |
| 备选 | Journal of Hydrology | 方法与案例深度空间更大；但“诊断+适用边界”叙事在 HESS 更易对齐审稿预期 |

**暂不**在题目中写 *global*，直至筛选后有效样本与区域覆盖统计清楚（Caravan 版本需冻结）。

## 2. 模仿的写作模板（已独立核验 DOI）

精读顺序建议：Santos → Wu → Premier → Husic → Yeste。

| 代号 | 文献 | DOI | 结构套路（可模仿点） |
|------|------|-----|----------------------|
| A | Santos et al., HESS 2025 | [10.5194/hess-29-683-2025](https://doi.org/10.5194/hess-29-683-2025) | 大样本 robustness：哪里失败 → 何种属性相关 → 结构该改什么。**全文主骨架** |
| B | Wu et al., HESS 2025 | [10.5194/hess-29-3703-2025](https://doi.org/10.5194/hess-29-3703-2025) | GXAJ→GXAJ-S→GXAJ-S-SF 逐级复杂度；寒区 XAJ **直接竞品**。我们反向做“最小修正+负对照” |
| C | Premier et al., HESS 2026 | [10.5194/hess-30-1189-2026](https://doi.org/10.5194/hess-30-1189-2026) | **只改融雪系数、其余参数固定**的机制隔离哲学 → 优化/参数自由度控制实验 |
| D | Husic et al., HESS 2025 | [10.5194/hess-29-4457-2025](https://doi.org/10.5194/hess-29-4457-2025) | 流域属性 → 性能预测 → SHAP/阈值 → 过程假说。目标改为预测 **ΔKGE** |
| E | Yeste et al., HESS 2024 | [10.5194/hess-28-5331-2024](https://doi.org/10.5194/hess-28-5331-2024) | Methods 实验块与 Results **一一镜像**；多状态/多 forcing 交叉验证 |

必须正面处理、否定“首次融雪 XAJ / 首次 XAJ–CemaNeige / 首次大样本 XAJ 融雪”的先例（见文献清单）：Tan 2023、Ju 2024、Dong 2024、Wu 2025、**Chen et al. 2025（水科学进展；CAMELS 531 + CemaNeige + 可微参数学习 dMXAJ）**。

**2026-08-16 审稿轮更新：** Chen et al. (2025) DOI `10.14042/j.cnki.32.1309.2025.02.003` 已独立核验。HESS 可辩护贡献收窄为：诊断-first + 最小非 ML 修正 + 负对照 + 公平性/适用边界；**不得**再主打“大样本 XAJ+CemaNeige 技巧提升”。

## 3. 建议题目

**主推：**  
*Diagnosing snow-related structural limitations of the Xinanjiang model across a large multi-regional catchment sample*

**备选（大样本结果清晰后）：**  
*When does the Xinanjiang model need snow? A large-sample diagnosis of a parsimonious snow extension*

## 4. Outline（HESS methods 风格）

### Abstract（约 230–280 英词）

Problem → Gap（已有区域 XAJ-snow，缺多区域“失效→最小修正→边界”）→ Method（Caravan + 成对协议 + 负对照 + 属性诊断）→ Results（**仅写未来大样本真结果**；勿塞入双站 pilot）→ Meaning（regime-dependent structural adequacy）。

### 1 Introduction（约 1200–1500 英词）

1. 大样本概念模型适用性（非“雪很重要”开场）  
2. XAJ 现状：已有 snow / DD-XAJ / GXAJ-S / dXAJ —— 缺口不是“从未扩展”  
3. 为何极简 snow（Valéry “as simple as possible…”）  
4. 为何仅 Q 不够（雪状态一致性）  
5. RQ1–RQ3；**RQ4（optimizer×sharing factorial）仅当真做完再写**

### 2 Data and Methods（约 3000–3600 英词）

| 小节 | 要点 | 字数量级 |
|------|------|----------|
| 2.1 Caravan & screening | 冻结版本；时间窗；缺失；属性；**强制说明 Caravan forcing ≠ 各地原始 CAMELS forcing**（Clerc-Schwarzenbach et al. 2024） | ~500–700 |
| 2.2 XAJ-MZ baseline | 15 参；无雪过程 | ~300 |
| 2.3 XAJ-Snow | *CemaNeige-style / single-band*；Ts=0, Tr=1；Kf, CTG；非 airGR 复现 | ~500–600 |
| 2.4 Calibration protocol | train/test/warmup；SCE-UA+KGE；评价 NSE/KGE/RMSE | ~400 |
| 2.5 Snow strata & negative controls | 预定义 0/低/中/高雪；负对照协议 | ~300 |
| 2.6 Fairness controls | 优化预算倍数 × seeds；固定雪参 vs 自由；边界撞壁报告 | ~400 |
| 2.7 Snow-state consistency | ERA5-Land SWE：**辅助一致性**，勿称 independent ground validation | ~300 |
| 2.8 Applicability regression | 预测 ΔKGE；GAM + RF/SHAP；**按区域/源数据集分组 CV** | ~400 |
| 2.9 Optional factorial | 仅可选；未完成则整节删除 | — |

### 3 Results（约 2400–3000 英词）

按 RQ 排列：失效分布 → 成对增益 → 负对照 → 雪状态 → 优化/自由度稳健 → 适用边界（→ 可选 factorial）。

### 4 Discussion（约 1500–2000 英词）

与 Tan/Ju/Wu/dXAJ 区分；适用边界；forcing 局限；单带/Ts-Tr；17 vs 15；不下因果终证。

### 5 Conclusions（约 400–600 英词）

贡献收束 + 边界 + 下一步（分层批量、可选 refine、可选真独立雪产品）。

## 5. 逐图论点映射（约定路径）

| 图 | 建议文件名 | 对应论点 |
|----|------------|----------|
| Fig.1 | `results/figures/fig01_study_domain_population.*` | 预定义大样本总体，非双站 cherry-pick |
| Fig.2 | `results/figures/fig02_xaj_mz_vs_xaj_snow_structure.*` | 故意最小结构扰动 |
| Fig.3 | `results/figures/fig03_paired_oos_performance.*` | 成对样本外 KGE/NSE |
| Fig.4 | `results/figures/fig04_delta_vs_frac_snow.*` | 增益随雪影响梯度变化 |
| Fig.5 | `results/figures/fig05_hydrograph_examples.*` | 预定义规则选例；雪区时序修正 vs 负对照无虚假增益 |
| Fig.6 | `results/figures/fig06_swe_consistency.*` | 雪状态一致性（非独立地面验证） |
| Fig.7 | `results/figures/fig07_optimizer_complexity_robustness.*` | 非纯优化预算/自由度解释 |
| Fig.8 | `results/figures/fig08_applicability_boundary.*` | 何时值得加雪过程 |
| Fig.9 | `results/figures/fig09_factorial_optimizer_sharing.*` | **可选**；未做 factorial 则不出 |

Pilot 双站（01013500 / 14306500）仅可作 Methods 示意或 SI，**不得**充当 Results 主证。

## 6. 贡献声明（采纳版，2–3 条）

1. **大样本结构失效诊断**：在多区域样本上量化 XAJ-MZ 样本外 adequacy 如何随雪与其他水文气候梯度变化——从“平均技巧”转向“regime-dependent structural adequacy”。  
2. **可证伪的最小融雪结构修正**：双参数、单带、CemaNeige-inspired 修正；增益应集中于雪影响流域，并在无雪负对照中消退。  
3. **适用边界 + 公平性控制**：跨区域验证的 Δ 适用边界；检验增益是否稳健于优化预算与额外参数自由度。若完成 factorial，再升级为 optimizer vs parameter-sharing 的归因分离（与 dXAJ 的非因子设计区分）。

**禁止**：首次把融雪引入 XAJ；首次 degree-day XAJ；把 ERA5-Land SWE 写成独立观测验证；未做 factorial 却声称已分离优化机制与参数共享。

## 7. 与 go/no-go 证据的关系

本地 medium（rep=800）仅支持 **工程 GO** 与方法可运行性：

- 雪区 ΔNSE≈+0.96；无雪 ΔNSE≈−0.006；Kf≈3.50、CTG≈0.116 未贴边  

论文级结论仍依赖分层/批量大样本与公平性实验。
