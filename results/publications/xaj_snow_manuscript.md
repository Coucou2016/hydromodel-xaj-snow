<!-- Markdown sibling of XAJ-Snow manuscript. HTML/PDF are the fully self-contained deliverables (base64 figures + inline CSS). This Markdown keeps relative image paths for in-repo reading. -->

Hydromodel 0.3.2 · XAJ-Snow manuscript draft · generated 2026-08-18 02:34 · for HESS-oriented polishing

  Manuscript draft · Hydrology and Earth System Sciences (target)

# Diagnosing snow-related structural limitations of the Xinanjiang model: a parsimonious snow extension, an engineering pilot, and a first-look multi-basin extension

Working title (avoid “global / first” until the frozen stratified sample is fully calibrated). Status: pilot completebatch1 first-looklarge-sample pending

Authors: *to be completed* · Affiliations: *to be completed* · Correspondence: *to be completed*

Software context: hydromodel v0.3.2; model names XAJ-MZ and XAJ-Snow; Caravan CAMELS subsets.

  **Contents**

    - Abstract

    - 1 Introduction

    - 2 Data and methods

    - 3 Results

    - 4 Discussion

    - 5 Conclusions

    - Code and data availability

    - Author contributions / Competing interests / Acknowledgements

    - References

    - Supplementary note on pilot figures

## Abstract

Conceptual rainfall–runoff models remain central to large-sample hydrology, yet structural adequacy can collapse in regimes that the model never represents.
The Xin’anjiang model (XAJ) in its Muskingum–Zhao routing form (XAJ-MZ) treats precipitation as liquid input and therefore cannot store snowfall or release meltwater.
Regional studies have already coupled snow and related cold-region processes to XAJ (Tan et al., 2023; Ju et al., 2024; Dong et al., 2024; Wu et al., 2025), and a large-sample CAMELS study has already coupled CemaNeige to XAJ under differentiable parameter learning across 531 catchments (Chen et al., 2025).
What remains under-documented in the HESS-facing literature is a diagnosis-first protocol that (i) maps *where* unmodified XAJ-MZ fails along snow/hydroclimate gradients, (ii) tests a deliberately minimal non-ML snow correction under matched budgets, (iii) requires neutrality on snow-free controls, and (iv) designs—rather than yet establishes—an applicability-domain estimate with fairness checks, instead of proposing another high-performing XAJ–snow family.

Here we implement XAJ-Snow: a single-band, CemaNeige-style degree-day layer with two free parameters—degree-day factor *K*f (mm °C−1 d−1) and cold-content coefficient CTG [-]—placed upstream of an otherwise unchanged XAJ-MZ core.
We report an **engineering go/no-go pilot** under identical Shuffled Complex Evolution–University of Arizona (SCE-UA) calibration against the Kling–Gupta efficiency (KGE) with matched medium budget (`rep`=800, `ngs`=15):
out-of-sample Nash–Sutcliffe efficiency (NSE) on snow-affected basin 01013500 (fraction of precipitation falling as snow ≈ 0.37) rises from -0.232 (XAJ-MZ) to 0.732 (XAJ-Snow), while KGE rises from 0.210 to 0.776;
on low-snow negative-control basin 14306500, NSE changes only from 0.711 to 0.704 (Δ ≈ -0.006).
Calibrated snow parameters on 01013500 remain interior (*K*f ≈ 3.50, CTG ≈ 0.116).
A supplementary SciPy NSE refine on 01013500 raises XAJ-Snow test NSE to 0.878 versus 0.139 for refined XAJ-MZ.
A first-look paired batch of 14 CAMELS basins at lighter budget (`rep`=200) yields median ΔNSE ≈ 0.55 for snow-affected basins (frac_snow ≥ 0.1, n=9) and ≈ -0.007 for low-snow basins (n=5).

**Pending (do not treat as completed Results):** full calibration of the frozen stratified sample (currently 80 basins frozen; longer-term target ~500); snow-water-equivalent (SWE) auxiliary consistency; complete optimizer-budget / parameter-freedom factorial (including `rep`=5000 and multi-seed; only a partial `rep`=2000 check on 01013500 is available); cross-region applicability regression. Until those experiments finish, do not extrapolate to a global claim.

