# Manuscript excerpt for review (sanitized)

This excerpt mirrors the journal-facing draft in `results/publications/xaj_snow_manuscript.md` after the 2026-08-17 evidence refresh. Absolute machine paths removed. Numbers match `01_project_status_and_evidence.md`.

---

## Title (working)

Diagnosing snow-related structural limitations of the Xinanjiang model: a parsimonious snow extension and an engineering pilot with a first-look multi-basin extension

Status badges: pilot complete · batch1 first-look complete · large-sample pending

---

## Abstract (draft)

Conceptual rainfall–runoff models remain central to large-sample hydrology, yet structural adequacy can collapse in regimes that the model never represents. The Xin’anjiang model (XAJ) in its Muskingum–Zhao routing form (XAJ-MZ) treats precipitation as liquid input and therefore cannot store snowfall or release meltwater. Regional studies have already coupled snow and related cold-region processes to XAJ (Tan et al., 2023; Ju et al., 2024; Dong et al., 2024; Wu et al., 2025), and a large-sample CAMELS study has already coupled CemaNeige to XAJ under differentiable parameter learning across 531 catchments (Chen et al., 2025). What remains under-documented in the HESS-facing literature is a diagnosis-first protocol that (i) maps where unmodified XAJ-MZ fails along snow/hydroclimate gradients, (ii) tests a deliberately minimal non-ML snow correction under matched budgets, (iii) requires neutrality on snow-free controls, and (iv) publishes an applicability boundary with fairness checks—rather than proposing another high-performing XAJ–snow family.

Here we implement XAJ-Snow: a single-band, CemaNeige-style degree-day layer with two free parameters—degree-day factor Kf (mm °C−1 d−1) and cold-content coefficient CTG [-]—placed upstream of an otherwise unchanged XAJ-MZ core. We report an engineering go/no-go pilot under identical SCE-UA calibration against KGE with matched medium budget (`rep`=800): on snow-affected basin 01013500 (frac_snow ≈ 0.37), out-of-sample NSE rises from −0.232 to 0.732 and KGE from 0.210 to 0.776; on low-snow control 14306500, NSE changes only from 0.711 to 0.704 (Δ ≈ −0.006). A SciPy NSE refine on 01013500 further raises XAJ-Snow test NSE to 0.878 versus 0.139 for refined XAJ-MZ (supplementary). A first-look paired batch of 14 CAMELS basins at lighter budget (`rep`=200) shows median ΔNSE ≈ +0.55 for snow-affected basins (frac_snow ≥ 0.1, n=9) and ≈ −0.007 for low-snow basins (n=5).

**Still pending (do not treat as completed Results):** full stratified calibration of the frozen 80-basin sample (and the longer-term ~500 target); SWE auxiliary consistency; complete optimizer×parameter-freedom factorial including `rep`=5000 and multi-seed; cross-region applicability regression. Until those finish, do not extrapolate to a global claim.

---

## 1 Introduction (compressed)

Large-sample evaluations show that average skill hides regime-dependent structural failure (Knoben et al., 2020; Santos et al., 2025). Snow-affected catchments are a recurring stress test.

XAJ snow/cold-region variants already exist (Tan 2023; Ju 2024; Dong 2024; Wu 2025; Chen 2025 dMXAJ). **This manuscript does not claim the first XAJ snow extension, nor the first XAJ–CemaNeige coupling, nor the first large-sample XAJ–snow evaluation.** The intended niche is diagnosis-first: map inadequacy; test a minimal non-ML fix under classical optimization; require snow-free neutrality; publish applicability/fairness diagnostics.

RQ1–RQ3 remain the guiding questions; current text reports the engineering pilot plus a cautious first-look batch.

---

## 2 Methods (keypoints)

- Data: Caravan (Kratzert et al., 2023); forcing ≠ original CAMELS (Clerc-Schwarzenbach et al., 2024).
- Pilot basins fixed a priori: 01013500 (snow target), 14306500 (negative control); similar human footprint falsifies a pure disturbance story.
- XAJ-Snow: single-band CemaNeige-style; Ts=0 °C, Tr=1 °C; free Kf∈[0,10], CTG∈[0,1]; isothermal melt gate + Gratio·(0.9G+0.1) melt scaling; Gthreshold estimated per forcing call (disclose; not a calibrated hidden parameter).
- Calibration: SCE-UA + KGE; pilot matched `rep`=800, `ngs`=15. Batch1 uses `rep`=200. Partial higher-budget check: 010 at `rep`=2000 complete; `rep`=5000 not run.
- Metrics: independent test NSE/KGE/RMSE.

---

## 3 Results (keypoints)

### 3.1 Pilot table (`rep`=800)

| Basin | Model | NSE | KGE | RMSE |
|-------|-------|----:|----:|-----:|
| 01013500 | XAJ-MZ | −0.2321 | 0.2096 | 2.2446 |
| 01013500 | XAJ-Snow | 0.7318 | 0.7764 | 1.0473 |
| 14306500 | XAJ-MZ | 0.7106 | 0.7815 | 3.0565 |
| 14306500 | XAJ-Snow | 0.7043 | 0.7795 | 3.0895 |

### 3.2 Supplementary refine (010 only)

XAJ-Snow NSE 0.8779 / KGE 0.9374; XAJ-MZ NSE 0.1393 / KGE 0.0856.

### 3.3 First-look batch1 (`rep`=200, n=14)

- snow≥0.1: median ΔNSE ≈ +0.546 (n=9)
- snow<0.1: median ΔNSE ≈ −0.007 (n=5)
- S2 (>0.3): median ΔNSE ≈ +0.584 (n=5)
- All-sample median is near zero because dual failures exist; prefer stratified reporting.

### 3.4 Still pending

Population inference on frozen N=80+; SWE consistency; full fairness factorial; applicability model.

---

## 4–5 Discussion / Conclusions (stance)

Pilot + first-look batch support selective structural benefit of a minimal snow store under classical SCE-UA, without claiming global applicability or physical melt identification without SWE constraints. Distinguish from Chen et al. (2025) skill-learning narrative and from Wu/Dong process-complexity ladders.

---

## Reviewer focus questions

See `04_requested_review_tasks.md`.
