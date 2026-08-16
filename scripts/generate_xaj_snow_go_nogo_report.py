"""Write go/no-go markdown + HTML from real evaluation CSV/NetCDF (no invented metrics).

Figures use SciencePlots + Times New Roman via ``plot_style`` and are also written
to ``results/figures/`` (PNG@300dpi + PDF) for paper reuse.
"""

from __future__ import annotations

import argparse
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

EXPERIMENTS = [
    {
        "key": "hist_010_mz_scipy",
        "basin": "camels_01013500",
        "model": "XAJ-MZ (historical scipy)",
        "rep": "v2 refine",
        "glob": "results/multi_basin_global_then_refine_v2/camels_01013500/xaj_mz_scipy/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/multi_basin_global_then_refine_v2/camels_01013500/xaj_mz_scipy/evaluation_test/*evaluation*.nc",
    },
    {
        "key": "smoke_010_mz",
        "basin": "camels_01013500",
        "model": "XAJ-MZ smoke",
        "rep": 120,
        "glob": "results/xaj_snow_go_nogo/smoke_camels_01013500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/xaj_snow_go_nogo/smoke_camels_01013500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/*evaluation*.nc",
    },
    {
        "key": "smoke_010_snow",
        "basin": "camels_01013500",
        "model": "XAJ-Snow smoke",
        "rep": 120,
        "glob": "results/xaj_snow_go_nogo/smoke_camels_01013500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/xaj_snow_go_nogo/smoke_camels_01013500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/*evaluation*.nc",
    },
    {
        "key": "med_010_mz",
        "basin": "camels_01013500",
        "model": "XAJ-MZ",
        "rep": 800,
        "glob": "results/xaj_snow_go_nogo/camels_01013500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/xaj_snow_go_nogo/camels_01013500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/*evaluation*.nc",
    },
    {
        "key": "med_010_snow",
        "basin": "camels_01013500",
        "model": "XAJ-Snow",
        "rep": 800,
        "glob": "results/xaj_snow_go_nogo/camels_01013500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/xaj_snow_go_nogo/camels_01013500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/*evaluation*.nc",
    },
    {
        "key": "refine_010_snow",
        "basin": "camels_01013500",
        "model": "XAJ-Snow scipy refine",
        "rep": "scipy",
        "glob": "results/xaj_snow_go_nogo/camels_01013500_xaj_snow_refine_scipy/xaj_snow_scipy/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/xaj_snow_go_nogo/camels_01013500_xaj_snow_refine_scipy/xaj_snow_scipy/evaluation_test/*evaluation*.nc",
    },
    {
        "key": "hist_143_mz_scipy",
        "basin": "camels_14306500",
        "model": "XAJ-MZ (historical scipy)",
        "rep": "v2 refine",
        "glob": "results/multi_basin_global_then_refine_v2/camels_14306500/xaj_mz_scipy/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/multi_basin_global_then_refine_v2/camels_14306500/xaj_mz_scipy/evaluation_test/*evaluation*.nc",
    },
    {
        "key": "med_143_mz",
        "basin": "camels_14306500",
        "model": "XAJ-MZ",
        "rep": 800,
        "glob": "results/xaj_snow_go_nogo/camels_14306500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/xaj_snow_go_nogo/camels_14306500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/*evaluation*.nc",
    },
    {
        "key": "med_143_snow",
        "basin": "camels_14306500",
        "model": "XAJ-Snow",
        "rep": 800,
        "glob": "results/xaj_snow_go_nogo/camels_14306500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/basins_metrics.csv",
        "nc_glob": "results/xaj_snow_go_nogo/camels_14306500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/*evaluation*.nc",
    },
]


def _load_metrics(csv_path: Path) -> dict[str, float] | None:
    if not csv_path.exists():
        return None
    df = pd.read_csv(csv_path, index_col=0)
    if df.empty:
        return None
    row = df.iloc[0]
    return {c: float(row[c]) for c in df.columns if pd.notna(row[c])}


def _series_from_nc(nc_path: Path, basin: str):
    ds = xr.open_dataset(nc_path)
    try:
        qobs = next((ds[n] for n in ("qobs", "streamflow", "Q_obs") if n in ds), None)
        qsim = next((ds[n] for n in ("qsim", "streamflow_sim", "Q_sim") if n in ds), None)
        if qobs is None or qsim is None:
            return None
        if "basin" in qobs.dims:
            qobs = qobs.sel(basin=basin)
            qsim = qsim.sel(basin=basin)
        obs = np.asarray(qobs.values, dtype=float).squeeze()
        sim = np.asarray(qsim.values, dtype=float).squeeze()
        t = pd.to_datetime(ds["time"].values) if "time" in ds.coords else np.arange(len(obs))
        return t, obs, sim
    finally:
        ds.close()