## 1 Introduction

Large-sample evaluations have shown that “average skill” hides regime-dependent structural failure
(Knoben et al., 2020; Santos et al., 2025).
Snow-affected catchments are a recurring stress test: models that cannot partition precipitation into rain and snow, or cannot delay melt, mis-time spring peaks even when annual water balance looks plausible.

The Xin’anjiang model is widely used in humid and semi-humid settings.
Variants that add snow or related cold-region processes already exist, including coupled snowmelt–XAJ applications (Tan et al., 2023; Ke et al., 2024), distributed degree-day XAJ with ice/snow melt (Ju et al., 2024), conceptual XAJ with snowmelt plus soil freeze–thaw (Dong et al., 2024), graded complexity GXAJ-S / GXAJ-S-SF with SNOW17 (Wu et al., 2025), and a CAMELS-scale (531 basins) differentiable XAJ–CemaNeige system (dMXAJ) with local and regional parameter learning (Chen et al., 2025).
Differentiable XAJ formulations further explore optimizer and parameter-sharing design (Ouyang et al., 2025).
More broadly, coupling established snow routines to parsimonious conceptual models is now routine methodology in multi-catchment HESS-facing work (Muñoz-Castro et al., 2026), event-type diagnostics already isolate snow-related process limitations at large scale (Wang et al., 2026), and large-sample studies already relate conceptual-model adequacy to the fraction of precipitation falling as snow (Liu et al., 2025; Bohl et al., 2026).
**This manuscript does not claim the first XAJ snow extension, nor the first XAJ–CemaNeige coupling, nor the first large-sample XAJ–snow evaluation.**

These studies demonstrate the value of representing snow processes and, increasingly, of controlling model complexity, but they leave a narrower model-evaluation question unresolved: *when* does adding a minimal snow process to an otherwise unchanged XAJ formulation provide evidence of correcting a process deficiency rather than simply increasing model flexibility?
Addressing this question requires paired evaluation across a snow gradient, comparable calibration effort, and a specificity check in catchments where snow processes should exert little influence.
Rather than proposing a new snow formulation, this study therefore examines when an established, parsimonious snow representation is warranted within the XAJ-MZ framework.
We formulate a diagnosis-first protocol in which the baseline and snow-enabled models retain the same rainfall–runoff and routing backbone, are calibrated under controlled computational budgets, and are evaluated jointly against snow-influenced basins and snow-poor negative controls.
The planned large-sample analysis is designed to relate the paired model response to catchment snow exposure, test whether apparent discharge gains are accompanied by consistent snow behavior, and assess their robustness to calibration-fairness choices
(Valéry et al., 2014a,b; Premier et al., 2026; Husic et al., 2025; Santos et al., 2025).
The current 14-basin experiment is treated only as first-look evidence motivating the completed multi-basin assessment, rather than as evidence for a general applicability threshold.
Relative to Chen et al. (2025), who demonstrate that CemaNeige plus differentiable parameter learning raises median KGE across CAMELS, our complementary question is when a minimal snow layer is *necessary* for structural adequacy under a falsifiable control design—not whether a high-capacity XAJ–snow learner can achieve high skill.
Relative to Wu et al. (2025) and Dong et al. (2024), which deepen process complexity within regional cold basins, the distinctive protocol here is paired minimalism plus negative controls and (pending) fairness / applicability diagnostics.
Relative to Wang et al. (2026) and Liu et al. (2025), which diagnose model limitations across large samples, the distinctive element here is a controlled *intervention* experiment: the same backbone with and without one specific process, evaluated with snow-poor basins as explicit negative controls.

Research questions guiding the full study:

  - RQ1 — Where does XAJ-MZ fail out of sample as a function of snow influence and related attributes?

  - RQ2 — Does a two-parameter, single-band CemaNeige-style layer selectively improve snow-affected basins while remaining neutral on negative controls?

  - RQ3 — Are gains robust to optimizer budget and the extra two parameters, and can an applicability domain be estimated (as a continuous relationship with uncertainty) from catchment attributes?

