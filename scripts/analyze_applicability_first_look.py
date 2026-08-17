"""First-look applicability: ΔNSE (snow − mz) vs frac_snow from batch metrics.

Reads results/batch/metrics_summary.csv + sample attributes; writes CSV/MD/figures.
Uses scripts.plot_style.apply_plot_style (SciencePlots) without changing its API.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> int:
    repo = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics", default=str(repo / "results" / "batch" / "metrics_summary.csv"))
    ap.add_argument("--sample", default=str(repo / "results" / "sampling" / "sample_frozen.csv"))
    ap.add_argument("--out-csv", default=str(repo / "results" / "diagnostics" / "applicability_first_look.csv"))
    ap.add_argument("--out-md", default=str(repo / "results" / "diagnostics" / "applicability_first_look.md"))
    ap.add_argument("--fig-dir", default=str(repo / "results" / "figures"))
    args = ap.parse_args()

    metrics_path = Path(args.metrics)
    if not metrics_path.exists():
        Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_md).write_text(
            "# Applicability first look\n\n**未运行**：尚无 `results/batch/metrics_summary.csv`。\n"
            "请先跑小批次：`.\\RUN_BATCH_CALIBRATION.ps1 24 400 1`\n",
            encoding="utf-8",
        )
        print("No metrics yet; wrote placeholder MD.")
        return 0

    m = pd.read_csv(metrics_path)
    m = m[m["status"].isin(["ok", "skipped_existing"])].copy()
    m["NSE"] = pd.to_numeric(m["NSE"], errors="coerce")
    wide = m.pivot_table(index="basin_id", columns="model", values="NSE", aggfunc="first")
    if "xaj_snow" not in wide.columns or "xaj_mz" not in wide.columns:
        raise SystemExit("Need both xaj_snow and xaj_mz NSE columns in metrics.")
    wide = wide.dropna(subset=["xaj_snow", "xaj_mz"])
    wide["delta_NSE"] = wide["xaj_snow"] - wide["xaj_mz"]

    sample = pd.read_csv(args.sample)
    attrs = sample.drop_duplicates("basin_id")[
        [c for c in ("basin_id", "region_folder", "frac_snow", "aridity", "dor_pc_pva", "snow_bin", "arid_bin", "dor_bin") if c in sample.columns]
    ]
    out = wide.reset_index().merge(attrs, on="basin_id", how="left")
    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_path, index=False)

    # Summary stats
    def _med(s):
        s = pd.to_numeric(s, errors="coerce").dropna()
        return float(s.median()) if len(s) else float("nan")

    snowy = out[out["frac_snow"] >= 0.1] if "frac_snow" in out.columns else out.iloc[0:0]
    dry = out[out["frac_snow"] < 0.1] if "frac_snow" in out.columns else out.iloc[0:0]

    lines = [
        "# Applicability first look (batch)",
        "",
        f"- Source metrics: `{metrics_path.as_posix()}`",
        f"- Paired basins with both models: **{len(out)}**",
        f"- Median ΔNSE (snow−mz) overall: `{_med(out['delta_NSE']):.4f}`",
        f"- Snowy (frac_snow≥0.1) n={len(snowy)} median ΔNSE=`{_med(snowy['delta_NSE']):.4f}` median NSE_snow=`{_med(snowy['xaj_snow']):.4f}` median NSE_mz=`{_med(snowy['xaj_mz']):.4f}`",
        f"- Low-snow (frac_snow<0.1) n={len(dry)} median ΔNSE=`{_med(dry['delta_NSE']):.4f}` median NSE_snow=`{_med(dry['xaj_snow']):.4f}` median NSE_mz=`{_med(dry['xaj_mz']):.4f}`",
        "",
        "## Region counts",
        "",
    ]
    if "region_folder" in out.columns:
        lines.append(out.groupby("region_folder").size().to_string())
    lines += ["", f"## Data table", f"`{out_path.as_posix()}`", ""]
    Path(args.out_md).write_text("\n".join(lines), encoding="utf-8")

    # Figures
    try:
        import matplotlib.pyplot as plt
        import sys

        sys.path.insert(0, str(repo / "scripts"))
        from plot_style import apply_plot_style, COLORS, save_fig

        apply_plot_style()
        fig_dir = Path(args.fig_dir)
        fig_dir.mkdir(parents=True, exist_ok=True)

        fig, ax = plt.subplots(figsize=(4.2, 3.2))
        ax.axhline(0.0, color=COLORS["grid"], lw=0.8)
        ax.scatter(
            out["frac_snow"],
            out["delta_NSE"],
            c=COLORS["snow"],
            s=28,
            alpha=0.85,
            edgecolors="none",
        )
        ax.set_xlabel("frac_snow")
        ax.set_ylabel(r"$\Delta$NSE (XAJ-Snow $-$ XAJ-MZ)")
        save_fig(fig, fig_dir / "fig_batch_delta_nse_vs_frac_snow", close=True)

        # Binned
        bins = [-0.01, 0.1, 0.3, 1.01]
        labels = ["S0 (<0.1)", "S1 (0.1–0.3)", "S2 (>0.3)"]
        out["snow_bin_plot"] = pd.cut(out["frac_snow"], bins=bins, labels=labels)
        fig, ax = plt.subplots(figsize=(4.0, 3.2))
        data = [out.loc[out["snow_bin_plot"] == lab, "delta_NSE"].dropna().values for lab in labels]
        parts = ax.boxplot(
            data,
            tick_labels=labels,
            patch_artist=True,
        )
        for box in parts["boxes"]:
            box.set_facecolor("#F0F0F0")
            box.set_edgecolor(COLORS["mz"])
        ax.axhline(0.0, color=COLORS["grid"], lw=0.8)
        ax.set_xlabel("Snow bin (S0/S1/S2)")
        ax.set_ylabel(r"$\Delta$NSE (XAJ-Snow $-$ XAJ-MZ)")
        save_fig(fig, fig_dir / "fig_batch_delta_nse_by_snow_bin", close=True)

        if "region_folder" in out.columns and out["region_folder"].nunique() > 1:
            fig, ax = plt.subplots(figsize=(5.0, 3.2))
            order = sorted(out["region_folder"].dropna().unique())
            data = [out.loc[out["region_folder"] == r, "delta_NSE"].dropna().values for r in order]
            ax.boxplot(data, tick_labels=order, patch_artist=True)
            ax.axhline(0.0, color=COLORS["grid"], lw=0.8)
            ax.set_ylabel(r"$\Delta$NSE")
            ax.set_title("ΔNSE by region")
            plt.xticks(rotation=30, ha="right")
            save_fig(fig, fig_dir / "fig_batch_delta_nse_by_region", close=True)
    except Exception as exc:  # noqa: BLE001
        with Path(args.out_md).open("a", encoding="utf-8") as f:
            f.write(f"\n\nFigure generation note: {exc}\n")

    print(f"Wrote {out_path} n={len(out)}")
    print(f"Wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
