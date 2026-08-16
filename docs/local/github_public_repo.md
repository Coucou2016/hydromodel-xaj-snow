# Public GitHub repository notes

## Repository

- **HTTPS URL**: https://github.com/Coucou2016/hydromodel-xaj-snow
- **Visibility**: public
- **Default branch**: master (as initialized locally)
- **Purpose**: open research snapshot of the **XAJ-Snow pilot** (Caravan/CAMELS experiments) plus publication drafts.

## What is included

- Source: `hydromodel/` (including `models/snow.py`, `models/xaj_snow.py`)
- Scripts, configs, tests, docs (including `docs/local/`)
- Lockfile / packaging: `pyproject.toml`, `uv.lock`, `README*`, helper `*.ps1`
- Results (curated only):
  - `results/figures/`
  - `results/publications/` (pilot manuscript / report drafts)
  - `results/diagnostics/*.md`, small `*.csv` / `*.txt` summaries

## What is excluded (do not expect in git)

- Parent **`hydrodata/`** (~100GB) and local **`_portable_data/`**
- Secrets: `.env`, tokens, private keys, filled MinIO/Postgres credentials
- Large binary caches: `*.nc`, `*.zip`, `*.tar.xz`, temp `*.tmp`
- Full calibration dumps: SpotPy/SCE-UA giant CSVs, nested `results/*/…` run folders, `results/diagnostics/rep_budget/`
- Virtualenvs, `__pycache__`, IDE caches

## Data you must prepare locally

Caravan / CAMELS NetCDF and portable caches are **not** shipped. Place data under `_portable_data/` (or configure `hydro_setting*.yml`) and follow `docs/local/data_sources_and_duplicates.md` plus `docs/data_guide.md`. Evaluation NetCDF outputs >50MB are gitignored; reproduce with the provided configs/scripts.

## Paper status (important)

Materials under `results/publications/` and related `docs/local/paper_*.md` are **pilot / working drafts**, not final peer-reviewed conclusions. Do not cite as definitive results without re-checking methods and metrics.

## Reproduce figures / metrics (high level)

1. Install deps (`uv sync` / `pip install -e .` per README).
2. Obtain Caravan/CAMELS inputs locally (never commit them).
3. Run go/no-go or batch scripts (`RUN_GO_NOGO_XAJ_SNOW.ps1`, configs under `configs/xaj_snow_*.yaml`).
4. Regenerate publication assets via `scripts/generate_publication_outputs.py` / `scripts/remake_publication_figures.py` as applicable.