The present draft reports the engineering pilot that unlocked the go decision for stratified sampling, plus a cautious first-look multi-basin extension at reduced calibration budget.
Full answers to RQ1–RQ3 on the frozen stratified sample remain incomplete.

## 2 Data and methods

### 2.1 Caravan data and the two pilot basins

Forcing and discharge come from the Caravan community dataset (Kratzert et al., 2023).
Caravan harmonizes multi-source CAMELS-family basins but its meteorological forcing is not identical to the original CAMELS products; this difference can change conceptual-model skill and must be stated explicitly (Clerc-Schwarzenbach et al., 2024).
Potential evapotranspiration (PET) uses FAO Penman–Monteith attributes supplied with Caravan.

Pilot basins (roles fixed a priori):

| Basin | Role | frac_snow | Area (km²) | Aridity (FAO-PM) | Human footprint |
| --- | --- | --- | --- | --- | --- |
| camels_01013500 | Snow-affected diagnosis target | ≈0.37 | 2298 | 0.49 | 30.6 |
| camels_14306500 | Low-snow negative control | ≈0.0 | 859 | 0.49 | 34.3 |

Catchment attributes from the Caravan attribute table used in the public diagnostic note for this basin pair. Human activity alone cannot explain the skill contrast (similar footprint; control even slightly higher).

Periods (identical for both models and both basins): training 1985-10-01–1995-09-30; testing 2005-10-01–2014-09-30; warmup length 365 days.
Daily variables: precipitation *P*, PET, discharge *Q*, and for XAJ-Snow also 2 m air temperature *T*.

### 2.2 XAJ-MZ baseline

XAJ-MZ denotes the hydromodel implementation of Xin’anjiang with Muskingum–Zhao routing and fifteen calibrated parameters (no snow store).
All precipitation enters the production module as rainfall-equivalent forcing.

### 2.3 XAJ-Snow: CemaNeige-style single-band layer

XAJ-Snow prepends a lumped (one elevation band) snow-accounting module inspired by CemaNeige (Valéry et al., 2014b) and related airGR documentation, then calls the same XAJ-MZ core on effective liquid input (rain + melt).
Fixed thresholds in this implementation: rain/snow threshold *T*s = 0 °C and linear mix half-width *T*r = 1 °C.
Free snow parameters:

  - Kf — degree-day melt factor (mm °C−1 d−1), search range [0, 10]; larger values melt faster for a given positive temperature.

  - CTG — dimensionless cold-content / thermal-state inertia in [0, 1]; larger CTG increases memory of prior cold conditions and delays melt onset.

Mass symbols used in the module: precipitation *P*, temperature *T*, snow water equivalent SWE, thermal state *G*, melt potential MeltPot, snow-cover factor Gratio, and melt *M*.
A schematic daily update is:

rain, snow ← partition(*P*, *T*; *T*s, *T*r)

SWE ← SWE + snow; *G* ← min(0, CTG·*G* + (1−CTG)·*T*)

MeltPot ← min(SWE, max(0, *K*f·*T*)) only if the pack is isothermal (*G* ≈ 0); else MeltPot = 0

Gratio ← min(1, SWE / Gthreshold); *M* ← min(SWE, (0.9·Gratio + 0.1)·MeltPot)

Unless an external array is supplied, *G*threshold is estimated inside each snow-module call as 0.9 × mean annual snowfall from the snowfall series of *that same call* (CemaNeige-style default; tiny floor for snow-free basins).
Because train and test periods are loaded separately, the pilot therefore recomputes *G*threshold from each period’s forcing rather than freezing a training-derived value into evaluation—an explicit protocol choice to disclose, not a hidden degree of freedom in the calibrated parameter vector.

We describe the layer as *CemaNeige-style / single-band*, not as a strict airGR reproduction (airGR defaults use multiple elevation bands and different temperature bands).
*K*f ≈ 3.5 mm °C−1 d−1 on the snow pilot is interior to the search range and within commonly reported degree-day magnitudes (~2–6), but without SWE constraints it remains an effective parameter rather than a physically identified melt coefficient.

### 2.4 Calibration and metrics

