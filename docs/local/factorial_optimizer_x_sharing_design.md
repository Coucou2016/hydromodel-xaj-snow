# Factorial design skeleton: optimizer × parameter sharing (2×2)

Status: **design + draft only** — do not break the existing per-basin calibration path.

## Cells

|  | Per-basin independent (current) | Attribute→parameter sharing (TODO) |
|--|----------------------------------|-------------------------------------|
| SCE-UA global | Cell A: production baseline (`run_xaj_calibration.py` + SCE_UA) | Cell C: joint params = f(attrs; θ) across basins |
| scipy local | Cell B: refine from SCE-UA (`algorithm: scipy`) | Cell D: local refine of shared map θ |

## Current code anchors

- Per-basin loop (Cells A/B): `hydromodel/trainers/unified_calibrate.py` → `calibrate()` comment:
  - “1. Calibrate all basins together (TODO - future implementation)”
  - “2. Calibrate each basin separately (current implementation)”
- Do **not** replace approach 2; add approach 1 behind an explicit flag, e.g.
  `training.multi_basin_mode: independent|shared_attr_map`.

## Minimal viable shared-map draft (not implemented this round)

1. Choose attribute vector `a_i` (e.g. `frac_snow`, `aridity`, `log(area)`, `pre_mm_syr`).
2. Map `p_i = sigmoid(W a_i + b)` into XAJ parameter bounds (shared `W,b`).
3. Objective: mean (or area-weighted) basin losses under SCE-UA / scipy on `vec(W,b)`.
4. Start with 5–10 basins, freeze attrs, compare vs independent Cell A on held-out basins.

## Compatibility rules

- Default remains `independent`.
- Shared mode writes to a separate `output_dir` suffix `_shared_attr`.
- Evaluation still emits per-basin `basins_metrics.csv` for ΔNSE analyses.

## Next executable steps (when scheduled)

1. Add config flag + no-op branch that errors with a clear message if shared mode selected before implementation.
2. Unit-test attribute packing/unpacking without running SCE-UA.
3. Smoke shared map on 3 basins with `rep=50` before any paper claim.
