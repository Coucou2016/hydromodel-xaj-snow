"""SCE-UA rep budget sensitivity for paired XAJ-MZ vs XAJ-Snow.

Runs (or reuses) calibrations at multiple `rep` values for the two pilot basins,
then writes a convergence table from real evaluation CSVs.

Default reps: 200, 800, 2000, 5000.
Existing medium (rep=800) results under results/xaj_snow_go_nogo/ are reused.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import yaml

BASINS = ("camels_01013500", "camels_14306500")
MODELS = ("xaj_mz", "xaj_snow")

# Reuse already-finished medium runs (rep=800)
REUSE_MAP = {
    ("camels_01013500", "xaj_mz", 800): "results/xaj_snow_go_nogo/camels_01013500_xaj_mz/xaj_mz_SCE_UA",
    ("camels_01013500", "xaj_snow", 800): "results/xaj_snow_go_nogo/camels_01013500_xaj_snow/xaj_snow_SCE_UA",
    ("camels_14306500", "xaj_mz", 800): "results/xaj_snow_go_nogo/camels_14306500_xaj_mz/xaj_mz_SCE_UA",
    ("camels_14306500", "xaj_snow", 800): "results/xaj_snow_go_nogo/camels_14306500_xaj_snow/xaj_snow_SCE_UA",
}


def _repo() -> Path:
    return Path(__file__).resolve().parents[1]


def _vars_for_model(model: str) -> list[str]:
    base = ["precipitation", "potential_evapotranspiration", "streamflow"]
    if model == "xaj_snow":
        return base + ["temperature_mean"]
    return base


def _write_config(repo: Path, basin: str, model: str, rep: int, out_root: Path) -> Path:
    cfg_dir = repo / "configs" / "_generated_rep_budget"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    run_name = f"{basin}_{model}_rep{rep}"
    output_dir = out_root / run_name
    cfg = {
        "data": {
            "dataset": "caravan",
            "path": None,
            "basin_ids": [basin],
            "warmup_length": 365,
            "variables": _vars_for_model(model),
            "datasource_kwargs": {"region": "US"},
            "train_period": ["1985-10-01", "1995-09-30"],
            "test_period": ["2005-10-01", "2014-09-30"],
            "output_dir": str(output_dir.as_posix()),
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
    path = cfg_dir / f"{run_name}.yaml"
    path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return path


def _cali_dir(output_dir: Path, model: str) -> Path:
    return output_dir / f"{model}_SCE_UA"


def _read_metrics(cali: Path) -> dict | None:
    mpath = cali / "evaluation_test" / "basins_metrics.csv"
    if not mpath.exists():
        return None
    import pandas as pd

    df = pd.read_csv(mpath)
    if len(df) == 0:
        return None
    row = df.iloc[0]
    return {
        "NSE": float(row["NSE"]) if "NSE" in row else float("nan"),
        "KGE": float(row["KGE"]) if "KGE" in row else float("nan"),
        "RMSE": float(row["RMSE"]) if "RMSE" in row else float("nan"),
        "source_csv": str(mpath.as_posix()),
    }


def _run_one(
    repo: Path,
    py: str,
    basin: str,
    model: str,
    rep: int,
    out_root: Path,
    reuse: bool,
) -> dict:
    key = (basin, model, rep)
    t0 = time.time()
    status = "ok"
    err = ""
    source = "new_run"
    cali = None

    if reuse and key in REUSE_MAP:
        src = repo / REUSE_MAP[key]
        dest_root = out_root / f"{basin}_{model}_rep{rep}"
        dest = dest_root / f"{model}_SCE_UA"
        dest_root.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            # symlink/junction not portable on all Windows setups; copy tree lightly via link of metrics
            shutil.copytree(src, dest, dirs_exist_ok=True)
        cali = dest
        source = f"reused:{REUSE_MAP[key]}"
    else:
        cfg = _write_config(repo, basin, model, rep, out_root)
        output_dir = out_root / f"{basin}_{model}_rep{rep}"
        cali = _cali_dir(output_dir, model)
        metrics_existing = _read_metrics(cali)
        if metrics_existing is not None:
            source = "resume_skip_existing"
        else:
            try:
                subprocess.run(
                    [py, str(repo / "scripts" / "run_xaj_calibration.py"), "--config", str(cfg)],
                    cwd=str(repo),
                    check=True,
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
                )
            except subprocess.CalledProcessError as exc:
                status = "failed"
                err = str(exc)

    elapsed = time.time() - t0
    metrics = _read_metrics(cali) if cali is not None else None
    if metrics is None and status == "ok":
        status = "missing_metrics"
    row = {
        "basin_id": basin,
        "model": model,
        "rep": rep,
        "status": status,
        "source": source,
        "elapsed_sec": round(elapsed, 1),
        "NSE": metrics["NSE"] if metrics else "",
        "KGE": metrics["KGE"] if metrics else "",
        "RMSE": metrics["RMSE"] if metrics else "",
        "source_csv": metrics["source_csv"] if metrics else "",
        "error": err,
    }
    return row


def _write_md(rows: list[dict], path: Path) -> None:
    lines = [
        "# SCE-UA rep budget sensitivity",
        "",
        "Purpose: show that XAJ-MZ underperformance on snowy `camels_01013500` is not from under-budgeting,",
        "and that XAJ-Snow gains are not an artifact of the two extra snow degrees of freedom alone.",
        "",
        "Protocol: SCE-UA + KGE; train 1985-10-01–1995-09-30; test 2005-10-01–2014-09-30; warmup=365.",
        "All metrics from `evaluation_test/basins_metrics.csv` (no fabricated values).",
        "",
        "| basin | model | rep | NSE | KGE | RMSE | status | source |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    for r in sorted(rows, key=lambda x: (x["basin_id"], x["model"], int(x["rep"]))):
        lines.append(
            f"| {r['basin_id']} | {r['model']} | {r['rep']} | {r['NSE']} | {r['KGE']} | {r['RMSE']} | {r['status']} | {r['source']} |"
        )
    lines += [
        "",
        "## Notes",
        "- `rep=800` rows reuse the go/no-go medium runs when present.",
        "- If higher `rep` cells are empty/`未运行`, see `RUN_REP_BUDGET_SENSITIVITY.ps1` long-run command.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    repo = _repo()
    ap = argparse.ArgumentParser()
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--reps", default="200,800,2000,5000")
    ap.add_argument("--basins", default=",".join(BASINS))
    ap.add_argument("--models", default=",".join(MODELS))
    ap.add_argument("--out-root", default=str(repo / "results" / "diagnostics" / "rep_budget"))
    ap.add_argument("--csv", default=str(repo / "results" / "diagnostics" / "rep_budget_sensitivity.csv"))
    ap.add_argument("--md", default=str(repo / "results" / "diagnostics" / "rep_budget_sensitivity.md"))
    ap.add_argument("--no-reuse", action="store_true")
    ap.add_argument(
        "--dry-write-only",
        action="store_true",
        help="Only write configs + summarize existing; do not launch calibrations.",
    )
    args = ap.parse_args()

    reps = [int(x) for x in args.reps.split(",") if x.strip()]
    basins = [b.strip() for b in args.basins.split(",") if b.strip()]
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for basin in basins:
        for model in models:
            for rep in reps:
                print(f"=== {basin} {model} rep={rep} ===", flush=True)
                if args.dry_write_only:
                    cfg = _write_config(repo, basin, model, rep, out_root)
                    cali = _cali_dir(out_root / f"{basin}_{model}_rep{rep}", model)
                    metrics = _read_metrics(cali)
                    if metrics is None and (not args.no_reuse) and (basin, model, rep) in REUSE_MAP:
                        metrics = _read_metrics(repo / REUSE_MAP[(basin, model, rep)])
                        source = f"reused:{REUSE_MAP[(basin, model, rep)]}"
                    else:
                        source = "existing_or_missing"
                    rows.append(
                        {
                            "basin_id": basin,
                            "model": model,
                            "rep": rep,
                            "status": "ok" if metrics else "未运行",
                            "source": source,
                            "elapsed_sec": "",
                            "NSE": metrics["NSE"] if metrics else "",
                            "KGE": metrics["KGE"] if metrics else "",
                            "RMSE": metrics["RMSE"] if metrics else "",
                            "source_csv": metrics["source_csv"] if metrics else "",
                            "error": "",
                            "config": str(cfg.as_posix()),
                        }
                    )
                else:
                    rows.append(
                        _run_one(
                            repo,
                            args.python,
                            basin,
                            model,
                            rep,
                            out_root,
                            reuse=not args.no_reuse,
                        )
                    )
                # Incremental save
                csv_path = Path(args.csv)
                csv_path.parent.mkdir(parents=True, exist_ok=True)
                with csv_path.open("w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                    w.writeheader()
                    w.writerows(rows)
                _write_md(rows, Path(args.md))

    print(json.dumps({"n_rows": len(rows), "csv": args.csv, "md": args.md}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