Optimizer: SCE-UA maximizing KGE on the training window.
The pilot medium protocol uses SCE-UA settings `rep`=800 and `ngs`=15 for *both* models and both basins (identical budget by configuration).
The first-look multi-basin batch uses the same objective and periods but a lighter budget (`rep`=200) for screening.
A partial higher-budget check on snow-affected 01013500 at `rep`=2000 is available (XAJ-MZ test NSE -0.3106; XAJ-Snow 0.7318); `rep`=5000 and the control basin at `rep`=2000 remain incomplete.
**Important:** matched budgets support controlled comparison; they do *not* yet constitute a full fairness proof versus multi-seed searches or fixed-snow-parameter ablations.
Those checks must precede any claim that gains are independent of optimization budget or the two extra degrees of freedom (17 vs 15 parameters).
Reported skill uses the independent test window.
NSE and KGE are defined in the conventional forms:

NSE = 1 − Σ(*Q*sim−*Q*obs)2 / Σ(*Q*obs−Q̅obs)2

KGE = 1 − √[ (r−1)2 + (α−1)2 + (β−1)2 ]

where *r* is correlation, α a variability ratio, and β a bias ratio (hydromodel implementation).
NSE = 1 is perfect; NSE = 0 matches climatological mean squared error; negative NSE is worse than the mean.
KGE = 1 is perfect; values near 0 indicate severe degradation of correlation, variability, and/or bias components.

### 2.5 Negative-control design

Basin 14306500 (frac_snow ≈ 0) is the negative control: a useful snow layer should not create large spurious skill gains when snow storage is irrelevant.
Human-footprint attributes are similar across the pair, which previously falsified a pure “human disturbance” explanation for 01013500’s poor XAJ-MZ skill.

**Pending methods blocks:** full calibration of the frozen stratified sample (80 basins frozen; expansion toward ~500 planned); SWE auxiliary consistency against ERA5-Land (consistency only, not independent ground validation); complete optimizer×parameter-freedom factorial; attribute-based ΔKGE applicability models with grouped cross-validation.

## 3 Results

### 3.1 Engineering pilot (completed)

Table 1 lists paired test-period metrics read directly from `basins_metrics.csv`.

**Table 1.** Out-of-sample metrics for the go/no-go pilot (SCE-UA + KGE, rep=800).

| Basin | Model | NSE | KGE | RMSE | Bias | Corr |
| --- | --- | --- | --- | --- | --- | --- |
| 01013500 | XAJ-MZ | -0.2321 | 0.2096 | 2.2446 | 0.2776 | 0.2550 |
| 01013500 | XAJ-Snow | 0.7318 | 0.7764 | 1.0473 | 0.1665 | 0.9031 |
| 14306500 | XAJ-MZ | 0.7106 | 0.7815 | 3.0565 | -0.3755 | 0.8461 |
| 14306500 | XAJ-Snow | 0.7043 | 0.7795 | 3.0895 | -0.2792 | 0.8410 |

Source files: results/xaj_snow_go_nogo/.../evaluation_test/basins_metrics.csv; protocol SCE-UA+KGE, rep=800; train 1985-10-01–1995-09-30; test 2005-10-01–2014-09-30; warmup=365.

On 01013500, XAJ-Snow improves NSE by Δ = +0.964 and KGE by Δ = +0.567.
On 14306500, ΔNSE = -0.006 and ΔKGE = -0.002, i.e. within a few thousandths—consistent with a non-inflating negative control.
Denormalized snow parameters on 01013500: *K*f = 3.5006 mm °C−1 d−1, CTG = 0.115624 (interior of [0,10]×[0,1]).

### 3.2 Supplementary SciPy refine on 01013500

After the matched SCE-UA runs, a SciPy local refine against NSE on 01013500 yields test NSE/KGE of 0.8779/0.9374 for XAJ-Snow versus 0.1393/0.0856 for XAJ-MZ.
We treat refine as **supplementary illustration** of headroom under a different objective/search stage—not as a replacement for the matched SCE-UA go/no-go comparison and not as a fairness proof.

### 3.3 Pilot figures

Figures 1–5 document the two-basin pilot. They support an engineering GO decision and method readiness; they are **not** a substitute for stratified population inference.

