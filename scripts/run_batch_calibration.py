"""Batch paired calibration for frozen stratified sample (XAJ-MZ vs XAJ-Snow).

Features:
  - minicache build per region group
  - paired xaj_mz / xaj_snow SCE-UA calibrations
  - evaluate test period
  - resume (skip if basins_metrics.csv exists)
  - failures recorded; do not abort the batch
  - configurable parallelism (process pool)
  - logs under results/batch/logs/

Summary: results/batch/metrics_summary.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import yaml

FOLDER_TO_CODE = {
    "camels": "US",
    "camelsaus": "AUS",
    "camelsbr": "BR",
    "camelscl": "CL",
    "camelsgb": "GB",
    "hysets": "NA",
    "lamah": "CE",
}


def _repo() -> Path:
    return Path(__file__).resolve().parents[1]


def _vars(model: str) -> list[str]:
    base = ["precipitation", "potential_evapotranspiration", "streamflow"]
    return base + ["temperature_mean"] if model == "xaj_snow" else base


def _job_dirs(out_root: Path, basin: str, model: str) -> tuple[Path, Path]:
    run_dir = out_root / f"{basin}_{model}"
    cali = run_dir / f"{model}_SCE_UA"
    return run_dir, cali


def _metrics_path(cali: Path) -> Path:
    return cali / "evaluation_test" / "basins_metrics.csv"


def _write_cfg(
    repo: Path,
    basin: str,
    region_folder: str,
    model: str,
    rep: int,
    out_root: Path,
) -> Path:
    cfg_dir = repo / "configs" / "_generated_batch"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    run_dir, _ = _job_dirs(out_root, basin, model)
    cfg = {
        "data": {
            "dataset": "caravan",
            "path": None,
            "basin_ids": [basin],
            "warmup_length": 365,
            "variables": _vars(model),
            "datasource_kwargs": {"region": FOLDER_TO_CODE.get(region_folder, "US")},
            "train_period": ["1985-10-01", "1995-09-30"],
            "test_period": ["2005-10-01", "2014-09-30"],
            "output_dir": str(run_dir.as_posix()),
        },
        "model": {
            "name": model,
            "params": {"source_type": "sources", "source_book": "HF", "kernel_size": 15},
            "output_variable": "qsim",
        },
        "training": {
            "algorithm": "SCE_UA",
            "SCE_UA": {
                "rep": int(rep),
                "ngs": 15,
                "kstop": 40,
                "peps": 0.1,
                "pcento": 0.1,
                "random_seed": 1234,
            },
            "loss": "KGE",
            "save_config": True,
        },
        "evaluation": {
            "metrics": ["NSE", "KGE", "RMSE", "PBIAS"],
            "save_results": True,
            "plot_results": False,
        },
    }
    path = cfg_dir / f"{basin}_{model}_rep{rep}.yaml"
    path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return path


def _ensure_env(repo: Path) -> None:
    os.environ["HOME"] = str(repo)
    os.environ["USERPROFILE"] = str(repo)
    os.environ["HYDRO_SETTING_FILE"] = str(repo / "hydro_setting.yml")
    os.environ["PYTHONUTF8"] = "1"


def _build_minicache(
    repo: Path,
    py: str,
    region_folder: str,
    basin_ids: list[str],
    cache_dir: Path,
    data_root: Path,
    log_path: Path,
) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        py,
        str(repo / "scripts" / "build_caravan_minicache.py"),
        "--data-root",
        str(data_root),
        "--region-folder",
        region_folder,
        "--basin-ids",
        *basin_ids,
        "--t-range",
        "1985-10-01",
        "2014-09-30",
        "--cache-dir",
        str(cache_dir),
        "--pet-preference",
        "FAO_PENMAN_MONTEITH",
    ]
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"\n$ {' '.join(cmd)}\n")
        log.flush()
        subprocess.run(cmd, cwd=str(repo), check=True, stdout=log, stderr=subprocess.STDOUT)


def _run_pair_worker(payload: dict) -> dict:
    """Worker for one basin × one model (process-safe)."""
    repo = Path(payload["repo"])
    _ensure_env(repo)
    py = payload["python"]
    basin = payload["basin_id"]
    region = payload["region_folder"]
    model = payload["model"]
    rep = int(payload["rep"])
    out_root = Path(payload["out_root"])
    log_dir = Path(payload["log_dir"])
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{basin}_{model}.log"

    run_dir, cali = _job_dirs(out_root, basin, model)
    t0 = time.time()
    row = {
        "basin_id": basin,
        "region": region,
        "model": model,
        "rep": rep,
        "status": "ok",
        "NSE": "",
        "KGE": "",
        "RMSE": "",
        "params_json": "",
        "elapsed_sec": "",
        "source_csv": "",
        "error": "",
    }
    try:
        if _metrics_path(cali).exists():
            row["status"] = "skipped_existing"
        else:
            cfg = _write_cfg(repo, basin, region, model, rep, out_root)
            with log_path.open("a", encoding="utf-8") as log:
                log.write(f"\n=== calibrate {basin} {model} rep={rep} ===\n")
                log.flush()
                subprocess.run(
                    [py, str(repo / "scripts" / "run_xaj_calibration.py"), "--config", str(cfg)],
                    cwd=str(repo),
                    check=True,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                )
                subprocess.run(
                    [
                        py,
                        str(repo / "scripts" / "run_xaj_evaluate.py"),
                        "--calibration-dir",
                        str(cali),
                        "--eval-period",
                        "test",
                    ],
                    cwd=str(repo),
                    check=True,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                )
        mpath = _metrics_path(cali)
        if mpath.exists():
            import pandas as pd

            df = pd.read_csv(mpath)
            r0 = df.iloc[0]
            row["NSE"] = float(r0["NSE"])
            row["KGE"] = float(r0["KGE"])
            row["RMSE"] = float(r0["RMSE"])
            row["source_csv"] = str(mpath.as_posix())
        else:
            row["status"] = "missing_metrics"
        params = cali / "calibration_results.json"
        if params.exists():
            row["params_json"] = str(params.as_posix())
    except Exception as exc:  # noqa: BLE001
        row["status"] = "failed"
        row["error"] = f"{exc}\n{traceback.format_exc()}"
        with log_path.open("a", encoding="utf-8") as log:
            log.write(row["error"] + "\n")
    row["elapsed_sec"] = round(time.time() - t0, 1)
    return row


def _append_summary(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "basin_id",
        "region",
        "model",
        "rep",
        "NSE",
        "KGE",
        "RMSE",
        "params_json",
        "elapsed_sec",
        "status",
        "source_csv",
        "error",
    ]
    # merge with existing
    existing = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                existing[(r["basin_id"], r["model"], str(r["rep"]))] = r
    for r in rows:
        existing[(r["basin_id"], r["model"], str(r["rep"]))] = {k: r.get(k, "") for k in fieldnames}
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for key in sorted(existing.keys()):
            w.writerow(existing[key])


def main() -> int:
    repo = _repo()
    ap = argparse.ArgumentParser(description="Batch paired XAJ-MZ / XAJ-Snow calibration.")
    ap.add_argument("--sample-csv", default=str(repo / "results" / "sampling" / "sample_frozen.csv"))
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--rep", type=int, default=800)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0, help="Max basins (0=all).")
    ap.add_argument("--snow-only", action="store_true", help="Only frac_snow bin S1/S2.")
    ap.add_argument("--nosnow-only", action="store_true", help="Only frac_snow bin S0.")
    ap.add_argument("--models", default="xaj_mz,xaj_snow")
    ap.add_argument("--out-root", default=str(repo / "results" / "batch" / "runs"))
    ap.add_argument("--summary", default=str(repo / "results" / "batch" / "metrics_summary.csv"))
    ap.add_argument(
        "--cache-dir",
        default=str(repo / "_portable_data" / ".cache_global_then_refine_v2"),
        help="Must match hydro_setting.yml cache so hydrodataset finds the minicache.",
    )
    ap.add_argument("--data-root", default=str(repo / "_portable_data" / "datasets-origin"))
    ap.add_argument("--skip-minicache", action="store_true")
    ap.add_argument("--basins", default="", help="Optional comma list to override sample.")
    args = ap.parse_args()

    _ensure_env(repo)
    import pandas as pd

    sample = pd.read_csv(args.sample_csv)
    if args.basins.strip():
        want = {b.strip() for b in args.basins.split(",") if b.strip()}
        sample = sample[sample["basin_id"].isin(want)]
    if args.snow_only and "snow_bin" in sample.columns:
        sample = sample[sample["snow_bin"].isin(["S1_0.1_0.3", "S2_gt0.3"])]
    if args.nosnow_only and "snow_bin" in sample.columns:
        sample = sample[sample["snow_bin"].eq("S0_lt0.1")]
    if args.limit and args.limit > 0:
        sample = sample.head(args.limit)

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    out_root = Path(args.out_root)
    log_dir = repo / "results" / "batch" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    out_root.mkdir(parents=True, exist_ok=True)

    # Minicache by region (one batch file per region subset)
    if not args.skip_minicache:
        for region, g in sample.groupby("region_folder"):
            basins = sorted(g["basin_id"].astype(str).unique().tolist())
            # Chunk to keep cache files manageable
            chunk = 20
            for i in range(0, len(basins), chunk):
                part = basins[i : i + chunk]
                print(f"minicache {region} n={len(part)} chunk={i // chunk}", flush=True)
                _build_minicache(
                    repo,
                    args.python,
                    str(region),
                    part,
                    Path(args.cache_dir),
                    Path(args.data_root),
                    log_dir / "minicache.log",
                )

    payloads = []
    for _, row in sample.iterrows():
        for model in models:
            payloads.append(
                {
                    "repo": str(repo),
                    "python": args.python,
                    "basin_id": str(row["basin_id"]),
                    "region_folder": str(row["region_folder"]),
                    "model": model,
                    "rep": args.rep,
                    "out_root": str(out_root),
                    "log_dir": str(log_dir),
                }
            )

    results: list[dict] = []
    if args.workers <= 1:
        for p in payloads:
            print(f"run {p['basin_id']} {p['model']}", flush=True)
            r = _run_pair_worker(p)
            results.append(r)
            _append_summary(Path(args.summary), [r])
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as ex:
            futs = {ex.submit(_run_pair_worker, p): p for p in payloads}
            for fut in as_completed(futs):
                r = fut.result()
                results.append(r)
                _append_summary(Path(args.summary), [r])
                print(f"done {r['basin_id']} {r['model']} status={r['status']}", flush=True)

    fail = [r for r in results if r["status"] == "failed"]
    (repo / "results" / "batch" / "failures.json").write_text(
        json.dumps(fail, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "n_jobs": len(results),
                "n_failed": len(fail),
                "summary": args.summary,
            },
            indent=2,
        )
    )
    return 0 if not fail else 2


if __name__ == "__main__":
    raise SystemExit(main())
