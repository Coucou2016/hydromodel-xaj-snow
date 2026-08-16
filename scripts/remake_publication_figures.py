"""Remake go/no-go publication figures from real CSV / evaluation NetCDF.

Outputs PNG@300dpi + PDF under results/figures/. Does not invent metrics.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

from plot_style import COLORS, apply_plot_style, save_fig, style_notes

REPO = Path(__file__).resolve().parents[1]

# Medium (rep=800) paired go/no-go experiments — primary paper comparison.
PAIR_EXPERIMENTS = [
    {
        "basin": "camels_01013500",
        "model": "XAJ-MZ",
        "short": "MZ",
        "metrics": "results/xaj_snow_go_nogo/camels_01013500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/basins_metrics.csv",
        "nc": "results/xaj_snow_go_nogo/camels_01013500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/xaj_mz_evaluation_results.nc",
    },
    {
        "basin": "camels_01013500",
        "model": "XAJ-Snow",
        "short": "Snow",
        "metrics": "results/xaj_snow_go_nogo/camels_01013500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/basins_metrics.csv",
        "nc": "results/xaj_snow_go_nogo/camels_01013500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/xaj_snow_evaluation_results.nc",
    },
    {
        "basin": "camels_14306500",
        "model": "XAJ-MZ",
        "short": "MZ",
        "metrics": "results/xaj_snow_go_nogo/camels_14306500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/basins_metrics.csv",
        "nc": "results/xaj_snow_go_nogo/camels_14306500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/xaj_mz_evaluation_results.nc",
    },
    {
        "basin": "camels_14306500",
        "model": "XAJ-Snow",
        "short": "Snow",
        "metrics": "results/xaj_snow_go_nogo/camels_14306500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/basins_metrics.csv",
        "nc": "results/xaj_snow_go_nogo/camels_14306500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/xaj_snow_evaluation_results.nc",
    },
]


def _load_metrics(repo: Path, rel: str) -> dict[str, float]:
    path = repo / rel
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, index_col=0)
    row = df.iloc[0]
    return {c: float(row[c]) for c in df.columns if pd.notna(row[c])}


def _load_series(nc_path: Path, basin: str) -> tuple[pd.DatetimeIndex, np.ndarray, np.ndarray]:
    ds = xr.open_dataset(nc_path)
    try:
        qobs = ds["qobs"]
        qsim = ds["qsim"]
        if "basin" in qobs.dims:
            qobs = qobs.sel(basin=basin)
            qsim = qsim.sel(basin=basin)
        t = pd.to_datetime(ds["time"].values)
        obs = np.asarray(qobs.values, dtype=float).squeeze()
        sim = np.asarray(qsim.values, dtype=float).squeeze()
        return t, obs, sim
    finally:
        ds.close()


def plot_metrics_bar(repo: Path, out_dir: Path) -> Path:
    rows = []
    for exp in PAIR_EXPERIMENTS:
        m = _load_metrics(repo, exp["metrics"])
        rows.append(
            {
                "label": f"{exp['basin'].replace('camels_', '')}\n{exp['model']}",
                "NSE": m["NSE"],
                "KGE": m["KGE"],
                "source": exp["metrics"],
            }
        )
    labels = [r["label"] for r in rows]
    nse = [r["NSE"] for r in rows]
    kge = [r["KGE"] for r in rows]
    x = np.arange(len(labels))
    w = 0.36
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    bars_n = ax.bar(x - w / 2, nse, width=w, label="NSE", color=COLORS["nse"], zorder=3)
    bars_k = ax.bar(x + w / 2, kge, width=w, label="KGE", color=COLORS["kge"], zorder=3)
    ax.axhline(0.0, color=COLORS["grid"], lw=0.7, zorder=1)
    ax.axhline(0.5, color="#E69F00", ls="--", lw=0.9, label="NSE = 0.5", zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Metric value")
    ax.set_title("Go/no-go test-period metrics (medium, rep=800)")
    ax.legend(loc="upper left", ncol=3, columnspacing=0.8)
    ax.set_ylim(min(-0.35, min(nse) - 0.05), max(1.0, max(kge) + 0.08))
    for bars in (bars_n, bars_k):
        for b in bars:
            h = b.get_height()
            ax.annotate(
                f"{h:.3f}",
                xy=(b.get_x() + b.get_width() / 2, h),
                xytext=(0, 3 if h >= 0 else -10),
                textcoords="offset points",
                ha="center",
                va="bottom" if h >= 0 else "top",
                fontsize=7.5,
            )
    stem = out_dir / "fig_go_nogo_metrics_bar"
    save_fig(fig, stem, formats=("png", "pdf", "svg"), close=True)
    return stem


def _shade_spring(ax, t: pd.DatetimeIndex) -> None:
    years = sorted(set(t.year))
    labeled = False
    for y in years:
        start = pd.Timestamp(f"{y}-03-01")
        end = pd.Timestamp(f"{y}-05-31")
        if end < t.min() or start > t.max():
            continue
        ax.axvspan(
            max(start, t.min()),
            min(end, t.max()),
            color=COLORS["spring"],
            alpha=0.12,
            lw=0,
            label="Mar–May" if not labeled else None,
            zorder=0,
        )
        labeled = True


def plot_paired_hydrograph(
    repo: Path,
    out_dir: Path,
    *,
    basin: str,
    mz_nc: str,
    snow_nc: str,
    stem_name: str,
    title: str,
    highlight_spring: bool,
    zoom_years: tuple[int, int] | None = None,
) -> Path:
    t_mz, obs, sim_mz = _load_series(repo / mz_nc, basin)
    t_sn, _, sim_sn = _load_series(repo / snow_nc, basin)
    if not np.array_equal(t_mz.values, t_sn.values):
        raise ValueError(f"Time axes differ for {basin}")
    t = t_mz
    if zoom_years is not None:
        y0, y1 = zoom_years
        mask = (t.year >= y0) & (t.year <= y1)
        t, obs, sim_mz, sim_sn = t[mask], obs[mask], sim_mz[mask], sim_sn[mask]

    fig, ax = plt.subplots(figsize=(8.0, 3.4))
    if highlight_spring:
        _shade_spring(ax, t)
    ax.plot(t, obs, color=COLORS["obs"], lw=0.85, label="Observed", zorder=3)
    ax.plot(t, sim_mz, color=COLORS["mz"], lw=0.9, alpha=0.9, label="XAJ-MZ", zorder=2)
    ax.plot(t, sim_sn, color=COLORS["snow"], lw=0.9, alpha=0.9, label="XAJ-Snow", zorder=2)
    ax.set_ylabel("Streamflow (mm d$^{-1}$)")
    ax.set_title(title)
    ax.legend(loc="upper right", ncol=2 if highlight_spring else 3)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlim(t.min(), t.max())
    stem = out_dir / stem_name
    save_fig(fig, stem, formats=("png", "pdf", "svg"), close=True)
    return stem


def plot_scatter_obs_sim(repo: Path, out_dir: Path) -> Path | None:
    """Obs–sim scatter for 01013500 MZ vs Snow (optional diagnostic)."""
    basin = "camels_01013500"
    mz = next(e for e in PAIR_EXPERIMENTS if e["basin"] == basin and e["model"] == "XAJ-MZ")
    sn = next(e for e in PAIR_EXPERIMENTS if e["basin"] == basin and e["model"] == "XAJ-Snow")
    _, obs_mz, sim_mz = _load_series(repo / mz["nc"], basin)
    _, obs_sn, sim_sn = _load_series(repo / sn["nc"], basin)
    # Same basin/obs expected; use MZ obs as reference.
    obs = obs_mz
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), sharex=True, sharey=True)
    for ax, sim, name, color in (
        (axes[0], sim_mz, "XAJ-MZ", COLORS["mz"]),
        (axes[1], sim_sn, "XAJ-Snow", COLORS["snow"]),
    ):
        ax.scatter(obs, sim, s=4, alpha=0.25, color=color, rasterized=True, edgecolors="none")
        lim = float(np.nanmax([obs.max(), sim.max()]) * 1.05)
        ax.plot([0, lim], [0, lim], color="0.4", lw=0.8, ls="--")
        ax.set_xlim(0, lim)
        ax.set_ylim(0, lim)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(f"{basin.replace('camels_', '')} {name}")
        ax.set_xlabel("Observed (mm d$^{-1}$)")
    axes[0].set_ylabel("Simulated (mm d$^{-1}$)")
    fig.suptitle("Test-period obs–sim scatter (from evaluation NetCDF)", y=1.02, fontsize=10)
    stem = out_dir / "fig_01013500_obs_sim_scatter"
    save_fig(fig, stem, formats=("png", "pdf", "svg"), close=True)
    return stem


def write_notes(out_dir: Path, produced: list[tuple[str, str]]) -> Path:
    lines = [
        "# Figure remake notes",
        "",
        style_notes(),
        "",
        "## Data sources (real files only)",
        "",
    ]
    for exp in PAIR_EXPERIMENTS:
        m = _load_metrics(REPO, exp["metrics"])
        lines.append(
            f"- {exp['basin']} {exp['model']}: NSE={m['NSE']:.4f}, KGE={m['KGE']:.4f} "
            f"← `{exp['metrics']}`; hydrograph ← `{exp['nc']}`"
        )
    lines.extend(["", "## Produced stems", ""])
    for stem, desc in produced:
        lines.append(f"- `{stem}.{{png,pdf,svg}}` — {desc}")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Hydrograph time axis is the evaluation NetCDF test window after warmup "
            "(2006-10-01 to 2014-09-30).",
            "- Spring shading (Mar–May) on 01013500 highlights the snowmelt season where "
            "XAJ-Snow improves peak timing/volume relative to XAJ-MZ.",
            "- 14306500 is the low-snow negative control; MZ and Snow should nearly overlap.",
        ]
    )
    path = out_dir / "figure_notes.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", default=str(REPO))
    p.add_argument(
        "--out-dir",
        default=str(REPO / "results" / "figures"),
    )
    args = p.parse_args()
    repo = Path(args.repo).resolve()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    font = apply_plot_style(base_size=10)
    print(f"Using serif font: {font}")

    produced: list[tuple[str, str]] = []
    bar = plot_metrics_bar(repo, out_dir)
    produced.append((bar.name, "NSE/KGE bars for 2 basins × 2 models"))

    h010 = plot_paired_hydrograph(
        repo,
        out_dir,
        basin="camels_01013500",
        mz_nc=PAIR_EXPERIMENTS[0]["nc"],
        snow_nc=PAIR_EXPERIMENTS[1]["nc"],
        stem_name="fig_01013500_hydrograph_mz_vs_snow",
        title="camels_01013500 test hydrograph (XAJ-MZ vs XAJ-Snow)",
        highlight_spring=True,
    )
    produced.append((h010.name, "full test hydrograph with spring shading"))

    h010z = plot_paired_hydrograph(
        repo,
        out_dir,
        basin="camels_01013500",
        mz_nc=PAIR_EXPERIMENTS[0]["nc"],
        snow_nc=PAIR_EXPERIMENTS[1]["nc"],
        stem_name="fig_01013500_hydrograph_spring_zoom_2010_2012",
        title="camels_01013500 spring-focused zoom (2010–2012)",
        highlight_spring=True,
        zoom_years=(2010, 2012),
    )
    produced.append((h010z.name, "2010–2012 zoom emphasizing spring peaks"))

    h143 = plot_paired_hydrograph(
        repo,
        out_dir,
        basin="camels_14306500",
        mz_nc=PAIR_EXPERIMENTS[2]["nc"],
        snow_nc=PAIR_EXPERIMENTS[3]["nc"],
        stem_name="fig_14306500_hydrograph_mz_vs_snow",
        title="camels_14306500 negative control (XAJ-MZ vs XAJ-Snow)",
        highlight_spring=False,
    )
    produced.append((h143.name, "negative-control hydrograph"))

    scatter = plot_scatter_obs_sim(repo, out_dir)
    if scatter is not None:
        produced.append((scatter.name, "obs–sim scatter for 01013500"))

    notes = write_notes(out_dir, produced)
    print(f"Wrote notes: {notes}")
    for stem, desc in produced:
        print(f"  {stem} — {desc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