![Paired out-of-sample NSE and KGE for the go/no-go pilot basins](../figures/fig_go_nogo_metrics_bar.png)

  **Figure 1.** Paired out-of-sample NSE and KGE for the go/no-go pilot basins.
  Data source: paired go/no-go basins_metrics.csv (SCE-UA+KGE, rep=800).

**Reading Figure 1.** Grouped bars compare NSE (blue family) and KGE (green family) for each basin–model pair.
Tall XAJ-Snow bars on 01013500 versus short/negative XAJ-MZ bars show the selective skill recovery;
near-equal bars on 14306500 show the control remains flat. The figure cannot prove causality beyond the paired protocol, nor generalize beyond two basins.

![Full test-period hydrograph for snow-affected basin 01013500](../figures/fig_01013500_hydrograph_mz_vs_snow.png)

  **Figure 2.** Full test-period hydrograph for snow-affected basin 01013500.
  Data source: evaluation NetCDF for the test window after warmup.

**Reading Figure 2.** Black: observed discharge; blue: XAJ-MZ; orange: XAJ-Snow over the full test window after warmup.
Spring shading marks March–May. XAJ-MZ systematically misplaces snow-season peaks; XAJ-Snow tracks volume and timing more closely.
Do not read summer/autumn residuals as snow-process proof; they may reflect soil/routing parameter trade-offs.

![Spring zoom (2010–2012) for basin 01013500](../figures/fig_01013500_hydrograph_spring_zoom_2010_2012.png)

  **Figure 3.** Spring zoom (2010–2012) for basin 01013500.
  Data source: same evaluation series as Fig. 2; Mar–May spring shading.

**Reading Figure 3.** A 2010–2012 zoom isolates consecutive snowmelt seasons.
Use it to inspect peak timing, multi-peak structure, and whether XAJ-Snow overshoots individual events.
It cannot separate temperature-forcing error from structural melt error.

![Negative-control hydrograph for low-snow basin 14306500](../figures/fig_14306500_hydrograph_mz_vs_snow.png)

  **Figure 4.** Negative-control hydrograph for low-snow basin 14306500.
  Data source: evaluation NetCDF for camels_14306500.

**Reading Figure 4.** On the negative control, XAJ-MZ and XAJ-Snow hydrographs nearly overlap, matching the near-zero Δ metrics.
This panel guards against “any extra parameters help everywhere” interpretations.

![Observed–simulated scatter for basin 01013500](../figures/fig_01013500_obs_sim_scatter.png)

  **Figure 5.** Observed–simulated scatter for basin 01013500.
  Data source: paired daily discharge from the evaluation series.

**Reading Figure 5.** Daily observed vs simulated scatter for 01013500; the 1:1 line is the reference.
XAJ-Snow points hug the diagonal more tightly (higher correlation / lower error), while XAJ-MZ shows larger scatter and bias.
Scatter plots compress timing information—pair with Figures 2–3 for hydrograph timing.

### 3.4 First-look multi-basin extension (batch1, n=14, `rep`=200)

As an **extended pilot / first look**—not a multi-region applicability map—we calibrated XAJ-MZ and XAJ-Snow on 14 CAMELS basins under the same periods and SCE-UA+KGE objective but with a lighter screening budget (`rep`=200).
Stratified medians of test ΔNSE (XAJ-Snow − XAJ-MZ) are 0.5461 for frac_snow ≥ 0.1 (n=9) and -0.0068 for frac_snow < 0.1 (n=5); the high-snow bin S2 (frac_snow > 0.3, n=5) has median ΔNSE 0.5835.
The all-sample median (0.0088) is near zero because a minority of basins fail for *both* models; manuscript emphasis therefore stays on stratified summaries.
Figures 6–7 visualize ΔNSE against snow fraction and by bin.

![First-look batch ΔNSE versus catchment snow fraction (n=14, rep=200)](../figures/fig_batch_delta_nse_vs_frac_snow.png)

  **Figure 6.** First-look batch ΔNSE versus catchment snow fraction (n=14, rep=200).
  Data source: results/diagnostics/batch1_paired_metrics.csv.

