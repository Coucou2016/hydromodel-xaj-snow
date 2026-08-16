# Verified project status and evidence baseline

**Audit date (local):** 2026-08-17  
**Rule:** every number below was re-read from CSV/MD under the public-repo-relative paths shown. No fabricated metrics.

## Software / model

| Item | Value |
|------|-------|
| Software | hydromodel v0.3.2 |
| Baseline | XAJ-MZ (15 params, no snow store) |
| Extension | XAJ-Snow = single-band CemaNeige-style layer (+Kf, +CTG) → same XAJ-MZ core |
| Forcing | Caravan CAMELS subsets (not original CAMELS meteorology) |
| Train | 1985-10-01 – 1995-09-30 |
| Test | 2005-10-01 – 2014-09-30 |
| Warmup | 365 d |
| Main optimizer | SCE-UA maximizing KGE (spotpy) |

## A. Two-basin go/no-go pilot (SCE-UA + KGE, `rep`=800) — COMPLETE

Source table: `results/diagnostics/xaj_snow_go_nogo.md`  
Metric CSVs: `results/xaj_snow_go_nogo/*/…/evaluation_test/basins_metrics.csv`

| Basin | Role | frac_snow | Model | Test NSE | Test KGE | Test RMSE |
|-------|------|----------:|-------|---------:|---------:|----------:|
| 01013500 | snow-affected target | ≈0.37 | XAJ-MZ | −0.2321 | 0.2096 | 2.2446 |
| 01013500 | snow-affected target | ≈0.37 | XAJ-Snow | 0.7318 | 0.7764 | 1.0473 |
| 14306500 | low-snow negative control | ≈0 | XAJ-MZ | 0.7106 | 0.7815 | 3.0565 |
| 14306500 | low-snow negative control | ≈0 | XAJ-Snow | 0.7043 | 0.7795 | 3.0895 |

**Deltas (010):** ΔNSE ≈ +0.964; ΔKGE ≈ +0.567  
**Deltas (143):** ΔNSE ≈ −0.006; ΔKGE ≈ −0.002  
**Snow params (010, denormalized):** Kf ≈ 3.5006; CTG ≈ 0.1156 (interior of search ranges)  
**Engineering decision:** GO for stratified sampling (not a population inference).

## B. SciPy NSE refine on 01013500 — COMPLETE

Sources:

- Snow refine: `results/xaj_snow_go_nogo/camels_01013500_xaj_snow_refine_scipy/xaj_snow_scipy/evaluation_test/basins_metrics.csv`
- MZ refine: `results/xaj_snow_go_nogo/camels_01013500_xaj_mz_refine_scipy/xaj_mz_scipy/evaluation_test/basins_metrics.csv`

| Model | Test NSE | Test KGE | Test RMSE |
|-------|---------:|---------:|----------:|
| XAJ-Snow scipy refine | **0.8779** | **0.9374** | 0.7066 |
| XAJ-MZ scipy refine | **0.1393** | 0.0856 | 1.8760 |

Note: refine is a **supplementary** local search after SCE-UA; do not replace the matched SCE-UA go/no-go comparison with refine-only claims.

## C. Rep-budget sensitivity — PARTIAL

Source: `results/diagnostics/rep_budget_sensitivity.csv` (+ `.md`)

| Basin | Model | rep | Test NSE | Status |
|-------|-------|----:|---------:|--------|
| 01013500 | XAJ-MZ | 200 | −0.2321 | complete (matches medium plateau) |
| 01013500 | XAJ-Snow | 200 | 0.5712 | complete |
| 01013500 | XAJ-MZ | 800 | −0.2321 | complete (go/no-go) |
| 01013500 | XAJ-Snow | 800 | 0.7318 | complete (go/no-go) |
| 01013500 | XAJ-MZ | **2000** | **−0.3106** | **complete** |
| 01013500 | XAJ-Snow | **2000** | **0.7318** | **complete** |
| 01013500 | either | 5000 | — | **not run** |
| 14306500 | either | 2000 / 5000 | — | **not run** (200 & 800 available via go/no-go / batch) |

**Interpretation so far (not final fairness proof):** on snowy 010, MZ stays poor even at rep=2000; Snow improves 200→800 and does not further improve at 2000 under this seed/protocol. Full factorial + multi-seed still pending.

## D. Frozen stratified sample — FREEZE DONE; FULL CALIBRATION NOT DONE

| Item | Value | Source |
|------|------:|--------|
| Frozen basins | **80** | `results/sampling/sample_frozen.csv` (may be local-only; documented in diagnostics) |
| Seed | 20260816 | delivery note |
| Snow bins (frozen) | S0=27, S1=35, S2=18 | `results/diagnostics/large_n_round_delivery.md` |
| Paper long-term target | ~500 | planning only |

## E. Batch1 paired calibration (rep=200, n=14) — COMPLETE (first look)

Sources:

- `results/diagnostics/batch1_paired_metrics.csv`
- `results/diagnostics/applicability_first_look.md` / `.csv`

Protocol: SCE-UA + KGE, **rep=200** (lighter than pilot medium), same train/test windows, 14 CAMELS basins × 2 models.

| Group | n | median ΔNSE (snow − mz) | median NSE_snow | median NSE_mz |
|-------|--:|------------------------:|----------------:|--------------:|
| All | 14 | 0.0088 | 0.4118 | 0.0119 |
| frac_snow ≥ 0.1 | 9 | **0.5461** | 0.5468 | −0.0734 |
| frac_snow < 0.1 | 5 | **−0.0068** | 0.3534 | 0.4739 |
| S2 (frac_snow > 0.3) | 5 | **0.5835** | 0.5712 | 0.0119 |

**Manuscript strength allowed:** “extended pilot / first-look stratified CAMELS subset” — **not** a multi-region or global applicability map.  
**Caveats:** n=14; rep=200 under-budgets relative to pilot medium; a few basins fail for both models (e.g. extreme negative NSE on some IDs) and pull down the all-sample median — report **stratified** medians.

Figures (SciencePlots): `results/figures/fig_batch_delta_nse_vs_frac_snow.png`, `fig_batch_delta_nse_by_snow_bin.png`.

## F. Explicitly incomplete (must not be written as done)

- `rep`=5000 on any basin
- `rep`=2000 on 14306500
- Full 80-basin (or 300–500) paired medium calibration
- SWE auxiliary consistency vs ERA5-Land
- Fixed-snow-parameter ablation / multi-seed fairness factorial
- Cross-region applicability regression with grouped CV
- Zenodo DOI

## G. Public GitHub tip (at briefing authoring)

Previous public tip was `5da6a04`. Local work may include newer commits after this briefing is pushed; always check the repository tip before citing a SHA in Availability.

## H. Prior ChatGPT threads (context only; re-verify)

- CemaNeige alignment / go-no-go: see `docs/local/chatgpt_consultation_xaj_snow.md`
- HESS round-1 review: `docs/local/manuscript_review_round1.md`
