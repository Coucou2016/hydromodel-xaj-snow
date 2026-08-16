"""
Generate a self-contained HTML iteration report for camels_01013500 work.

Reads real metrics from results/*/evaluation_test/basins_metrics.csv and
optional evaluation NetCDF for hydrographs. Embeds matplotlib PNG as base64
(SciencePlots + Times New Roman via plot_style; also writes results/figures/).
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot_style import (  # noqa: E402
    COLORS,
    apply_plot_style,
    fig_to_png_b64,
    save_fig,
    style_notes,
)


def _load_metrics(csv_path: Path) -> dict[str, float] | None:
    if not csv_path.exists():
        return None
    df = pd.read_csv(csv_path, index_col=0)
    if df.empty:
        return None
    row = df.iloc[0]
    return {c: float(row[c]) for c in df.columns if pd.notna(row[c])}


def _find_metrics(repo: Path, rel_glob: str) -> dict[str, float] | None:
    hits = sorted(repo.glob(rel_glob))
    if not hits:
        return None
    return _load_metrics(hits[0])


def _plot_metrics_bar(rows: list[dict], fig_dir: Path) -> str:
    labels = [r["label"] for r in rows if r.get("NSE") is not None]
    nse = [r["NSE"] for r in rows if r.get("NSE") is not None]
    kge = [r.get("KGE", np.nan) for r in rows if r.get("NSE") is not None]
    x = np.arange(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    ax.bar(x - w / 2, nse, width=w, label="NSE", color=COLORS["nse"], zorder=3)
    ax.bar(x + w / 2, kge, width=w, label="KGE", color=COLORS["kge"], zorder=3)
    ax.axhline(0, color=COLORS["grid"], lw=0.7, zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.set_ylabel("Metric value")
    ax.set_title("camels_01013500 test-period metrics")
    ax.legend(loc="best")
    save_fig(fig, fig_dir / "report_iteration_metrics_bar", close=False)
    return fig_to_png_b64(fig, dpi=300, close=True)


def _plot_hydrograph_from_nc(
    nc_path: Path, basin: str, title: str, fig_stem: Path | None
) -> str | None:
    if not nc_path.exists():
        return None
    ds = xr.open_dataset(nc_path)
    try:
        qobs = None
        qsim = None
        for obs_name in ("qobs", "streamflow", "Q_obs"):
            if obs_name in ds:
                qobs = ds[obs_name]
                break
        for sim_name in ("qsim", "streamflow_sim", "Q_sim"):
            if sim_name in ds:
                qsim = ds[sim_name]
                break
        if qobs is None or qsim is None:
            return None
        if "basin" in qobs.dims:
            qobs = qobs.sel(basin=basin)
            qsim = qsim.sel(basin=basin)
        obs = np.asarray(qobs.values).squeeze()
        sim = np.asarray(qsim.values).squeeze()
        t = pd.to_datetime(ds["time"].values) if "time" in ds.coords else np.arange(len(obs))
        fig, ax = plt.subplots(figsize=(9.5, 3.4))
        ax.plot(t, obs, color=COLORS["obs"], lw=0.85, label="Observed")
        ax.plot(t, sim, color=COLORS["mz"], lw=0.9, alpha=0.9, label="Simulated")
        ax.set_title(title)
        ax.set_ylabel("Streamflow (mm d$^{-1}$)")
        ax.legend(loc="upper right")
        if hasattr(t, "year"):
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        if fig_stem is not None:
            save_fig(fig, fig_stem, close=False)
        return fig_to_png_b64(fig, dpi=300, close=True)
    finally:
        ds.close()


EXPERIMENTS = [
    {
        "label": "baseline v2 scipy",
        "glob": "results/multi_basin_global_then_refine_v2/camels_01013500/xaj_mz_scipy/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/multi_basin_global_then_refine_v2/camels_01013500/xaj_mz_scipy/evaluation_test/*evaluation*.nc",
        "note": "历史最佳对照 (~NSE 0.139)",
    },
    {
        "label": "refine scipy (single)",
        "glob": "results/real_caravan_camels_01013500_refine_scipy/xaj_mz_scipy/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/real_caravan_camels_01013500_refine_scipy/xaj_mz_scipy/evaluation_test/*evaluation*.nc",
    },
    {
        "label": "smoke SCE-UA (KGE, rep=80)",
        "glob": "results/real_caravan_camels_01013500_extended_sceua_smoke/xaj_mz_SCE_UA/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/real_caravan_camels_01013500_extended_sceua_smoke/xaj_mz_SCE_UA/evaluation_test/*evaluation*.nc",
    },
    {
        "label": "smoke scipy refine",
        "glob": "results/real_caravan_camels_01013500_extended_refine_scipy_smoke/xaj_mz_scipy/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/real_caravan_camels_01013500_extended_refine_scipy_smoke/xaj_mz_scipy/evaluation_test/*evaluation*.nc",
    },
    {
        "label": "extended scipy (full)",
        "glob": "results/real_caravan_camels_01013500_extended_refine_scipy/xaj_mz_scipy/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/real_caravan_camels_01013500_extended_refine_scipy/xaj_mz_scipy/evaluation_test/*evaluation*.nc",
    },
]

CONTROL_14306500 = {
    "label": "14306500 control scipy",
    "glob": "results/multi_basin_global_then_refine_v2/camels_14306500/xaj_mz_scipy/evaluation_test/basins_metrics.csv",
    "nc_glob": "results/multi_basin_global_then_refine_v2/camels_14306500/xaj_mz_scipy/evaluation_test/*evaluation*.nc",
}


def _collect_rows(repo: Path) -> list[dict]:
    rows = []
    for exp in EXPERIMENTS + [CONTROL_14306500]:
        m = _find_metrics(repo, exp["glob"])
        row = {"label": exp["label"], "note": exp.get("note", "")}
        if m:
            row.update(m)
        rows.append(row)
    return rows


def _metrics_table_html(rows: list[dict]) -> str:
    cols = ["label", "NSE", "KGE", "RMSE", "PBIAS", "note"]
    hdr = "".join(f"<th>{c}</th>" for c in cols)
    body = []
    for r in rows:
        cells = []
        for c in cols:
            v = r.get(c, "")
            if isinstance(v, float):
                cells.append(f"<td>{v:.4f}</td>")
            else:
                cells.append(f"<td>{v}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"<table><thead><tr>{hdr}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def _find_nc(repo: Path, pattern: str) -> Path | None:
    hits = sorted(repo.glob(pattern))
    return hits[0] if hits else None


def build_report(repo: Path, out_path: Path) -> None:
    os.chdir(repo)
    if str(repo) not in os.environ.get("HOME", ""):
        os.environ["HOME"] = str(repo)
        os.environ["USERPROFILE"] = str(repo)
    os.environ.setdefault("HYDRO_SETTING_FILE", str(repo / "hydro_setting.yml"))

    apply_plot_style(base_size=10)
    fig_dir = repo / "results" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    rows = _collect_rows(repo)
    bar_rows = [r for r in rows if r.get("NSE") is not None]
    bar_png = _plot_metrics_bar(bar_rows if bar_rows else rows, fig_dir)

    hydro_imgs: list[tuple[str, str]] = []
    for key, basin, title, stem in [
        ("baseline", "camels_01013500", "01013500 baseline v2 (test period)", "report_iteration_hydro_01013500_baseline"),
        ("smoke", "camels_01013500", "01013500 smoke pipeline (test period)", "report_iteration_hydro_01013500_smoke"),
        ("control", "camels_14306500", "14306500 control (test period)", "report_iteration_hydro_14306500_control"),
    ]:
        if key == "baseline":
            nc = _find_nc(repo, EXPERIMENTS[0]["nc_glob"])
        elif key == "smoke":
            nc = _find_nc(repo, EXPERIMENTS[2]["nc_glob"])
        else:
            nc = _find_nc(repo, CONTROL_14306500["nc_glob"])
        if nc:
            img = _plot_hydrograph_from_nc(nc, basin, title, fig_dir / stem)
            if img:
                hydro_imgs.append((title, img))

    cache_dir = repo / "_portable_data" / ".cache_global_then_refine_v2"
    cache_files = sorted(cache_dir.glob("caravan_camels_timeseries_batch_*.nc")) if cache_dir.exists() else []
    diag_notes = (repo / "results/diagnostics/01013500_iteration_notes.md").read_text(encoding="utf-8") if (repo / "results/diagnostics/01013500_iteration_notes.md").exists() else ""

    status_path = repo / "results/diagnostics/smoke_pipeline_status.txt"
    pipeline_status = "未运行 smoke"
    if status_path.exists():
        try:
            pipeline_status = status_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            pipeline_status = status_path.read_text(encoding="utf-16")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<title>Hydromodel 01013500 迭代报告</title>
<style>
body {{ font-family: "Times New Roman", "Segoe UI", "Microsoft YaHei", serif; margin: 2rem; color: #0f172a; line-height: 1.5; }}
h1,h2 {{ color: #1e3a5f; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.95rem; }}
th, td {{ border: 1px solid #cbd5e1; padding: 0.45rem 0.6rem; text-align: left; }}
th {{ background: #e2e8f0; }}
img {{ max-width: 100%; height: auto; border: 1px solid #e2e8f0; margin: 0.5rem 0 1.5rem; }}
.summary {{ background: #f1f5f9; padding: 1rem 1.2rem; border-radius: 8px; }}
pre {{ background: #f8fafc; padding: 0.8rem; overflow-x: auto; font-size: 0.85rem; }}
</style>
</head>
<body>
<h1>Hydromodel camels_01013500 迭代报告</h1>
<p class="summary">生成时间：{now}。指标均来自 <code>basins_metrics.csv</code>；过程线来自 evaluation NetCDF（若存在）。绘图：{style_notes()}。图片落地：<code>results/figures/</code>。</p>

<h2>执行摘要</h2>
<ul>
<li><strong>轮 A（修复）</strong>：根因为多个 CARAVAN minicache 批次沿 <code>basin</code> 拼接导致重复测站，<code>sel(basin=...)</code> 触发 InvalidIndexError。已修复 <code>build_caravan_minicache.py</code>（剔除重叠批次）与 <code>unified_data_loader.py</code>（防御性去重）。</li>
<li><strong>轮 B（率定）</strong>：smoke 配置 SCE-UA rep=80 → scipy n_starts=2；完整 extended rep=3500 需数小时，见 RUN_EXTENDED 脚本。</li>
<li><strong>轮 C（对照）</strong>：baseline NSE≈0.139；14306500 对照 NSE≈0.801。</li>
<li><strong>pipeline 状态</strong>：<pre>{pipeline_status.strip()}</pre></li>
</ul>

<h2>数据与缓存状态</h2>
<table>
<tr><th>项目</th><th>状态</th></tr>
<tr><td>HOME / hydro_setting</td><td>指向仓库根 <code>{repo}</code></td></tr>
<tr><td>cache 目录</td><td><code>{cache_dir}</code>（{len(cache_files)} 个 batch 文件）</td></tr>
<tr><td>minicache 批次</td><td>{'<br/>'.join(p.name for p in cache_files) or '无'}</td></tr>
</table>

<h2>指标对比（测试期）</h2>
{_metrics_table_html(rows)}
<h3>柱状图</h3>
<img alt="metrics bar" src="data:image/png;base64,{bar_png}"/>

<h2>过程线</h2>
"""
    if hydro_imgs:
        for title, b64 in hydro_imgs:
            html += f"<h3>{title}</h3><img alt='{title}' src='data:image/png;base64,{b64}'/>\n"
    else:
        html += "<p>尚无 evaluation NetCDF；请先对各率定目录运行 <code>run_xaj_evaluate.py --eval-period test</code>。</p>\n"

    html += f"""
<h2>迭代日志摘录</h2>
<pre>{diag_notes[:4000]}</pre>

<h2>未完成项与建议</h2>
<ul>
<li>长跑：<code>.\\RUN_EXTENDED_01013500_SCEUA.ps1</code>（rep=3500 + scipy + evaluate）</li>
<li>若 NSE 仍 &lt;0.2：尝试 ERA5 PET、log-NSE、或增加 n_starts / rep</li>
<li>多流域 batch cache 勿重叠；重建 minicache 会自动清理含相同 basin 的旧文件</li>
</ul>
</body>
</html>
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote report: {out_path}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--output",
        default=str(REPO / "results/reports/hydromodel_iteration_report.html"),
    )
    args = p.parse_args()
    build_report(REPO, Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