**Reading Figure 6.** Each point is one CAMELS basin in the first-look batch (`rep`=200).
Positive ΔNSE indicates XAJ-Snow outperforming XAJ-MZ on the independent test window.
The pattern is consistent with larger gains at higher snow fractions, but n=14 and the lighter budget forbid population inference.

![First-look batch ΔNSE by snow-fraction bin (n=14, rep=200)](../figures/fig_batch_delta_nse_by_snow_bin.png)

  **Figure 7.** First-look batch ΔNSE by snow-fraction bin (n=14, rep=200).
  Data source: results/diagnostics/batch1_paired_metrics.csv.

**Reading Figure 7.** Box/summary view of ΔNSE by snow-fraction bin for the same first-look batch.
Lead with stratified medians (snow-affected vs low-snow) rather than the all-sample median, which is depressed by dual-model failures.

**Pending Results (fill after experiments):**

- Paired calibration of the frozen stratified sample (80 basins frozen; not yet fully run at medium budget).

- Population distribution of XAJ-MZ inadequacy vs snow fraction and covariates across regions.

- SWE auxiliary consistency diagnostics (ERA5-Land), clearly labelled as non-independent.

- Complete optimizer-budget and fixed-vs-free snow-parameter robustness (rep=5000; multi-seed; control basin at higher rep).

- Applicability boundary model (e.g. GAM / RF+SHAP) with region-grouped CV.

- Optional factorial separating optimizer mechanism from parameter sharing.

## 4 Discussion

The pilot is consistent with a structural snow-process gap on 01013500 rather than a pure human-activity story: footprint indices are comparable, yet only the snow-affected basin shows large paired gains.
The near-zero change on 14306500 reduces—but does not eliminate—concern that seventeen versus fifteen parameters alone buy universal skill; a single negative control cannot replace a stratified zero-snow cohort or a fixed-snow-parameter ablation.

Relative to Tan et al. (2023), Ju et al. (2024), Dong et al. (2024), Wu et al. (2025), and especially Chen et al. (2025), the distinctive claim we aim for is not novelty of “XAJ + snow / CemaNeige”, but a controlled process-necessity experiment: the same backbone with and without one established, parsimonious snow intervention, evaluated with explicit negative controls and fairness checks, designed to estimate an applicability domain once the stratified sample is complete.
Chen et al. (2025) already show large-sample skill gains from CemaNeige and from differentiable parameter learning on CAMELS; that result narrows—but does not erase—the niche for a falsifiable diagnosis of *when* a minimal snow store is structurally required under classical SCE-UA and snow-free controls.
Wu et al. (2025) remain the closest HESS-facing complexity ladder (GXAJ→GXAJ-S→GXAJ-S-SF); Dong et al. (2024) further add freeze–thaw in a Chinese regional XAJ setting.
Multi-catchment CemaNeige comparisons (Muñoz-Castro et al., 2026), event-type process diagnostics (Wang et al., 2026), and snow-fraction–stratified large-sample evaluations (Liu et al., 2025; Bohl et al., 2026) confirm that the ingredients of our protocol are individually established; the remaining question is whether their combination as a paired, control-based intervention experiment yields information those studies do not provide.
Our contribution is complementary: parsimony, paired controls, and (pending) applicability / fairness diagnostics—not a competing claim of richer cold-region physics or higher median skill.
Relative to Premier et al. (2026), future work should isolate melt-factor effects more tightly (e.g. freeze non-snow parameters) once the stratified sample exists.

Alternative explanations that remain open: Caravan forcing biases (Clerc-Schwarzenbach et al., 2024); PET product choice; single-band temperature representativeness; equifinality among soil parameters absorbing snow errors; and residual anthropogenic regulation not captured by footprint indices.
SWE was not used as a calibration target here; without snow-state constraints, *K*f and CTG remain effective parameters (Ruelland, 2023, 2024; Tong et al., 2022).
Interior *K*f/CTG values support numerical stability of the search but do not alone prove physical melt identification.

## 5 Conclusions