def _plot_bar(rows: list[dict], fig_dir: Path) -> str | None:
    # Prefer medium paired 4-group comparison when available.
    preferred_keys = {"med_010_mz", "med_010_snow", "med_143_mz", "med_143_snow"}
    usable = [r for r in rows if r.get("NSE") is not None and r["key"] in preferred_keys]
    if len(usable) < 4:
        usable = [r for r in rows if r.get("NSE") is not None]
    if not usable:
        return None
    labels = [f"{r['basin'].replace('camels_', '')}\n{r['model']}" for r in usable]
    nse = [r["NSE"] for r in usable]
    kge = [r.get("KGE", np.nan) for r in usable]
    x = np.arange(len(labels))
    w = 0.36
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.bar(x - w / 2, nse, width=w, label="NSE", color=COLORS["nse"], zorder=3)
    ax.bar(x + w / 2, kge, width=w, label="KGE", color=COLORS["kge"], zorder=3)
    ax.axhline(0.5, color="#E69F00", ls="--", lw=0.9, label="NSE=0.5", zorder=2)
    ax.axhline(0, color=COLORS["grid"], lw=0.7, zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Metric value")
    ax.set_title("Go/no-go test-period metrics (from basins_metrics.csv)")
    ax.legend(loc="best", ncol=3)
    save_fig(fig, fig_dir / "report_go_nogo_metrics_bar", close=False)
    return fig_to_png_b64(fig, dpi=300, close=True)


def _plot_hydrograph(nc_path: Path, basin: str, title: str, fig_stem: Path | None) -> str | None:
    series = _series_from_nc(nc_path, basin)
    if series is None:
        return None
    t, obs, sim = series
    fig, ax = plt.subplots(figsize=(8.0, 3.2))
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


def _plot_paired(
    mz_nc: Path,
    snow_nc: Path,
    basin: str,
    title: str,
    fig_stem: Path,
    *,
    shade_spring: bool,
) -> str | None:
    a = _series_from_nc(mz_nc, basin)
    b = _series_from_nc(snow_nc, basin)
    if a is None or b is None:
        return None
    t, obs, sim_mz = a
    t2, _, sim_sn = b
    if hasattr(t, "values") and hasattr(t2, "values") and not np.array_equal(t.values, t2.values):
        return None
    fig, ax = plt.subplots(figsize=(8.0, 3.3))
    if shade_spring and hasattr(t, "year"):
        labeled = False
        for y in sorted(set(t.year)):
            start, end = pd.Timestamp(f"{y}-03-01"), pd.Timestamp(f"{y}-05-31")
            if end < t.min() or start > t.max():
                continue
            ax.axvspan(
                max(start, t.min()),
                min(end, t.max()),
                color=COLORS["spring"],
                alpha=0.12,
                lw=0,
                label="Mar–May" if not labeled else None,
            )
            labeled = True
    ax.plot(t, obs, color=COLORS["obs"], lw=0.85, label="Observed")
    ax.plot(t, sim_mz, color=COLORS["mz"], lw=0.9, alpha=0.9, label="XAJ-MZ")
    ax.plot(t, sim_sn, color=COLORS["snow"], lw=0.9, alpha=0.9, label="XAJ-Snow")
    ax.set_title(title)
    ax.set_ylabel("Streamflow (mm d$^{-1}$)")
    ax.legend(loc="upper right", ncol=2)
    if hasattr(t, "year"):
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    save_fig(fig, fig_stem, close=False)
    return fig_to_png_b64(fig, dpi=300, close=True)


def _fmt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def _collect(repo: Path) -> list[dict]:
    rows = []
    for exp in EXPERIMENTS:
        hits = sorted(repo.glob(exp["glob"]))
        m = _load_metrics(hits[0]) if hits else None
        row = dict(exp)
        if m:
            row.update(m)
        nc_hits = sorted(repo.glob(exp["nc_glob"]))
        row["nc"] = str(nc_hits[0]) if nc_hits else None
        rows.append(row)
    return rows


def _go_nogo_verdict(rows: list[dict]) -> str:
    mz = next((r for r in rows if r["key"] == "med_010_mz" and r.get("NSE") is not None), None)
    snow = next((r for r in rows if r["key"] == "med_010_snow" and r.get("NSE") is not None), None)
    hist = next((r for r in rows if r["key"] == "hist_010_mz_scipy" and r.get("NSE") is not None), None)
    mz143 = next((r for r in rows if r["key"] == "med_143_mz" and r.get("NSE") is not None), None)
    snow143 = next(
        (r for r in rows if r["key"] == "med_143_snow" and r.get("NSE") is not None), None
    )
    mz_nse = mz["NSE"] if mz else (hist["NSE"] if hist else None)
    snow_nse = snow["NSE"] if snow else None
    if snow_nse is None or mz_nse is None:
        return (
            "尚无成对 medium 测试期 NSE，不能下 go/no-go 结论。"
            "请先跑 `RUN_GO_NOGO_XAJ_SNOW.ps1 medium`。"
        )
    delta = snow_nse - mz_nse
    ctrl = ""
    if mz143 is not None and snow143 is not None:
        d143 = snow143["NSE"] - mz143["NSE"]
        ctrl = (
            f" 负对照 14306500：XAJ-Snow NSE={snow143['NSE']:.3f} vs XAJ-MZ "
            f"{mz143['NSE']:.3f}（Δ={d143:+.3f}）"
            + ("，无明显虚假提升。" if abs(d143) < 0.05 else "，存在性能漂移，需警惕额外参数。")
        )
    if snow_nse > 0.5 and delta > 0.1:
        return (
            f"**GO（全速推进 XAJ-Snow）**：01013500 XAJ-Snow NSE={snow_nse:.3f}，"
            f"对照 XAJ-MZ NSE={mz_nse:.3f}（Δ={delta:+.3f}），达到 >0.5 且明显提升。"
            f"{ctrl}"
        )
    if delta > 0.15:
        return (
            f"**有条件 GO**：01013500 XAJ-Snow NSE={snow_nse:.3f} vs XAJ-MZ {mz_nse:.3f}"
            f"（Δ={delta:+.3f}）提升明显，但未稳定超过 0.5。建议加大 rep / scipy 精修后再批量。"
            f"{ctrl}"
        )
    if abs(delta) < 0.05:
        return (
            f"**NO-GO（转向率定协议/区域化）**：01013500 XAJ-Snow NSE={snow_nse:.3f} vs "
            f"XAJ-MZ {mz_nse:.3f}（Δ={delta:+.3f}）几乎无增益。融雪假说在本设定下未立住。"
            f"{ctrl}"
        )
    if delta > 0:
        return (
            f"**弱支持**：01013500 XAJ-Snow NSE={snow_nse:.3f} vs XAJ-MZ {mz_nse:.3f}"
            f"（Δ={delta:+.3f}）有增益但不够大。不要宣称修好，先加大率定预算或检查度日公式。"
            f"{ctrl}"
        )
    return (
        f"**NO-GO**：01013500 XAJ-Snow NSE={snow_nse:.3f} 差于 XAJ-MZ {mz_nse:.3f}"
        f"（Δ={delta:+.3f}）。不要全速推进融雪主线。"
        f"{ctrl}"
    )


def write_markdown(repo: Path, rows: list[dict], verdict: str) -> Path:
    out = repo / "results" / "diagnostics" / "xaj_snow_go_nogo.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# XAJ-Snow go/no-go 诊断",
        "",
        f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "- 指标均来自 `evaluation_test/basins_metrics.csv`，禁止口算编造。",
        "- 训练期 1985-10-01–1995-09-30；测试期 2005-10-01–2014-09-30；warmup=365。",
        "- 主线目标函数：SCE-UA + KGE。historical 对照为 v2 scipy(NSE) 精修。",
        f"- 绘图样式：{style_notes()}",
        "",
        "## 假说",
        "",
        "01013500（frac_snow≈0.37）XAJ-MZ 差是因为无融雪、降雪被当降雨立刻产流；",
        "14306500（frac_snow≈0）为负对照。人类活动解释已否定（hft 30.6 vs 34.3）。",
        "",
        "## 测试期指标",
        "",
        "| key | basin | model | rep | NSE | KGE | RMSE | 来源 |",
        "|-----|-------|-------|-----|-----|-----|------|------|",
    ]
    for r in rows:
        src = r["glob"] if r.get("NSE") is not None else "（尚未运行）"
        lines.append(
            f"| {r['key']} | {r['basin']} | {r['model']} | {r['rep']} | "
            f"{_fmt(r.get('NSE'))} | {_fmt(r.get('KGE'))} | {_fmt(r.get('RMSE'))} | `{src}` |"
        )
    lines.extend(["", "## 判据结论", "", verdict, ""])
    lines.extend(
        [
            "## 下一步命令",
            "",
            "```powershell",
            "cd d:\\Projects\\hydromodel-0.3.2\\hydromodel-0.3.2",
            ".\\RUN_GO_NOGO_XAJ_SNOW.ps1 smoke    # 验证 pipeline",
            ".\\RUN_GO_NOGO_XAJ_SNOW.ps1 medium   # rep=800 成对对比",
            ".\\RUN_GO_NOGO_XAJ_SNOW.ps1 refine   # 可选 scipy NSE 精修",
            "```",
            "",
        ]
    )
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_html(repo: Path, rows: list[dict], verdict: str, md_path: Path) -> Path:
    out = repo / "results" / "reports" / "xaj_snow_go_nogo_report.html"
    fig_dir = repo / "results" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)

    bar = _plot_bar(rows, fig_dir) or ""
    hydro_imgs: list[tuple[str, str]] = []

    by_key = {r["key"]: r for r in rows}
    paired_specs = [
        (
            "med_010_mz",
            "med_010_snow",
            "camels_01013500 medium: Observed / XAJ-MZ / XAJ-Snow",
            fig_dir / "report_01013500_paired_hydrograph",
            True,
        ),
        (
            "med_143_mz",
            "med_143_snow",
            "camels_14306500 medium negative control: Observed / XAJ-MZ / XAJ-Snow",
            fig_dir / "report_14306500_paired_hydrograph",
            False,
        ),
    ]
    for mz_key, snow_key, title, stem, spring in paired_specs:
        mz, sn = by_key.get(mz_key), by_key.get(snow_key)
        if not mz or not sn or not mz.get("nc") or not sn.get("nc"):
            continue
        img = _plot_paired(
            Path(mz["nc"]), Path(sn["nc"]), mz["basin"], title, stem, shade_spring=spring
        )
        if img:
            hydro_imgs.append((title, img))

    # Additional single-run hydrographs for remaining rows with NC (skip duplicates).
    shown = {mz_key for mz_key, *_ in paired_specs} | {snow_key for _, snow_key, *_ in paired_specs}
    for r in rows:
        if r["key"] in shown or not r.get("nc"):
            continue
        title = f"{r['basin']} {r['model']} (rep={r['rep']})"
        safe = r["key"].replace("/", "_")
        img = _plot_hydrograph(Path(r["nc"]), r["basin"], title, fig_dir / f"report_hydro_{safe}")
        if img:
            hydro_imgs.append((title, img))

    hdr = "".join(f"<th>{c}</th>" for c in ["basin", "model", "rep", "NSE", "KGE", "RMSE"])
    body = []
    for r in rows:
        body.append(
            "<tr>"
            + "".join(
                f"<td>{_fmt(r.get(c))}</td>"
                for c in ["basin", "model", "rep", "NSE", "KGE", "RMSE"]
            )
            + "</tr>"
        )
    table = f"<table><thead><tr>{hdr}</tr></thead><tbody>{''.join(body)}</tbody></table>"
    hydro_html = ""
    for title, b64 in hydro_imgs:
        hydro_html += f"<h3>{title}</h3><img alt='{title}' src='data:image/png;base64,{b64}'/>\n"
    if not hydro_html:
        hydro_html = "<p>尚无 evaluation NetCDF。</p>"
    bar_html = (
        f"<img alt='metrics' src='data:image/png;base64,{bar}'/>" if bar else "<p>无已完成指标可绘图。</p>"
    )
    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/>