Under a paired SCE-UA+KGE protocol, a two-parameter CemaNeige-style layer converts a strongly negative out-of-sample NSE on snow-affected basin 01013500 into a clearly positive score, while leaving a low-snow control essentially unchanged.
A first-look 14-basin CAMELS batch at lighter budget shows the same directional pattern in stratified medians, without authorizing a multi-region applicability map.
This supports an engineering GO for completing the frozen stratified sample.
It does *not* yet establish a global applicability map, independent SWE validation, or optimizer-versus-complexity attribution.

Next steps: finish medium-budget calibration on the frozen sample; add SWE consistency and fairness controls; then rewrite Abstract/Results without pilot-only extrapolation.

## Code and data availability

Research code, curated figures, diagnostics notes, consultation briefings, and publication drafts are publicly available at
[https://github.com/Coucou2016/hydromodel-xaj-snow](https://github.com/Coucou2016/hydromodel-xaj-snow)
(branch `master`; generator snapshot commit `2a464aa`).
Core modules include the snow accounting layer and XAJ-Snow wrapper registered in the hydromodel model dictionary; matched pilot configurations, unit tests, and the publication generator are included.
Caravan / CAMELS forcing and discharge follow Kratzert et al. (2023) licensing; large NetCDF caches and portable hydrodata trees are **not** redistributed in the public snapshot.
Full optimizer dump trees are also excluded; curated metric tables and figures remain.
Zenodo archival DOI: pending (to be minted before journal submission).

## Author contributions / Competing interests / Acknowledgements

**Author contributions:** to be completed.

**Competing interests:** to be completed (declare none if applicable).

**Acknowledgements:** to be completed.

## References

Only locally verified DOIs from docs/local/literature_review_xaj_snow.md are listed.

- Bohl, J. P., Wood, R. R., Frank, C., Astagneau, P. C., Peters, J., and Brunner, M. I.: Hybrid models generalize better to warmer climate conditions than process-based and purely data-driven models. HESS, 30, 4667–4698, https://doi.org/10.5194/hess-30-4667-2026, 2026.
- Clerc-Schwarzenbach, F., et al.: Technical note: How many times can you afford to change hydrologic forcing? HESS, 28, 4219–4235, https://doi.org/10.5194/hess-28-4219-2024, 2024.
- Chen, Z., Zhao, T., et al.: Incorporating snow accumulation and melting into the Xin’anjiang model using differentiable parameter learning (dMXAJ / CemaNeige; 531 CAMELS catchments). Advances in Water Science, https://doi.org/10.14042/j.cnki.32.1309.2025.02.003, 2025.
- Dong, N., Wang, H., Yang, M., Zhang, J., and Xu, S.: An improved Xin’anjiang model with snow melting and soil freeze–thaw processes (Upper Yalongjiang). Advances in Water Science, https://doi.org/10.14042/j.cnki.32.1309.2024.04.002, 2024.
- Husic, A., Hammond, J., Price, A. N., and Roundy, J. K.: Interrogating process deficiencies in large-scale hydrologic models with interpretable machine learning. HESS, 29, 4457–4472, https://doi.org/10.5194/hess-29-4457-2025, 2025.
- Ju, J., et al.: Application of distributed Xin’anjiang model of melting ice and snow in Bahe River basin (DD-XAJ). Journal of Hydrology: Regional Studies, 42, 101638, https://doi.org/10.1016/j.ejrh.2023.101638, 2024.
- Ke, H., et al.: Xinanjiang-based interval forecasting model for daily streamflow considering climate change impacts (with snowmelt module). Water Resources Management, https://doi.org/10.1007/s11269-024-03909-6, 2024.
- Knoben, W. J. M., et al.: A quantitative assessment of 36 conceptual rainfall–runoff models across 559 catchments. WRR, https://doi.org/10.1029/2019WR025975, 2020.
- Kratzert, F., et al.: Caravan — A global community dataset for large-sample hydrology. Scientific Data, https://doi.org/10.1038/s41597-023-01975-w, 2023.
- Liu, W., Liu, P., Zhang, L., Zhang, X., Xu, H., Lei, X., et al.: Development of a conceptual hydrological model based on supply-demand relationship and its applications. Water Resources Research, 61(9), e2024WR038873, https://doi.org/10.1029/2024WR038873, 2025.
- Muñoz-Castro, E., Anderson, B. J., Astagneau, P. C., Swain, D. L., Mendoza, P. A., and Brunner, M. I.: How well do hydrological models simulate streamflow extremes and drought-to-flood transitions? HESS, 30, 825–848, https://doi.org/10.5194/hess-30-825-2026, 2026.
- Ouyang, W., et al.: Continental-scale streamflow modeling with LSTM under reservoir influences. Journal of Hydrology, https://doi.org/10.1016/j.jhydrol.2021.126455, 2021.
- Ouyang, W., Ye, L., Chai, Y., Ma, H., Chu, J., Peng, Y., and Zhang, C.: A differentiable, physics-based hydrological model and its evaluation for data-limited basins (dXAJ / dXAJnn). Journal of Hydrology, 649, 132471, https://doi.org/10.1016/j.jhydrol.2024.132471, 2025.
- Premier, V., et al.: Isolating snowmelt-coefficient effects by fixing remaining parameters. HESS, https://doi.org/10.5194/hess-30-1189-2026, 2026.
- Ruelland, D.: SIAR and parsimonious snow accounting under limited degrees of freedom. Journal of Hydrology, https://doi.org/10.1016/j.jhydrol.2023.129867, 2023.
- Ruelland, D.: Snow data improve consistency and robustness of semi-distributed models. Journal of Hydrology, https://doi.org/10.1016/j.jhydrol.2024.130820, 2024.
- Santos, L., Andréassian, V., Sonnenborg, T. O., Lindström, G., de Lavenne, A., Perrin, C., Collet, L., and Thirel, G.: Lack of robustness of hydrological models: a large-sample diagnosis and an attempt to identify hydrological and climatic drivers. HESS, 29, 683–700, https://doi.org/10.5194/hess-29-683-2025, 2025.
- Tan, Q., et al.: Coupling snowmelt with XAJ and SCE-UA calibration in northwestern basins. Water, 15, 3401, https://doi.org/10.3390/w15193401, 2023.
- Tong, R., et al.: Multi-objective calibration with satellite snow cover and soil moisture. HESS, https://doi.org/10.5194/hess-26-1779-2022, 2022.
- Valéry, A., Andréassian, V., and Perrin, C.: As simple as possible but not simpler (Part 1). Journal of Hydrology, https://doi.org/10.1016/j.jhydrol.2014.04.059, 2014.
- Valéry, A., Andréassian, V., and Perrin, C.: As simple as possible but not simpler (Part 2): CemaNeige. Journal of Hydrology, https://doi.org/10.1016/j.jhydrol.2014.04.058, 2014.
- Wang, Z., Tarasova, L., and Merz, R.: Event-type-based multi-dimensional diagnostics of process limitations in hydrological models. Water Resources Research, 62(2), e2025WR040264, https://doi.org/10.1029/2025WR040264, 2026.
- Wu, N., Zhang, K., Naghibi, A., Hashemi, H., Ning, Z., Zhang, Q., Yi, X., Wang, H., Liu, W., Gao, W., and Jarsjö, J.: Predicting snow cover and frozen ground impacts on large basin runoff: developing appropriate model complexity (GXAJ / GXAJ-S / GXAJ-S-SF). HESS, 29, 3703–3725, https://doi.org/10.5194/hess-29-3703-2025, 2025.
- Yeste, P., García-Valdecasas Ojeda, M., Gámiz-Fortis, S. R., Castro-Díez, Y., Bronstert, A., and Esteban-Parra, M. J.: A large-sample modelling approach towards integrating streamflow and evaporation data for the Spanish catchments. HESS, 28, 5331–5352, https://doi.org/10.5194/hess-28-5331-2024, 2024.

## Supplementary note on pilot figures

Figures use SciencePlots styling (≥300 dpi PNG siblings in the public snapshot).
Metric provenance is documented in the repository diagnostics tables accompanying the go/no-go, refine, rep-budget, and batch1 CSV files.
This HTML is self-contained (CSS inline; figures as base64).

Generated 2026-08-18 02:34 from real CSV-backed metrics and figures. No fabricated metrics. Claims beyond completed evidence remain pending.