<title>XAJ-Snow go/no-go</title>
<style>
body {{ font-family: "Times New Roman", "Segoe UI","Microsoft YaHei",serif; margin: 2rem; color:#0f172a; }}
table {{ border-collapse: collapse; width:100%; }}
th,td {{ border:1px solid #cbd5e1; padding:0.4rem 0.6rem; }}
th {{ background:#e2e8f0; }}
.summary {{ background:#f1f5f9; padding:1rem; border-radius:8px; }}
img {{ max-width:100%; height:auto; border:1px solid #e2e8f0; margin:0.4rem 0 1.2rem; }}
</style></head><body>
<h1>XAJ-Snow go/no-go 报告</h1>
<p class="summary">生成时间 {datetime.now().strftime('%Y-%m-%d %H:%M')}。数字只来自 CSV/NetCDF。
绘图：{style_notes()}。落地矢量/位图见 <code>results/figures/</code>。笔记：<code>{md_path.as_posix()}</code></p>
<h2>结论</h2><p>{verdict}</p>
<h2>测试期指标</h2>{table}
<h3>柱状图</h3>{bar_html}
<h2>过程线</h2>{hydro_html}
</body></html>
"""
    out.write_text(html, encoding="utf-8")
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", default=str(REPO))
    args = p.parse_args()
    repo = Path(args.repo).resolve()
    apply_plot_style(base_size=10)
    rows = _collect(repo)
    verdict = _go_nogo_verdict(rows)
    md = write_markdown(repo, rows, verdict)
    html = write_html(repo, rows, verdict, md)
    print(f"Wrote {md}")
    print(f"Wrote {html}")
    print(verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
