#!/usr/bin/env python3
"""Generate self-contained XAJ-Snow manuscript + research report (HTML/MD/PDF).

Reads real metrics from basins_metrics.csv and embeds PNG figures as base64.
Does not invent metrics. Does not modify model code or delete data.
"""
from __future__ import annotations

import base64
import csv
import html
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "results" / "publications"
FIG = REPO / "results" / "figures"

METRIC_PATHS = {
    ("01013500", "mz"): REPO
    / "results/xaj_snow_go_nogo/camels_01013500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/basins_metrics.csv",
    ("01013500", "snow"): REPO
    / "results/xaj_snow_go_nogo/camels_01013500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/basins_metrics.csv",
    ("14306500", "mz"): REPO
    / "results/xaj_snow_go_nogo/camels_14306500_xaj_mz/xaj_mz_SCE_UA/evaluation_test/basins_metrics.csv",
    ("14306500", "snow"): REPO
    / "results/xaj_snow_go_nogo/camels_14306500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/basins_metrics.csv",
}
PARAM_PATHS = {
    "01013500": REPO
    / "results/xaj_snow_go_nogo/camels_01013500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/basins_denorm_params.csv",
    "14306500": REPO
    / "results/xaj_snow_go_nogo/camels_14306500_xaj_snow/xaj_snow_SCE_UA/evaluation_test/basins_denorm_params.csv",
}
REFINE_PATHS = {
    ("01013500", "mz"): REPO
    / "results/xaj_snow_go_nogo/camels_01013500_xaj_mz_refine_scipy/xaj_mz_scipy/evaluation_test/basins_metrics.csv",
    ("01013500", "snow"): REPO
    / "results/xaj_snow_go_nogo/camels_01013500_xaj_snow_refine_scipy/xaj_snow_scipy/evaluation_test/basins_metrics.csv",
}
BATCH1_CSV = REPO / "results/diagnostics/batch1_paired_metrics.csv"
APPLICABILITY_MD = REPO / "results/diagnostics/applicability_first_look.md"
REP_BUDGET_CSV = REPO / "results/diagnostics/rep_budget_sensitivity.csv"

FIGURES = [
    {
        "id": "fig1",
        "file": "fig_go_nogo_metrics_bar.png",
        "ms_title": "Paired out-of-sample NSE and KGE for the go/no-go pilot basins",
        "rep_title": "Go/no-go 成对样本外 NSE 与 KGE 柱状对比",
        "source": "paired go/no-go basins_metrics.csv (SCE-UA+KGE, rep=800)",
    },
    {
        "id": "fig2",
        "file": "fig_01013500_hydrograph_mz_vs_snow.png",
        "ms_title": "Full test-period hydrograph for snow-affected basin 01013500",
        "rep_title": "雪影响流域 01013500 全测试期水文过程线",
        "source": "evaluation NetCDF for the test window after warmup",
    },
    {
        "id": "fig3",
        "file": "fig_01013500_hydrograph_spring_zoom_2010_2012.png",
        "ms_title": "Spring zoom (2010–2012) for basin 01013500",
        "rep_title": "01013500 春季放大过程线（2010–2012）",
        "source": "same evaluation series as Fig. 2; Mar–May spring shading",
    },
    {
        "id": "fig4",
        "file": "fig_14306500_hydrograph_mz_vs_snow.png",
        "ms_title": "Negative-control hydrograph for low-snow basin 14306500",
        "rep_title": "低雪负对照流域 14306500 水文过程线",
        "source": "evaluation NetCDF for camels_14306500",
    },
    {
        "id": "fig5",
        "file": "fig_01013500_obs_sim_scatter.png",
        "ms_title": "Observed–simulated scatter for basin 01013500",
        "rep_title": "01013500 观测–模拟散点图",
        "source": "paired daily discharge from the evaluation series",
    },
    {
        "id": "fig6",
        "file": "fig_batch_delta_nse_vs_frac_snow.png",
        "ms_title": "First-look batch ΔNSE versus catchment snow fraction (n=14, rep=200)",
        "rep_title": "Batch1 ΔNSE 随 frac_snow 散点（n=14，rep=200）",
        "source": "results/diagnostics/batch1_paired_metrics.csv",
    },
    {
        "id": "fig7",
        "file": "fig_batch_delta_nse_by_snow_bin.png",
        "ms_title": "First-look batch ΔNSE by snow-fraction bin (n=14, rep=200)",
        "rep_title": "Batch1 ΔNSE 按雪量分箱（n=14，rep=200）",
        "source": "results/diagnostics/batch1_paired_metrics.csv",
    },
]


def read_metrics(path: Path) -> dict[str, float]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise RuntimeError(f"empty metrics: {path}")
    row = rows[0]
    return {k: float(row[k]) for k in ("NSE", "KGE", "RMSE", "Bias", "Corr") if k in row}


def read_params(path: Path) -> dict[str, float]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    row = rows[0]
    out = {}
    for k in ("Kf", "CTG", "K", "B", "IM", "SM"):
        if k in row and row[k] not in ("", None):
            out[k] = float(row[k])
    return out


def img_data_uri(path: Path) -> str:
    raw = path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:image/png;base64,{b64}"


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def shared_css() -> str:
    return """
:root {
  --ink: #1a1a1a;
  --muted: #555;
  --line: #c8c8c8;
  --accent: #0b3d5c;
  --soft: #f7f5f1;
  --warn: #7a3e00;
  --ok: #1b5e3b;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: var(--ink);
  background: #fff;
  font-family: "Microsoft YaHei", "Noto Sans CJK SC", SimSun,
               "Times New Roman", "Noto Serif", "Liberation Serif", serif;
  font-size: 11.5pt;
  line-height: 1.62;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
.page {
  max-width: 920px;
  margin: 0 auto;
  padding: 28px 36px 64px;
}
h1, h2, h3, h4 {
  font-family: "Microsoft YaHei", "Noto Sans CJK SC", "Times New Roman", serif;
  color: var(--accent);
  line-height: 1.3;
  page-break-after: avoid;
}
h1 { font-size: 1.85rem; margin: 0.2em 0 0.4em; }
h2 {
  font-size: 1.35rem;
  border-bottom: 1.5px solid var(--line);
  padding-bottom: 0.25em;
  margin-top: 1.8em;
}
h3 { font-size: 1.12rem; margin-top: 1.35em; }
h4 { font-size: 1.02rem; margin-top: 1.1em; color: #244a63; }
p { margin: 0.75em 0; text-align: justify; }
.meta, .muted, .src, .caption-note { color: var(--muted); }
.cover {
  border: 1px solid var(--line);
  background: linear-gradient(180deg, #fbfaf7 0%, #fff 70%);
  padding: 36px 32px 28px;
  margin-bottom: 28px;
}
.cover .eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.78rem;
  color: var(--muted);
  font-family: "Microsoft YaHei", sans-serif;
}
.cover .subtitle { font-size: 1.05rem; color: #333; margin-top: 0.6em; }
.badge {
  display: inline-block;
  border: 1px solid #c9a227;
  color: var(--warn);
  background: #fff8e8;
  padding: 0.15em 0.55em;
  font-size: 0.85rem;
  border-radius: 3px;
  margin-right: 0.35em;
}
.toc {
  background: var(--soft);
  border: 1px solid var(--line);
  padding: 16px 22px;
  margin: 18px 0 28px;
}
.toc ol { margin: 0.4em 0 0 1.2em; padding: 0; }
.toc a { color: var(--accent); text-decoration: none; }
.toc a:hover { text-decoration: underline; }
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0 1.4em;
  font-size: 0.95rem;
  page-break-inside: avoid;
}
th, td {
  border: 1px solid var(--line);
  padding: 0.45em 0.55em;
  vertical-align: top;
}
th {
  background: #eef3f7;
  text-align: left;
  font-family: "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
}
tr:nth-child(even) td { background: #fcfcfc; }
.num { font-variant-numeric: tabular-nums; text-align: right; white-space: nowrap; }
figure {
  margin: 1.4em 0 1.8em;
  page-break-inside: avoid;
}
figure img {
  display: block;
  width: 100%;
  max-width: 100%;
  height: auto;
  border: 1px solid #ddd;
  background: #fff;
}
figcaption {
  margin-top: 0.55em;
  font-size: 0.92rem;
  color: #222;
}
.explain {
  background: #f9fbfc;
  border-left: 3px solid #7aa0b8;
  padding: 0.7em 1em;
  margin: 0.6em 0 1.2em;
}
.explain h4 { margin-top: 0.4em; }
.todo {
  border: 1px dashed #b8872c;
  background: #fff9ef;
  padding: 0.85em 1em;
  margin: 1em 0;
  color: #5a3a00;
}
.eq {
  display: block;
  margin: 0.9em auto;
  text-align: center;
  font-family: "Times New Roman", serif;
  font-size: 1.05rem;
}
.footer-note {
  margin-top: 2.5em;
  padding-top: 0.8em;
  border-top: 1px solid var(--line);
  font-size: 0.85rem;
  color: var(--muted);
}
ul, ol { margin: 0.5em 0 0.9em 1.3em; }
li { margin: 0.25em 0; }
a.ref { color: var(--accent); }
.header-bar, .footer-bar {
  font-size: 0.78rem;
  color: var(--muted);
  font-family: "Microsoft YaHei", sans-serif;
}
.header-bar {
  border-bottom: 1px solid var(--line);
  padding-bottom: 0.35em;
  margin-bottom: 1.2em;
}
@media print {
  body { font-size: 10.5pt; }
  .page { max-width: none; padding: 12mm 14mm; }
  a { color: inherit; text-decoration: none; }
  .toc { page-break-after: always; }
  h2 { page-break-before: auto; }
  .no-print { display: none !important; }
  @page {
    size: A4;
    margin: 16mm 14mm 18mm;
  }
}
"""


def _median(vals: list[float]) -> float:
    s = sorted(vals)
    n = len(s)
    if n == 0:
        raise RuntimeError("empty median")
    mid = n // 2
    return s[mid] if n % 2 else 0.5 * (s[mid - 1] + s[mid])


def load_batch1_summary() -> dict:
    if not BATCH1_CSV.exists():
        raise FileNotFoundError(BATCH1_CSV)
    rows = []
    with BATCH1_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append(
                {
                    "basin_id": row["basin_id"],
                    "frac_snow": float(row["frac_snow"]),
                    "delta_NSE": float(row["delta_NSE"]),
                    "NSE_snow": float(row["NSE_xaj_snow"]),
                    "NSE_mz": float(row["NSE_xaj_mz"]),
                }
            )
    if len(rows) != 14:
        raise RuntimeError(f"expected 14 batch1 rows, got {len(rows)}")

    def subset(pred):
        return [r for r in rows if pred(r)]

    snow_ge = subset(lambda r: r["frac_snow"] >= 0.1)
    snow_lt = subset(lambda r: r["frac_snow"] < 0.1)
    s2 = subset(lambda r: r["frac_snow"] > 0.3)
    summary = {
        "n": len(rows),
        "all_med_d": _median([r["delta_NSE"] for r in rows]),
        "snow_ge_n": len(snow_ge),
        "snow_ge_med_d": _median([r["delta_NSE"] for r in snow_ge]),
        "snow_ge_med_sn": _median([r["NSE_snow"] for r in snow_ge]),
        "snow_ge_med_mz": _median([r["NSE_mz"] for r in snow_ge]),
        "snow_lt_n": len(snow_lt),
        "snow_lt_med_d": _median([r["delta_NSE"] for r in snow_lt]),
        "s2_n": len(s2),
        "s2_med_d": _median([r["delta_NSE"] for r in s2]),
    }
    # Cross-check published first-look medians
    assert abs(summary["snow_ge_med_d"] - 0.5461) < 0.001
    assert abs(summary["snow_lt_med_d"] - (-0.0068)) < 0.001
    assert abs(summary["s2_med_d"] - 0.5835) < 0.001
    return summary


def load_rep_budget_010() -> dict:
    """Partial fairness: rep=2000 on 010 only (5000 / 143@2000 not run)."""
    out = {}
    if not REP_BUDGET_CSV.exists():
        return out
    with REP_BUDGET_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("status") != "ok":
                continue
            key = (row["basin_id"].replace("camels_", ""), row["model"], int(row["rep"]))
            out[key] = float(row["NSE"])
    # verified completed cells
    assert abs(out[("01013500", "xaj_mz", 2000)] - (-0.3106)) < 0.001
    assert abs(out[("01013500", "xaj_snow", 2000)] - 0.7318) < 0.001
    return out


def git_short_hash() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(REPO),
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return "unknown"


def load_all() -> dict:
    metrics = {k: read_metrics(p) for k, p in METRIC_PATHS.items()}
    refine = {k: read_metrics(p) for k, p in REFINE_PATHS.items()}
    params = {k: read_params(p) for k, p in PARAM_PATHS.items()}
    batch1 = load_batch1_summary()
    rep_budget = load_rep_budget_010()
    images = {}
    for fig in FIGURES:
        p = FIG / fig["file"]
        if not p.exists():
            raise FileNotFoundError(p)
        images[fig["id"]] = img_data_uri(p)
    # sanity against known go/no-go values
    assert abs(metrics[("01013500", "mz")]["NSE"] - (-0.2321)) < 0.001
    assert abs(metrics[("01013500", "snow")]["NSE"] - 0.7318) < 0.001
    assert abs(metrics[("14306500", "mz")]["NSE"] - 0.7106) < 0.001
    assert abs(metrics[("14306500", "snow")]["NSE"] - 0.7043) < 0.001
    assert abs(refine[("01013500", "snow")]["NSE"] - 0.8779) < 0.001
    assert abs(refine[("01013500", "mz")]["NSE"] - 0.1393) < 0.001
    return {
        "metrics": metrics,
        "refine": refine,
        "params": params,
        "batch1": batch1,
        "rep_budget": rep_budget,
        "images": images,
        "git": git_short_hash(),
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def fmt(x: float, n: int = 3) -> str:
    return f"{x:.{n}f}"


def delta(a: float, b: float, n: int = 3) -> str:
    d = a - b
    sign = "+" if d >= 0 else ""
    return f"{sign}{d:.{n}f}"


def figure_block(doc: str, data: dict, fig: dict, lang: str) -> str:
    mid = fig["id"]
    title = fig["ms_title"] if lang == "en" else fig["rep_title"]
    src = fig["source"]
    num = mid.replace("fig", "")
    label = f"Figure {num}" if lang == "en" else f"图 {num}"
    img = data["images"][mid]
    return f"""
<figure id="{mid}">
  <img src="{img}" alt="{esc(title)}" />
  <figcaption><strong>{label}.</strong> {esc(title)}.
  <span class="src">Data source: {esc(src)}.</span></figcaption>
</figure>
"""


def metrics_table_html(data: dict, lang: str) -> str:
    m = data["metrics"]
    rows = [
        ("01013500", "XAJ-MZ", m[("01013500", "mz")]),
        ("01013500", "XAJ-Snow", m[("01013500", "snow")]),
        ("14306500", "XAJ-MZ", m[("14306500", "mz")]),
        ("14306500", "XAJ-Snow", m[("14306500", "snow")]),
    ]
    if lang == "en":
        head = "<tr><th>Basin</th><th>Model</th><th>NSE</th><th>KGE</th><th>RMSE</th><th>Bias</th><th>Corr</th></tr>"
    else:
        head = "<tr><th>流域</th><th>模型</th><th>NSE</th><th>KGE</th><th>RMSE</th><th>Bias</th><th>Corr</th></tr>"
    body = []
    for basin, model, d in rows:
        body.append(
            "<tr>"
            f"<td>{basin}</td><td>{model}</td>"
            f"<td class='num'>{fmt(d['NSE'],4)}</td>"
            f"<td class='num'>{fmt(d['KGE'],4)}</td>"
            f"<td class='num'>{fmt(d['RMSE'],4)}</td>"
            f"<td class='num'>{fmt(d['Bias'],4)}</td>"
            f"<td class='num'>{fmt(d['Corr'],4)}</td>"
            "</tr>"
        )
    note = (
        "Source files: results/xaj_snow_go_nogo/.../evaluation_test/basins_metrics.csv; "
        "protocol SCE-UA+KGE, rep=800; train 1985-10-01–1995-09-30; "
        "test 2005-10-01–2014-09-30; warmup=365."
        if lang == "en"
        else "数据来源：results/xaj_snow_go_nogo/.../evaluation_test/basins_metrics.csv；"
        "协议 SCE-UA+KGE，rep=800；训练 1985-10-01–1995-09-30；测试 2005-10-01–2014-09-30；warmup=365。"
    )
    return f"<table>{head}{''.join(body)}</table><p class='src'>{esc(note)}</p>"


def refs_html() -> str:
    items = [
        ("Bohl et al., 2026", "https://doi.org/10.5194/hess-30-4667-2026",
         "Bohl, J. P., Wood, R. R., Frank, C., Astagneau, P. C., Peters, J., and Brunner, M. I.: Hybrid models generalize better to warmer climate conditions than process-based and purely data-driven models. HESS, 30, 4667–4698, https://doi.org/10.5194/hess-30-4667-2026, 2026."),
        ("Clerc-Schwarzenbach et al., 2024", "https://doi.org/10.5194/hess-28-4219-2024",
         "Clerc-Schwarzenbach, F., et al.: Technical note: How many times can you afford to change hydrologic forcing? HESS, 28, 4219–4235, https://doi.org/10.5194/hess-28-4219-2024, 2024."),
        ("Chen et al., 2025", "https://doi.org/10.14042/j.cnki.32.1309.2025.02.003",
         "Chen, Z., Zhao, T., et al.: Incorporating snow accumulation and melting into the Xin’anjiang model using differentiable parameter learning (dMXAJ / CemaNeige; 531 CAMELS catchments). Advances in Water Science, https://doi.org/10.14042/j.cnki.32.1309.2025.02.003, 2025."),
        ("Dong et al., 2024", "https://doi.org/10.14042/j.cnki.32.1309.2024.04.002",
         "Dong, N., Wang, H., Yang, M., Zhang, J., and Xu, S.: An improved Xin’anjiang model with snow melting and soil freeze–thaw processes (Upper Yalongjiang). Advances in Water Science, https://doi.org/10.14042/j.cnki.32.1309.2024.04.002, 2024."),
        ("Husic et al., 2025", "https://doi.org/10.5194/hess-29-4457-2025",
         "Husic, A., Hammond, J., Price, A. N., and Roundy, J. K.: Interrogating process deficiencies in large-scale hydrologic models with interpretable machine learning. HESS, 29, 4457–4472, https://doi.org/10.5194/hess-29-4457-2025, 2025."),
        ("Ju et al., 2024", "https://doi.org/10.1016/j.ejrh.2023.101638",
         "Ju, J., et al.: Application of distributed Xin’anjiang model of melting ice and snow in Bahe River basin (DD-XAJ). Journal of Hydrology: Regional Studies, 42, 101638, https://doi.org/10.1016/j.ejrh.2023.101638, 2024."),
        ("Ke et al., 2024", "https://doi.org/10.1007/s11269-024-03909-6",
         "Ke, H., et al.: Xinanjiang-based interval forecasting model for daily streamflow considering climate change impacts (with snowmelt module). Water Resources Management, https://doi.org/10.1007/s11269-024-03909-6, 2024."),
        ("Knoben et al., 2019", "https://doi.org/10.5194/hess-23-4323-2019",
         "Knoben, W. J. M., Freer, J. E., and Woods, R. A.: Technical note: Inherent benchmark or not? Comparing Nash–Sutcliffe and Kling–Gupta efficiency scores. HESS, 23, 4323–4331, https://doi.org/10.5194/hess-23-4323-2019, 2019."),
        ("Knoben et al., 2020", "https://doi.org/10.1029/2019WR025975",
         "Knoben, W. J. M., et al.: A quantitative assessment of 36 conceptual rainfall–runoff models across 559 catchments. WRR, https://doi.org/10.1029/2019WR025975, 2020."),
        ("Kratzert et al., 2023", "https://doi.org/10.1038/s41597-023-01975-w",
         "Kratzert, F., et al.: Caravan — A global community dataset for large-sample hydrology. Scientific Data, https://doi.org/10.1038/s41597-023-01975-w, 2023."),
        ("Liu et al., 2025", "https://doi.org/10.1029/2024WR038873",
         "Liu, W., Liu, P., Zhang, L., Zhang, X., Xu, H., Lei, X., et al.: Development of a conceptual hydrological model based on supply-demand relationship and its applications. Water Resources Research, 61(9), e2024WR038873, https://doi.org/10.1029/2024WR038873, 2025."),
        ("Muñoz-Castro et al., 2026", "https://doi.org/10.5194/hess-30-825-2026",
         "Muñoz-Castro, E., Anderson, B. J., Astagneau, P. C., Swain, D. L., Mendoza, P. A., and Brunner, M. I.: How well do hydrological models simulate streamflow extremes and drought-to-flood transitions? HESS, 30, 825–848, https://doi.org/10.5194/hess-30-825-2026, 2026."),
        ("Ouyang et al., 2021", "https://doi.org/10.1016/j.jhydrol.2021.126455",
         "Ouyang, W., et al.: Continental-scale streamflow modeling with LSTM under reservoir influences. Journal of Hydrology, https://doi.org/10.1016/j.jhydrol.2021.126455, 2021."),
        ("Ouyang et al., 2025", "https://doi.org/10.1016/j.jhydrol.2024.132471",
         "Ouyang, W., Ye, L., Chai, Y., Ma, H., Chu, J., Peng, Y., and Zhang, C.: A differentiable, physics-based hydrological model and its evaluation for data-limited basins (dXAJ / dXAJnn). Journal of Hydrology, 649, 132471, https://doi.org/10.1016/j.jhydrol.2024.132471, 2025."),
        ("Premier et al., 2026", "https://doi.org/10.5194/hess-30-1189-2026",
         "Premier, V., et al.: Isolating snowmelt-coefficient effects by fixing remaining parameters. HESS, https://doi.org/10.5194/hess-30-1189-2026, 2026."),
        ("Ruelland, 2023", "https://doi.org/10.1016/j.jhydrol.2023.129867",
         "Ruelland, D.: SIAR and parsimonious snow accounting under limited degrees of freedom. Journal of Hydrology, https://doi.org/10.1016/j.jhydrol.2023.129867, 2023."),
        ("Ruelland, 2024", "https://doi.org/10.1016/j.jhydrol.2024.130820",
         "Ruelland, D.: Snow data improve consistency and robustness of semi-distributed models. Journal of Hydrology, https://doi.org/10.1016/j.jhydrol.2024.130820, 2024."),
        ("Santos et al., 2025", "https://doi.org/10.5194/hess-29-683-2025",
         "Santos, L., Andréassian, V., Sonnenborg, T. O., Lindström, G., de Lavenne, A., Perrin, C., Collet, L., and Thirel, G.: Lack of robustness of hydrological models: a large-sample diagnosis and an attempt to identify hydrological and climatic drivers. HESS, 29, 683–700, https://doi.org/10.5194/hess-29-683-2025, 2025."),
        ("Tan et al., 2023", "https://doi.org/10.3390/w15193401",
         "Tan, Q., et al.: Coupling snowmelt with XAJ and SCE-UA calibration in northwestern basins. Water, 15, 3401, https://doi.org/10.3390/w15193401, 2023."),
        ("Tong et al., 2022", "https://doi.org/10.5194/hess-26-1779-2022",
         "Tong, R., et al.: Multi-objective calibration with satellite snow cover and soil moisture. HESS, https://doi.org/10.5194/hess-26-1779-2022, 2022."),
        ("Valéry et al., 2014a", "https://doi.org/10.1016/j.jhydrol.2014.04.059",
         "Valéry, A., Andréassian, V., and Perrin, C.: As simple as possible but not simpler (Part 1). Journal of Hydrology, https://doi.org/10.1016/j.jhydrol.2014.04.059, 2014."),
        ("Valéry et al., 2014b", "https://doi.org/10.1016/j.jhydrol.2014.04.058",
         "Valéry, A., Andréassian, V., and Perrin, C.: As simple as possible but not simpler (Part 2): CemaNeige. Journal of Hydrology, https://doi.org/10.1016/j.jhydrol.2014.04.058, 2014."),
        ("Wang et al., 2026", "https://doi.org/10.1029/2025WR040264",
         "Wang, Z., Tarasova, L., and Merz, R.: Event-type-based multi-dimensional diagnostics of process limitations in hydrological models. Water Resources Research, 62(2), e2025WR040264, https://doi.org/10.1029/2025WR040264, 2026."),
        ("Wu et al., 2025", "https://doi.org/10.5194/hess-29-3703-2025",
         "Wu, N., Zhang, K., Naghibi, A., Hashemi, H., Ning, Z., Zhang, Q., Yi, X., Wang, H., Liu, W., Gao, W., and Jarsjö, J.: Predicting snow cover and frozen ground impacts on large basin runoff: developing appropriate model complexity (GXAJ / GXAJ-S / GXAJ-S-SF). HESS, 29, 3703–3725, https://doi.org/10.5194/hess-29-3703-2025, 2025."),
        ("Yeste et al., 2024", "https://doi.org/10.5194/hess-28-5331-2024",
         "Yeste, P., García-Valdecasas Ojeda, M., Gámiz-Fortis, S. R., Castro-Díez, Y., Bronstert, A., and Esteban-Parra, M. J.: A large-sample modelling approach towards integrating streamflow and evaporation data for the Spanish catchments. HESS, 28, 5331–5352, https://doi.org/10.5194/hess-28-5331-2024, 2024."),
    ]
    lis = "".join(
        f'<li id="ref-{i+1}"><a class="ref" href="{url}">{esc(text)}</a></li>'
        for i, (_, url, text) in enumerate(items)
    )
    return f"<ol>{lis}</ol>"


def build_manuscript_html(data: dict) -> str:
    m = data["metrics"]
    rf = data["refine"]
    b1 = data["batch1"]
    p010 = data["params"]["01013500"]
    nse_mz = m[("01013500", "mz")]["NSE"]
    nse_sn = m[("01013500", "snow")]["NSE"]
    kge_mz = m[("01013500", "mz")]["KGE"]
    kge_sn = m[("01013500", "snow")]["KGE"]
    nse_c_mz = m[("14306500", "mz")]["NSE"]
    nse_c_sn = m[("14306500", "snow")]["NSE"]
    kge_c_mz = m[("14306500", "mz")]["KGE"]
    kge_c_sn = m[("14306500", "snow")]["KGE"]
    nse_rf_mz = rf[("01013500", "mz")]["NSE"]
    nse_rf_sn = rf[("01013500", "snow")]["NSE"]
    kge_rf_mz = rf[("01013500", "mz")]["KGE"]
    kge_rf_sn = rf[("01013500", "snow")]["KGE"]
    nse_mz_2000 = data["rep_budget"].get(("01013500", "xaj_mz", 2000))
    nse_sn_2000 = data["rep_budget"].get(("01013500", "xaj_snow", 2000))

    body = f"""
<div class="header-bar">Hydromodel 0.3.2 · XAJ-Snow manuscript draft · generated {esc(data['generated'])} · for HESS-oriented polishing</div>
<article class="page">
<section class="cover">
  <div class="eyebrow">Manuscript draft · Hydrology and Earth System Sciences (target)</div>
  <h1>Diagnosing snow-related structural limitations of the Xinanjiang model: a parsimonious snow extension, an engineering pilot, and a first-look multi-basin extension</h1>
  <p class="subtitle">Working title (avoid “global / first” until the frozen stratified sample is fully calibrated). Status: <span class="badge">pilot complete</span><span class="badge">batch1 first-look</span><span class="badge">large-sample pending</span></p>
  <p class="meta">Authors: <em>to be completed</em> · Affiliations: <em>to be completed</em> · Correspondence: <em>to be completed</em></p>
  <p class="meta">Software context: hydromodel v0.3.2; model names XAJ-MZ and XAJ-Snow; Caravan CAMELS subsets.</p>
</section>

<nav class="toc" id="toc">
  <strong>Contents</strong>
  <ol>
    <li><a href="#abstract">Abstract</a></li>
    <li><a href="#sec1">1 Introduction</a></li>
    <li><a href="#sec2">2 Data and methods</a></li>
    <li><a href="#sec3">3 Results</a></li>
    <li><a href="#sec4">4 Discussion</a></li>
    <li><a href="#sec5">5 Conclusions</a></li>
    <li><a href="#avail">Code and data availability</a></li>
    <li><a href="#contrib">Author contributions / Competing interests / Acknowledgements</a></li>
    <li><a href="#refs">References</a></li>
    <li><a href="#si">Supplementary note on pilot figures and objective sensitivity</a></li>
  </ol>
</nav>

<section id="abstract">
<h2>Abstract</h2>
<p>
Conceptual rainfall–runoff models remain central to large-sample hydrology, yet structural adequacy can collapse in regimes that the model never represents.
The Xin’anjiang model (XAJ) in its Muskingum–Zhao routing form (XAJ-MZ) treats precipitation as liquid input and therefore cannot store snowfall or release meltwater.
Regional studies have already coupled snow and related cold-region processes to XAJ (Tan et al., 2023; Ju et al., 2024; Dong et al., 2024; Wu et al., 2025), and a large-sample CAMELS study has already coupled CemaNeige to XAJ under differentiable parameter learning across 531 catchments (Chen et al., 2025).
What remains under-documented in the HESS-facing literature is a diagnosis-first protocol that (i) maps <em>where</em> unmodified XAJ-MZ fails along snow/hydroclimate gradients, (ii) tests a deliberately minimal non-ML snow correction under matched nominal calibration budgets, (iii) requires neutrality on snow-free controls, and (iv) designs—rather than yet establishes—an applicability-domain estimate with fairness checks, instead of proposing another high-performing XAJ–snow family.
</p>
<p>
Here we implement XAJ-Snow: a single-band, CemaNeige-style degree-day layer with two free parameters—degree-day factor <em>K</em><sub>f</sub> (mm °C<sup>−1</sup> d<sup>−1</sup>) and cold-content coefficient CTG [-]—placed upstream of an otherwise unchanged XAJ-MZ core.
We report an <strong>engineering go/no-go pilot</strong> under identical Shuffled Complex Evolution–University of Arizona (SCE-UA) calibration against the Kling–Gupta efficiency (KGE) with matched medium budget (<code>rep</code>=800, <code>ngs</code>=15):
out-of-sample Nash–Sutcliffe efficiency (NSE) on snow-affected basin 01013500 (fraction of precipitation falling as snow ≈ 0.37) rises from {fmt(nse_mz,3)} (XAJ-MZ) to {fmt(nse_sn,3)} (XAJ-Snow), while KGE rises from {fmt(kge_mz,3)} to {fmt(kge_sn,3)};
on low-snow negative-control basin 14306500, NSE changes only from {fmt(nse_c_mz,3)} to {fmt(nse_c_sn,3)} (Δ ≈ {delta(nse_c_sn, nse_c_mz)}).
Calibrated snow parameters on 01013500 remain interior to their search ranges (<em>K</em><sub>f</sub> ≈ {fmt(p010['Kf'],2)}, CTG ≈ {fmt(p010['CTG'],3)}), although interiority alone does not identify a physical melt coefficient without SWE constraints.
A first-look paired batch of {b1['n']} CAMELS basins at lighter budget (<code>rep</code>=200) yields median ΔNSE ≈ {fmt(b1['snow_ge_med_d'],2)} for snow-affected basins (frac_snow ≥ 0.1, n={b1['snow_ge_n']}) and ≈ {fmt(b1['snow_lt_med_d'],3)} for low-snow basins (n={b1['snow_lt_n']}).
</p>
<div class="todo"><strong>Pending (do not treat as completed Results):</strong> full calibration of the frozen stratified sample (currently 80 basins frozen; longer-term target ~500); snow-water-equivalent (SWE) auxiliary consistency; complete optimizer-budget / parameter-freedom factorial (including <code>rep</code>=5000 and multi-seed; only a partial <code>rep</code>=2000 check on 01013500 is available); cross-region applicability regression. Until those experiments finish, do not extrapolate to a global claim.</div>
</section>

<section id="sec1">
<h2>1 Introduction</h2>
<p>
Large-sample evaluations have shown that “average skill” hides regime-dependent structural failure
(Knoben et al., 2020; Santos et al., 2025).
Snow-affected catchments are a recurring stress test: models that cannot partition precipitation into rain and snow, or cannot delay melt, can misrepresent seasonal storage and runoff timing even when annual water balance looks plausible.
</p>
<p>
The Xin’anjiang model is widely used in humid and semi-humid settings.
Variants that add snow or related cold-region processes already exist, including coupled snowmelt–XAJ applications (Tan et al., 2023; Ke et al., 2024), distributed degree-day XAJ with ice/snow melt (Ju et al., 2024), conceptual XAJ with snowmelt plus soil freeze–thaw (Dong et al., 2024), graded complexity GXAJ-S / GXAJ-S-SF with SNOW17 (Wu et al., 2025), and a CAMELS-scale (531 basins) differentiable XAJ–CemaNeige system (dMXAJ) with local and regional parameter learning (Chen et al., 2025).
Differentiable XAJ formulations further explore optimizer and parameter-sharing design (Ouyang et al., 2025).
More broadly, coupling established snow routines to parsimonious conceptual models is now routine methodology in multi-catchment HESS-facing work (Muñoz-Castro et al., 2026), event-type diagnostics already isolate snow-related process limitations at large scale (Wang et al., 2026), and large-sample studies already relate conceptual-model adequacy to the fraction of precipitation falling as snow (Liu et al., 2025; Bohl et al., 2026).
<strong>This manuscript does not claim the first XAJ snow extension, nor the first XAJ–CemaNeige coupling, nor the first large-sample XAJ–snow evaluation.</strong>
</p>
<p>
These studies demonstrate the value of representing snow processes and, increasingly, of controlling model complexity, but they leave a narrower model-evaluation question unresolved: <em>when</em> does adding a minimal snow process to an otherwise unchanged XAJ formulation provide evidence of correcting a process deficiency rather than simply increasing model flexibility?
Addressing this question requires paired evaluation across a snow gradient, comparable calibration effort, and a specificity check in catchments where snow processes should exert little influence.
Rather than proposing a new snow formulation, this study therefore examines when an established, parsimonious snow representation is warranted within the XAJ-MZ framework.
We formulate a diagnosis-first protocol in which the baseline and snow-enabled models retain the same rainfall–runoff and routing backbone, are calibrated under controlled computational budgets, and are evaluated jointly against snow-influenced basins and snow-poor negative controls.
The planned large-sample analysis is designed to relate the paired model response to catchment snow exposure, test whether apparent discharge gains are accompanied by consistent snow behavior, and assess their robustness to calibration-fairness choices
(Valéry et al., 2014a,b; Premier et al., 2026; Husic et al., 2025; Santos et al., 2025).
The current 14-basin experiment is treated only as first-look evidence motivating the completed multi-basin assessment, rather than as evidence for a general applicability threshold.
Relative to the studies above—whether they demonstrate XAJ–snow skill (Tan et al., 2023; Chen et al., 2025), deepen cold-region process complexity (Ju et al., 2024; Dong et al., 2024; Wu et al., 2025), or diagnose model limitations across large samples (Wang et al., 2026; Liu et al., 2025; Bohl et al., 2026)—the distinctive element here is a controlled <em>intervention</em> experiment: the same backbone with and without one specific snow process, evaluated with snow-poor basins as explicit negative controls and matched calibration effort.
</p>
<p>
Research questions guiding the full study:
</p>
<ol>
  <li>RQ1 — Where does XAJ-MZ fail out of sample as a function of snow influence and related attributes?</li>
  <li>RQ2 — Does a two-parameter, single-band CemaNeige-style layer selectively improve snow-affected basins while remaining neutral on negative controls, where neutrality is defined prospectively (Section 2.5) rather than chosen after seeing the results?</li>
  <li>RQ3 — Are the paired gains robust to optimizer budget and to the two extra parameters (multi-seed runs and fixed-snow-parameter ablations)?</li>
  <li>RQ4 — Can an applicability domain be estimated as a continuous relationship with uncertainty from catchment attributes?</li>
</ol>
<p>
The present draft reports the engineering pilot that unlocked the go decision for stratified sampling, plus a cautious first-look multi-basin screen at reduced calibration budget.
Full answers to RQ1–RQ4 on the frozen stratified sample remain incomplete.
</p>
</section>

<section id="sec2">
<h2>2 Data and methods</h2>
<h3>2.1 Caravan data and basin sampling</h3>
<p>
Forcing and discharge come from the Caravan community dataset (Kratzert et al., 2023).
Caravan harmonizes multi-source CAMELS-family basins but its meteorological forcing is not identical to the original CAMELS products; this difference can change conceptual-model skill and must be stated explicitly (Clerc-Schwarzenbach et al., 2024).
Potential evapotranspiration (PET) uses FAO Penman–Monteith attributes supplied with Caravan.
</p>
<p>
The snow-exposure covariate <code>frac_snow</code> is the basin-level fraction of precipitation falling as snow, taken from the Caravan attribute table (attributes_other_*) for each region; it is a catchment attribute, not a model output.
All basins are drawn from a reproducible stratified design over seven Caravan regions (snow bin × aridity bin × regulation bin, 3×3×2 strata) frozen at a fixed seed; the frozen first batch contains 80 basins, and the paper-scale target is ~500.
Two pilot basins had fixed roles assigned a priori, and a separate 14-basin CAMELS (US) screening subset (batch1) consisting of the two pilot basins plus 12 CAMELS basins from the frozen stratified sample was used for first-look screening; the full basin list and attributes are published in the repository diagnostics.
The snow bins S0 (frac_snow &lt; 0.1), S1 (0.1–0.3), and S2 (&gt; 0.3) are defined here in Methods and used consistently in Results.
</p>
<table>
<tr><th>Basin</th><th>Role</th><th>frac_snow</th><th>Area (km²)</th><th>Aridity (FAO-PM)</th><th>Human footprint</th></tr>
<tr><td>camels_01013500</td><td>Snow-affected diagnosis target</td><td class="num">≈0.37</td><td class="num">2298</td><td class="num">0.49</td><td class="num">30.6</td></tr>
<tr><td>camels_14306500</td><td>Low-snow negative control</td><td class="num">≈0.0</td><td class="num">859</td><td class="num">0.49</td><td class="num">34.3</td></tr>
</table>
<p class="src">Catchment attributes from the Caravan attribute table used in the public diagnostic note for this basin pair. Attributes are listed for context; their interpretive use is deferred to the Discussion.</p>
<p>
Periods (identical for both models and both basins): training 1985-10-01–1995-09-30; testing 2005-10-01–2014-09-30; warmup length 365 days.
Daily variables: precipitation <em>P</em>, PET, discharge <em>Q</em>, and for XAJ-Snow also 2 m air temperature <em>T</em>.
</p>

<h3>2.2 XAJ-MZ baseline</h3>
<p>
XAJ-MZ denotes the hydromodel implementation of Xin’anjiang with Muskingum–Zhao routing and fifteen calibrated parameters (no snow store).
All precipitation enters the production module as rainfall-equivalent forcing.
XAJ-Snow shares this backbone exactly and adds only the two snow parameters below, for seventeen total; the same fifteen base parameters are calibrated for both models under identical search ranges (Table 2).
</p>
<p><strong>Table 2.</strong> Calibrated parameter search ranges (identical for XAJ-MZ and XAJ-Snow; XAJ-Snow adds Kf and CTG).</p>
<table>
<tr><th>Parameter</th><th>Role</th><th class="num">Range</th></tr>
<tr><td>K</td><td>PET ratio to reference crop evaporation</td><td class="num">[0.1, 1.0]</td></tr>
<tr><td>B</td><td>Exponent of tension water capacity curve</td><td class="num">[0.1, 0.4]</td></tr>
<tr><td>IM</td><td>Impervious area fraction</td><td class="num">[0.01, 0.1]</td></tr>
<tr><td>UM, LM, DM</td><td>Tension water capacity: upper / lower / deep (mm)</td><td class="num">[0, 20] / [60, 90] / [60, 120]</td></tr>
<tr><td>C</td><td>Deep evapotranspiration coefficient</td><td class="num">[0, 0.2]</td></tr>
<tr><td>SM, EX</td><td>Mean free-water storage (mm); curve exponent</td><td class="num">[1, 100] / [1.0, 1.5]</td></tr>
<tr><td>KI, KG</td><td>Interflow / groundwater outflow coefficients</td><td class="num">[0, 0.7] each</td></tr>
<tr><td>A, THETA</td><td>mizuRoute channel parameters</td><td class="num">[0, 2.9] / [0, 6.5]</td></tr>
<tr><td>CI, CG</td><td>Recession constants: lower interflow / groundwater</td><td class="num">[0, 0.9] / [0.98, 0.998]</td></tr>
<tr><td>Kf</td><td>Degree-day melt factor (mm °C<sup>−1</sup> d<sup>−1</sup>) — XAJ-Snow only</td><td class="num">[0, 10]</td></tr>
<tr><td>CTG</td><td>Snow thermal-state weight [-] — XAJ-Snow only</td><td class="num">[0, 1]</td></tr>
</table>

<h3>2.3 XAJ-Snow: CemaNeige-style single-band layer</h3>
<p>
XAJ-Snow prepends a lumped (one elevation band) snow-accounting module inspired by CemaNeige (Valéry et al., 2014b) and related airGR documentation, then calls the same XAJ-MZ core on effective liquid input (rain + melt).
Fixed thresholds in this implementation: rain/snow threshold <em>T</em><sub>s</sub> = 0 °C and linear mix half-width <em>T</em><sub>r</sub> = 1 °C.
Free snow parameters:
</p>
<ul>
  <li><em>K</em><sub>f</sub> — degree-day melt factor (mm °C<sup>−1</sup> d<sup>−1</sup>), search range [0, 10]; larger values melt faster for a given positive temperature.</li>
  <li>CTG — dimensionless cold-content / thermal-state inertia in [0, 1]; larger CTG increases memory of prior cold conditions and delays melt onset.</li>
</ul>
<p>
Mass symbols used in the module: precipitation <em>P</em>, temperature <em>T</em>, snow water equivalent SWE, thermal state <em>G</em>, melt potential MeltPot, snow-cover factor Gratio, and melt <em>M</em>.
A schematic daily update is:
</p>
<p class="eq">rain, snow ← partition(<em>P</em>, <em>T</em>; <em>T</em><sub>s</sub>, <em>T</em><sub>r</sub>)</p>
<p class="eq">SWE ← SWE + snow; <em>G</em> ← min(0, CTG·<em>G</em> + (1−CTG)·<em>T</em>)</p>
<p class="eq">MeltPot ← min(SWE, max(0, <em>K</em><sub>f</sub>·<em>T</em>)) only if the pack is isothermal (<em>G</em> ≈ 0); else MeltPot = 0</p>
<p class="eq">Gratio ← min(1, SWE / G<sub>threshold</sub>); <em>M</em> ← min(SWE, (0.9·Gratio + 0.1)·MeltPot)</p>
<p>
Unless an external array is supplied, <em>G</em><sub>threshold</sub> is estimated inside each snow-module call as 0.9 × mean annual snowfall from the snowfall series of <em>that same call</em> (CemaNeige-style default; tiny floor for snow-free basins).
Because train and test periods are loaded separately, the pilot therefore recomputes <em>G</em><sub>threshold</sub> from each period’s forcing rather than freezing a training-derived value into evaluation.
This is not a fitted degree of freedom, but it does make the test simulation depend on a climatological statistic of the complete test-period forcing; we disclose it explicitly here, and a training-derived/frozen <em>G</em><sub>threshold</sub> protocol is listed as a pending sensitivity check rather than yet completed.
Snow states are initialized at zero SWE and <em>G</em> = 0 °C and run through the same 365-day warm-up as the XAJ soil states; states are not carried across the train/test boundary.
</p>
<p>
We describe the layer as <em>CemaNeige-style / single-band</em>, not as a strict airGR reproduction (airGR defaults use multiple elevation bands and different temperature bands).
<em>K</em><sub>f</sub> ≈ 3.5 mm °C<sup>−1</sup> d<sup>−1</sup> on the snow pilot is interior to the search range and within commonly reported degree-day magnitudes (~2–6), but without SWE constraints it remains an effective parameter rather than a physically identified melt coefficient.
</p>

<h3>2.4 Calibration and metrics</h3>
<p>
Optimizer: SCE-UA (Shuffled Complex Evolution–University of Arizona) maximizing KGE on the training window, implemented through SpotPy.
In this implementation, <code>rep</code> caps the total number of model evaluations (the SCE-UA “repetitions” budget), and <code>ngs</code> is the number of complexes the population is split into; both models and both basins use the same random seed (1234), so repeated runs of the same basin–model–budget cell are deterministic.
Convergence criteria (kstop = 40, peps = pcento = 0.1) are also identical across all runs.
The pilot medium protocol uses <code>rep</code>=800 and <code>ngs</code>=15 for <em>both</em> models and both basins (matched nominal budgets by configuration).
The first-look multi-basin batch uses the same objective, periods, and seed but a lighter budget (<code>rep</code>=200) for screening.
A partial higher-budget sensitivity on snow-affected 01013500 at <code>rep</code>=2000 was also conducted; its numerical outcome is reported in Section 3.4, and <code>rep</code>=5000 and the control basin at <code>rep</code>=2000 remain incomplete.
<strong>Important:</strong> matched budgets support controlled comparison; they do <em>not</em> yet constitute a full fairness proof versus multi-seed searches or fixed-snow-parameter ablations.
Those checks must precede any claim that gains are independent of optimization budget or the two extra degrees of freedom (17 vs 15 parameters).
Reported skill uses the independent test window.
NSE and KGE are defined in the conventional forms:
</p>
<p class="eq">NSE = 1 − Σ(<em>Q</em><sub>sim</sub>−<em>Q</em><sub>obs</sub>)<sup>2</sup> / Σ(<em>Q</em><sub>obs</sub>−Q̅<sub>obs</sub>)<sup>2</sup></p>
<p class="eq">KGE = 1 − √[ (r−1)<sup>2</sup> + (α−1)<sup>2</sup> + (β−1)<sup>2</sup> ]</p>
<p>
where <em>r</em> is correlation, α a variability ratio, and β a bias ratio (hydromodel implementation).
NSE = 1 is perfect; NSE = 0 matches the mean-flow benchmark and negative NSE is worse than the mean.
KGE = 1 is optimal and lower values indicate increasing departure in its correlation, variability, and bias components.
Unlike NSE, KGE has no inherent zero benchmark: the mean-flow predictor corresponds to KGE = 1 − √2 ≈ −0.41, so KGE values must not be read with the NSE zero-threshold convention (Knoben et al., 2019).
</p>

<h3>2.5 Negative-control design and the neutrality criterion</h3>
<p>
Basin 14306500 (frac_snow ≈ 0) is the negative control: a useful snow layer should not create large spurious skill gains when snow storage is irrelevant.
To keep the test prospective rather than post hoc, we define neutrality operationally before examining multi-basin results: XAJ-Snow is considered neutral on a negative-control basin when its test-period ΔNSE lies within ±0.05 and the absolute ΔKGE within 0.05; larger movements in either direction trigger inspection rather than dismissal.
The completed pilot control satisfies this criterion; whether the wider zero-snow cohort of the frozen sample does is part of the planned analysis.
</p>

<h3>2.6 Planned full-sample analyses (not yet completed)</h3>
<p>
The following analyses answer RQ1–RQ4 but are incomplete at the time of writing and are listed here as the study protocol rather than as results: full medium-budget calibration of the frozen stratified sample (80 basins frozen; expansion toward ~500 planned); snow-water-equivalent (SWE) auxiliary consistency diagnostics against ERA5-Land (consistency only, not independent ground validation); the complete optimizer-budget and parameter-freedom factorial (<code>rep</code>=5000, multi-seed runs, control basin at higher budget, and fixed-snow-parameter ablations); and attribute-based applicability-domain models with region-grouped cross-validation.
</p>
</section>

<section id="sec3">
<h2>3 Results</h2>
<h3>3.1 Paired pilot performance and negative control</h3>
<p>
Table 1 lists paired test-period metrics read directly from <code>basins_metrics.csv</code>.
</p>
<p><strong>Table 1.</strong> Out-of-sample metrics for the go/no-go pilot (SCE-UA + KGE, rep=800).</p>
{metrics_table_html(data, "en")}
<p>
On 01013500, XAJ-Snow improves NSE by Δ = {delta(nse_sn, nse_mz)} and KGE by Δ = {delta(kge_sn, kge_mz)}.
On 14306500, ΔNSE = {delta(nse_c_sn, nse_c_mz)} and ΔKGE = {delta(kge_c_sn, kge_c_mz)}, i.e. within a few thousandths—inside the prospective neutrality band of Section 2.5.
Denormalized snow parameters on 01013500: <em>K</em><sub>f</sub> = {fmt(p010['Kf'],4)} mm °C<sup>−1</sup> d<sup>−1</sup>, CTG = {fmt(p010['CTG'],6)} (interior of [0,10]×[0,1]); interiority only shows the optimum is not pinned at a bound and is not evidence of physical identification or search stability.
A supplementary local refine of the SCE-UA optimum against NSE on 01013500 (different objective and search stage) is reported in the Supplementary note as an objective/search sensitivity, not as part of the matched comparison.
</p>

<h3>3.2 Pilot hydrograph diagnostics</h3>
<p>
Figures 1–5 document the two-basin pilot. They support an engineering GO decision and method readiness; they are <strong>not</strong> a substitute for stratified population inference.
</p>
"""
    # insert figures with short academic analysis
    analyses_en = {
        "fig1": """
<div class="explain">
<p><strong>Reading Figure 1.</strong> Grouped bars compare NSE (blue family) and KGE (green family) for each basin–model pair.
Tall XAJ-Snow bars on 01013500 versus short/negative XAJ-MZ bars show the selective skill recovery;
near-equal bars on 14306500 show the control remains flat. The figure cannot prove causality beyond the paired protocol, nor generalize beyond two basins.</p>
</div>""",
        "fig2": """
<div class="explain">
<p><strong>Reading Figure 2.</strong> Black: observed discharge; blue: XAJ-MZ; orange: XAJ-Snow over the full test window after warmup.
Spring shading marks March–May. In this basin, XAJ-MZ visibly displaces or attenuates snow-season peaks relative to observations, while XAJ-Snow tracks volume and timing more closely; this is a qualitative hydrograph pattern, since no formal peak-timing metric is included in the completed evidence.
Do not read summer/autumn residuals as snow-process proof; they may reflect soil/routing parameter trade-offs.</p>
</div>""",
        "fig3": """
<div class="explain">
<p><strong>Reading Figure 3.</strong> A 2010–2012 zoom isolates consecutive snowmelt seasons.
Use it to inspect peak timing, multi-peak structure, and whether XAJ-Snow overshoots individual events.
It cannot separate temperature-forcing error from structural melt error.</p>
</div>""",
        "fig4": """
<div class="explain">
<p><strong>Reading Figure 4.</strong> On the negative control, XAJ-MZ and XAJ-Snow hydrographs nearly overlap, matching the near-zero Δ metrics.
This panel guards against “any extra parameters help everywhere” interpretations.</p>
</div>""",
        "fig5": """
<div class="explain">
<p><strong>Reading Figure 5.</strong> Daily observed vs simulated scatter for 01013500; the 1:1 line is the reference.
XAJ-Snow points hug the diagonal more tightly (higher correlation / lower error), while XAJ-MZ shows larger scatter and bias.
Scatter plots compress timing information—pair with Figures 2–3 for hydrograph timing.</p>
</div>""",
        "fig6": """
<div class="explain">
<p><strong>Reading Figure 6.</strong> Each point is one CAMELS basin in the first-look batch (<code>rep</code>=200).
Positive ΔNSE indicates XAJ-Snow outperforming XAJ-MZ on the independent test window.
The pattern is consistent with larger gains at higher snow fractions, but n=14 and the lighter budget forbid population inference.</p>
</div>""",
        "fig7": """
<div class="explain">
<p><strong>Reading Figure 7.</strong> Box/summary view of ΔNSE by snow-fraction bin (defined in Section 2.1) for the same first-look batch.
Both the all-sample and stratified summaries are reported; stratification follows the prespecified snow-exposure hypothesis, not the observed all-sample median.</p>
</div>""",
    }
    for fig in FIGURES:
        if fig["id"] in ("fig6", "fig7"):
            continue  # placed after batch1 section
        body += figure_block("ms", data, fig, "en")
        body += analyses_en[fig["id"]]

    body += f"""
<h3>3.3 First-look multi-basin screening under a reduced calibration budget</h3>
<p>
To assess whether the two-basin pilot warranted completion of the planned stratified experiment, we conducted an exploratory paired screening of {b1['n']} CAMELS (US) basins using the same training and test periods and the same SCE-UA–KGE objective as the pilot, but with a lighter calibration budget (<code>rep</code> = 200 rather than <code>rep</code> = 800).
These runs are therefore treated as screening evidence rather than as budget-equivalent replication or population-level inference.
Within this first-look sample, the median test-period ΔNSE (XAJ-Snow − XAJ-MZ) was {fmt(b1['snow_ge_med_d'],4)} for basins with frac_snow ≥ 0.1 (n = {b1['snow_ge_n']}) and {fmt(b1['snow_lt_med_d'],4)} for basins with frac_snow &lt; 0.1 (n = {b1['snow_lt_n']}); for the S2 subset (frac_snow &gt; 0.3, n = {b1['s2_n']}), the median ΔNSE was {fmt(b1['s2_med_d'],4)}.
The all-sample median ΔNSE was {fmt(b1['all_med_d'],4)}; we report both the overall and snow-stratified summaries because snow stratification follows the prespecified snow-exposure hypothesis of Section 2.1, and because both models fail on a minority of basins in every bin.
These descriptive contrasts motivate completion of the frozen stratified sample and calibration-fairness analyses, but they do not establish an applicability threshold or population-level snow-response relationship.
Figures 6–7 visualize ΔNSE against snow fraction and by bin.
</p>
"""
    for fig in FIGURES:
        if fig["id"] not in ("fig6", "fig7"):
            continue
        body += figure_block("ms", data, fig, "en")
        body += analyses_en[fig["id"]]

    body += f"""
<h3>3.4 Partial optimizer-budget sensitivity (01013500, <code>rep</code>=2000)</h3>
<p>
On snow-affected 01013500, increasing the available SCE-UA budget from <code>rep</code>=800 to <code>rep</code>=2000 does not reverse the pilot contrast: XAJ-MZ test NSE moves from {fmt(nse_mz,4)} to {fmt(nse_mz_2000,4)}, while XAJ-Snow remains at {fmt(nse_sn_2000,4)}.
This single completed higher-budget cell is a bounded sensitivity result: it does not establish budget robustness, because the negative-control basin at <code>rep</code>=2000, any <code>rep</code>=5000 run, and multi-seed replicates remain incomplete (Section 2.6).
</p>
</section>

<section id="sec4">
<h2>4 Discussion</h2>
<p>
The pilot evidence is consistent with, but not diagnostic of, an omitted snow-process limitation on 01013500: a large paired recovery on one snow-affected basin plus a near-neutral response on one low-snow basin is what the snow-deficiency hypothesis predicts, yet the intervention also changes parameter dimensionality and no SWE consistency check is completed.
An alternative explanation based on human disturbance alone is less likely given comparable footprint indices across the pair, but similar footprints do not causally exclude anthropogenic effects (Section 2.1), and they lie outside the performance evidence itself.
The near-zero change on 14306500 reduces—but does not eliminate—concern that seventeen versus fifteen parameters alone buy universal skill; a single negative control cannot replace a stratified zero-snow cohort or a fixed-snow-parameter ablation.
</p>
<p>
The 14-basin first-look screen (Section 3.3) reproduces the directional specificity of the pilot at a lighter budget (<code>rep</code>=200, not the pilot’s <code>rep</code>=800): stratified medians are positive and large for snow-exposed basins and near zero for low-snow basins.
At n = 14 this supports continuing the controlled structural-diagnosis experiment; it does not identify an applicability threshold or a population-level snow-response relationship.
Likewise, the one completed higher-budget cell (Section 3.4) shows the pilot contrast was not reversed on 01013500 at <code>rep</code>=2000, but cannot demonstrate optimizer robustness without the remaining control-basin, <code>rep</code>=5000, and multi-seed cells.
</p>
<p>
Relative to the existing XAJ–snow literature (Tan et al., 2023; Ju et al., 2024; Dong et al., 2024; Wu et al., 2025; Chen et al., 2025), multi-catchment snow-routine comparisons (Muñoz-Castro et al., 2026), and the large-sample diagnostic studies (Wang et al., 2026; Liu et al., 2025; Bohl et al., 2026), the contribution targeted here is methodological: a paired, control-based intervention experiment with matched nominal budgets and a prospectively defined neutrality criterion.
Whether that combination yields information the individual studies do not provide will be decided by the completed stratified sample, not by the current evidence.
Relative to Premier et al. (2026), future work should isolate melt-factor effects more tightly (e.g. freeze non-snow parameters) once the stratified sample exists.
</p>
<p>
Alternative explanations that remain open: Caravan forcing biases (Clerc-Schwarzenbach et al., 2024); PET product choice; single-band temperature representativeness; equifinality among soil parameters absorbing snow errors; and residual anthropogenic regulation not captured by footprint indices.
SWE was not used as a calibration target here; without snow-state constraints, <em>K</em><sub>f</sub> and CTG remain effective parameters (Ruelland, 2023, 2024; Tong et al., 2022).
Interior <em>K</em><sub>f</sub>/CTG values show only that the selected optimum is not pinned to the parameter bounds; establishing search or numerical stability would require repeated seeds and convergence diagnostics, which remain pending.
</p>
</section>

<section id="sec5">
<h2>5 Conclusions</h2>
<p>
Under a paired SCE-UA+KGE protocol, a two-parameter CemaNeige-style layer converts a strongly negative out-of-sample NSE on snow-affected basin 01013500 into a clearly positive score, while leaving a low-snow control essentially unchanged.
A first-look 14-basin CAMELS batch at lighter budget shows the same directional pattern in stratified medians, without authorizing a multi-region applicability map.
This supports an engineering GO for completing the frozen stratified sample.
It does <em>not</em> yet establish a global applicability map, independent SWE validation, or optimizer-versus-complexity attribution.
</p>
<p>
Next steps: finish medium-budget calibration on the frozen sample; add SWE consistency and fairness controls; then rewrite Abstract/Results without pilot-only extrapolation.
</p>
</section>

<section id="avail">
<h2>Code and data availability</h2>
<p>
Research code, curated figures, diagnostics notes, consultation briefings, and publication drafts are publicly available at
<a href="https://github.com/Coucou2016/hydromodel-xaj-snow">https://github.com/Coucou2016/hydromodel-xaj-snow</a>
(branch <code>master</code>; generator snapshot commit <code>{esc(data['git'])}</code>).
Core modules include the snow accounting layer and XAJ-Snow wrapper registered in the hydromodel model dictionary; matched pilot configurations, unit tests, and the publication generator are included.
The paired batch1 metrics table and the sanitized 14-basin sampling/attribute table (basin identity, coordinates, attributes, snow/aridity/regulation strata, and frozen-sample seed) are published under <code>results/diagnostics/</code>.
Caravan / CAMELS forcing and discharge follow Kratzert et al. (2023) licensing; large NetCDF caches and portable hydrodata trees are <strong>not</strong> redistributed in the public snapshot.
Full optimizer dump trees are also excluded; curated metric tables and figures remain.
Zenodo archival DOI: pending (to be minted before journal submission).
</p>
</section>

<section id="contrib">
<h2>Author contributions / Competing interests / Acknowledgements</h2>
<p><strong>Author contributions:</strong> to be completed.</p>
<p><strong>Competing interests:</strong> to be completed (declare none if applicable).</p>
<p><strong>Acknowledgements:</strong> to be completed.</p>
</section>

<section id="refs">
<h2>References</h2>
<p class="src">Only locally verified DOIs from docs/local/literature_review_xaj_snow.md are listed.</p>
{refs_html()}
</section>

<section id="si">
<h2>Supplementary note on pilot figures and objective sensitivity</h2>
<p>
Figures use SciencePlots styling (≥300 dpi PNG siblings in the public snapshot).
Metric provenance is documented in the repository diagnostics tables accompanying the go/no-go, refine, rep-budget, and batch1 CSV files.
This HTML is self-contained (CSS inline; figures as base64).
</p>
<p>
<strong>S1. Objective/search-stage sensitivity (SciPy refine, 01013500 only).</strong>
After the matched SCE-UA+KGE runs, a local SciPy refine against NSE on 01013500 yields test NSE/KGE of {fmt(nse_rf_sn,4)}/{fmt(kge_rf_sn,4)} for XAJ-Snow versus {fmt(nse_rf_mz,4)}/{fmt(kge_rf_mz,4)} for XAJ-MZ.
Because it changes both the optimization objective and the search stage, this contrast is supplementary headroom evidence; it is not a replacement for the matched SCE-UA comparison and not a fairness proof.
</p>
</section>

<div class="footer-note">Generated {esc(data['generated'])} from real CSV-backed metrics and figures. No fabricated metrics. Claims beyond completed evidence remain pending.</div>
</article>
"""
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\"/>\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>\n"
        "<title>XAJ-Snow manuscript draft</title>\n"
        f"<style>{shared_css()}</style>\n"
        "</head>\n<body>\n"
        f"{body}\n"
        "</body>\n</html>\n"
    )


def report_figure_explain(fig_id: str) -> str:
    """Ultra-detailed Chinese explanations for the research report."""
    blocks = {
        "fig1": """
<div class="explain">
<h4>图 1 超详细解读（来龙去脉）</h4>
<p><strong>背景与目的：</strong>在推进大样本之前，需要一张“成对协议下谁赢、赢多少”的总览图，把四个实验（两流域×两模型）的样本外技巧摆在同一坐标上，避免口头比较。</p>
<p><strong>全篇作用：</strong>它是 go/no-go 的定量门闩：雪区必须明显提升，负对照不能出现虚假大增益。</p>
<p><strong>如何阅读：</strong>横轴是流域；每组柱对应 NSE 与 KGE。颜色区分指标族，同一指标下再对比 XAJ-MZ 与 XAJ-Snow。数值越高越好（NSE/KGE 上限为 1）。</p>
<p><strong>可看出：</strong>01013500 上 XAJ-Snow 柱显著高于 XAJ-MZ（NSE 由负转正）；14306500 两模型几乎等高。</p>
<p><strong>不能看出：</strong>不能外推到“全球都需要加雪”；不能区分提升来自结构还是仅仅多了两个参数的优化运气（需后续公平性实验）。</p>
<p><strong>通俗解释：</strong>像考试成绩单：有雪的流域“补课后成绩飞跃”；几乎没雪的对照班“补课前后差不多”，说明不是随便补课都能涨分。</p>
</div>""",
        "fig2": """
<div class="explain">
<h4>图 2 超详细解读（来龙去脉）</h4>
<p><strong>背景与目的：</strong>指标只给一个分数；过程线展示“错在什么季节、错成什么形状”。</p>
<p><strong>全篇作用：</strong>把“无融雪→降雪当雨立刻产流”的机制假说落到可看见的春汛峰值上。</p>
<p><strong>如何阅读：</strong>横轴为测试期日期（warmup 之后），纵轴为流量。黑线=观测，蓝线=XAJ-MZ，橙线=XAJ-Snow；浅色条带≈3–5 月融雪季。</p>
<p><strong>可看出：</strong>春季峰值时机与量级上，橙线更贴近黑线；蓝线常偏早/偏肥或错峰。</p>
<p><strong>不能看出：</strong>单靠过程线不能证明 SWE 模拟正确；夏秋季残差也可能来自土壤/汇流参数权衡。</p>
<p><strong>通俗解释：</strong>把河流当“蓄水罐出水”。没雪模块时，冬天的“固态水”被当成立刻可流走的雨；有雪模块后，水先存再化，春天洪峰才对得上。</p>
</div>""",
        "fig3": """
<div class="explain">
<h4>图 3 超详细解读（来龙去脉）</h4>
<p><strong>背景与目的：</strong>全时段图信息密度高，春季细节被压缩；放大 2010–2012 连续融雪季以便审稿式细读。</p>
<p><strong>全篇作用：</strong>检查提升是否来自“一两个偶然大洪水”，还是跨年可重复的季节性修正。</p>
<p><strong>如何阅读：</strong>同图 2 的颜色语义；聚焦每个春季多峰结构、起涨点与退水坡。</p>
<p><strong>可看出：</strong>连续年份中 XAJ-Snow 对春峰更稳定地贴合观测。</p>
<p><strong>不能看出：</strong>无法分离气温强迫误差与融雪结构误差；也不能推广到未绘制的其他年份以外的统计总体。</p>
<p><strong>通俗解释：</strong>把三年春天的录像慢放，看“开化放水”的节奏是否被模型学会，而不是只看全年总分。</p>
</div>""",
        "fig4": """
<div class="explain">
<h4>图 4 超详细解读（来龙去脉）</h4>
<p><strong>背景与目的：</strong>负对照流域几乎无雪，用来回答“多两个参数会不会到处涨分”。</p>
<p><strong>全篇作用：</strong>支撑“选择性增益”叙事，防止把 XAJ-Snow 写成万能补丁。</p>
<p><strong>如何阅读：</strong>若蓝/橙过程线高度重叠，且与表中 ΔNSE≈0 一致，则对照成立。</p>
<p><strong>可看出：</strong>两模型过程线接近，指标几乎不变（甚至略降）。</p>
<p><strong>不能看出：</strong>不能证明一切无雪流域都中性——目前只有一个对照；分层大样本后才能给置信区间。</p>
<p><strong>通俗解释：</strong>给不需要羽绒服的地方也发一件羽绒服：如果成绩不变，说明衣服不是“作弊神器”，而是对症工具。</p>
</div>""",
        "fig5": """
<div class="explain">
<h4>图 5 超详细解读（来龙去脉）</h4>
<p><strong>背景与目的：</strong>散点图压缩时间维，突出误差幅度与相关结构。</p>
<p><strong>全篇作用：</strong>与 NSE/KGE/RMSE 数字互证：点云更贴 1:1 线 ↔ 更高相关、更低误差。</p>
<p><strong>如何阅读：</strong>横轴观测、纵轴模拟；1:1 线为完美一致。点越散、越偏，技巧越差。</p>
<p><strong>可看出：</strong>XAJ-Snow 点云更收敛；XAJ-MZ 更分散且偏离。</p>
<p><strong>不能看出：</strong>看不出洪峰迟到还是早到（需过程线）；也看不出季节分层误差。</p>
<p><strong>通俗解释：</strong>像打靶：橙点更靠近靶心对角线，蓝点更“散弹”。</p>
</div>""",
        "fig6": """
<div class="explain">
<h4>图 6 超详细解读（来龙去脉）</h4>
<p><strong>背景与目的：</strong>把 batch1（n=14，rep=200）的成对 ΔNSE 放到雪量梯度上，检验 pilot 方向是否在更多 CAMELS 站重复。</p>
<p><strong>全篇作用：</strong>extended pilot / first-look；不是多区域适用边界终结论。</p>
<p><strong>如何阅读：</strong>横轴 frac_snow，纵轴 ΔNSE=NSE_snow−NSE_mz；正值表示雪模块增益。</p>
<p><strong>可看出：</strong>高雪站多为大正 ΔNSE；低雪站贴近 0 或略负。</p>
<p><strong>不能看出：</strong>不能外推到冻结的 80 站总体；rep=200 轻于 pilot medium。</p>
</div>""",
        "fig7": """
<div class="explain">
<h4>图 7 超详细解读（来龙去脉）</h4>
<p><strong>背景与目的：</strong>按雪量分箱汇总 batch1 ΔNSE，突出分层中位数。</p>
<p><strong>全篇作用：</strong>解释为何全文中位数接近 0（双模型失败站下拉），论文应主报分层中位数。</p>
<p><strong>如何阅读：</strong>各箱的分布与中位线；对照 applicability_first_look.md 表。</p>
<p><strong>可看出：</strong>雪影响箱中位 ΔNSE 大幅为正；无雪箱接近 0。</p>
<p><strong>不能看出：</strong>分箱宽度与样本量仍小，置信区间未估计。</p>
</div>""",
    }
    return blocks[fig_id]


def build_report_html(data: dict) -> str:
    m = data["metrics"]
    rf = data["refine"]
    b1 = data["batch1"]
    p010 = data["params"]["01013500"]
    p143 = data["params"]["14306500"]
    nse_mz = m[("01013500", "mz")]["NSE"]
    nse_sn = m[("01013500", "snow")]["NSE"]
    kge_mz = m[("01013500", "mz")]["KGE"]
    kge_sn = m[("01013500", "snow")]["KGE"]
    nse_c_mz = m[("14306500", "mz")]["NSE"]
    nse_c_sn = m[("14306500", "snow")]["NSE"]
    nse_rf_mz = rf[("01013500", "mz")]["NSE"]
    nse_rf_sn = rf[("01013500", "snow")]["NSE"]
    nse_mz_2000 = data["rep_budget"].get(("01013500", "xaj_mz", 2000))
    nse_sn_2000 = data["rep_budget"].get(("01013500", "xaj_snow", 2000))

    body = f"""
<div class="header-bar">Hydromodel 0.3.2 · XAJ-Snow 完整科研报告 · {esc(data['generated'])} · 研究报告（可含工程细节）</div>
<article class="page">
<section class="cover" id="cover">
  <div class="eyebrow">完整科研报告 · 正式学术风格 · 自包含 HTML</div>
  <h1>XAJ-Snow：从错误的人类活动解释到雪过程结构缺失的诊断、最小修正与工程 Go/No-Go 验证</h1>
  <p class="subtitle">副标题：基于 Caravan 两流域成对实验的可复现研究报告（大样本结论待补充）</p>
  <p class="meta">项目软件：hydromodel 0.3.2　|　生成脚本：scripts/generate_publication_outputs.py　|　状态：<span class="badge">工程 GO</span><span class="badge">论文大样本待补充</span></p>
  <p class="meta">交付物：results/publications/（HTML 自包含；指标来自 basins_metrics.csv）</p>
</section>

<nav class="toc" id="toc">
  <strong>目录（可点击）</strong>
  <ol>
    <li><a href="#exec">执行摘要</a></li>
    <li><a href="#bg">研究背景与目的</a></li>
    <li><a href="#rq">研究问题与假设形成过程</a></li>
    <li><a href="#data">数据来源与数据准备</a></li>
    <li><a href="#methods">方法</a></li>
    <li><a href="#process">研究过程</a></li>
    <li><a href="#results">结果展示</a></li>
    <li><a href="#figdetail">图表超详细解释</a></li>
    <li><a href="#discussion">分析与讨论</a></li>
    <li><a href="#conclusions">主要结论</a></li>
    <li><a href="#limits">局限与展望</a></li>
    <li><a href="#repro">软件与可复现性</a></li>
    <li><a href="#refs">参考文献</a></li>
    <li><a href="#appendix">附录</a></li>
  </ol>
</nav>

<section id="exec">
<h2>1. 执行摘要</h2>
<p>
本报告记录 XAJ-Snow（在 Xin’anjiang model, XAJ 上游增加 CemaNeige-style 融雪层）的工程实现、成对率定与 go/no-go 判定。
在统一的 Shuffled Complex Evolution–University of Arizona (SCE-UA) + Kling–Gupta efficiency (KGE) 协议（rep=800）下，真实测试期指标为：
</p>
<ul>
  <li>camels_01013500（frac_snow≈0.37）：XAJ-MZ 的 Nash–Sutcliffe efficiency (NSE)={fmt(nse_mz,4)}、KGE={fmt(kge_mz,4)}；XAJ-Snow NSE={fmt(nse_sn,4)}、KGE={fmt(kge_sn,4)}（ΔNSE≈{delta(nse_sn,nse_mz)}）。</li>
  <li>camels_14306500（低雪负对照）：XAJ-MZ NSE={fmt(nse_c_mz,4)}；XAJ-Snow NSE={fmt(nse_c_sn,4)}（ΔNSE≈{delta(nse_c_sn,nse_c_mz)}）。</li>
  <li>01013500 最优雪参：Kf≈{fmt(p010['Kf'],2)} mm/°C/day，CTG≈{fmt(p010['CTG'],3)}（未贴边）。单元测试 8/8 PASS。</li>
</ul>
<p>
<strong>判定：工程 GO。</strong> 融雪结构假说在本成对协议下获强支持。
<strong>边界：</strong>不得把双流域试验外推为大样本论文主结论；分层批量、SWE（snow water equivalent）辅助一致性、优化预算/自由度因子实验等仍为“待补充”。
不得声称“首次 XAJ 融雪”。
</p>
</section>

<section id="bg">
<h2>2. 研究背景与目的</h2>
<p>
大样本水文显示，概念模型的“平均技巧”会掩盖特定气候/地貌区间的结构性失效（Knoben et al., 2020；Santos et al., 2025）。
雪影响流域是典型压力测试：若模型不能把降雪暂存并以融雪形式释放，春汛峰现时间与洪量会被系统性扭曲。
</p>
<p>
XAJ 已有融雪/寒区过程耦合先例（Tan et al., 2023；Ju et al., 2024；Dong et al., 2024；Wu et al., 2025），且 Chen et al.（2025）已在 CAMELS 531 流域上把 CemaNeige 接入可微参数学习的积融雪新安江（dMXAJ），中位 KGE 显著提升。
因此本文/本报告贡献不是“第一次加雪/第一次 XAJ–CemaNeige/第一次大样本 XAJ 融雪”，而是：
（1）在统一经典 SCE-UA 协议下做失效诊断；（2）用故意极简、非 ML 的双参数修正做可证伪检验；（3）用负对照约束虚假增益；（4）为后续适用边界与公平性实验铺路。
与 Chen et al.（2025）的“大样本高技巧学习器”叙事相比，本工作追问的是<strong>何时需要最小融雪结构</strong>；与 Wu et al.（2025）及 Dong et al.（2024）相比，强调最小修正 + 负对照，而非更完整寒区物理。
</p>
<p>
本报告目的：把本地真实实验链条（数据→代码→率定→指标→图→判定）写成可独立审阅的完整档案，并与投稿向论文初稿对齐。
</p>
</section>

<section id="rq">
<h2>3. 研究问题与假设形成过程</h2>
<p>
早期直觉曾把 01013500 的差表现归因于人类活动/土地利用复杂。
流域属性对照显示：人类足迹指数 hft≈30.6（010）对 34.3（143），对照流域甚至略高；干旱指数同为约 0.49。
因而“人类活动更强导致更差”缺乏支持（见 basin_alignment 诊断）。
</p>
<p>
转向结构假说：XAJ-MZ 无雪过程，降雪被当作降雨立刻参与产流 → 雪区样本外崩溃；在低雪区则不一定。
可检验预测：
</p>
<ol>
  <li>同一协议下，雪区 XAJ-Snow ≫ XAJ-MZ；</li>
  <li>负对照区 XAJ-Snow ≈ XAJ-MZ（无虚假大增益）；</li>
  <li>雪参 Kf、CTG 落在合理区间且不贴边。</li>
</ol>
<p>
这些预测在 medium go/no-go 中全部满足，从而形成“全速推进分层大样本”的工程决策；论文级总体结论仍待大样本。
</p>
</section>

<section id="data">
<h2>4. 数据来源与数据准备</h2>
<h3>4.1 Caravan 与变量</h3>
<p>
数据来自 Caravan（Kratzert et al., 2023）中的 CAMELS 子集。须强调：Caravan 强迫场≠各地原始 CAMELS 强迫，可能改变概念模型表现（Clerc-Schwarzenbach et al., 2024）。
本实验使用的关键变量：降水 <em>P</em>、潜在蒸散发 PET（诊断默认 FAO Penman–Monteith）、流量 <em>Q</em>、以及 XAJ-Snow 所需的 2 m 气温 <em>T</em>（temperature_2m_mean 写入 minicache）。
</p>
<h3>4.2 两流域角色</h3>
<table>
<tr><th>流域 ID</th><th>角色</th><th>frac_snow</th><th>面积 km²</th><th>干旱指数</th><th>人类足迹</th><th>森林%</th></tr>
<tr><td>camels_01013500</td><td>雪影响诊断目标</td><td class="num">0.37</td><td class="num">2298</td><td class="num">0.49</td><td class="num">30.6</td><td class="num">88.5</td></tr>
<tr><td>camels_14306500</td><td>低雪负对照</td><td class="num">≈0</td><td class="num">859</td><td class="num">0.49</td><td class="num">34.3</td><td class="num">98.7</td></tr>
</table>
<p class="src">来源：results/diagnostics/basin_alignment_01013500_vs_14306500.md；训练/测试日数均为 3652 / 3287，P/E/Q NaN 比例为 0。</p>
<h3>4.3 时段与质量</h3>
<table>
<tr><th>项目</th><th>取值</th></tr>
<tr><td>训练期</td><td>1985-10-01 – 1995-09-30</td></tr>
<tr><td>测试期</td><td>2005-10-01 – 2014-09-30</td></tr>
<tr><td>warmup</td><td>365 d</td></tr>
<tr><td>缺失检查</td><td>两流域训/测 P·E·Q 无 NaN（对齐诊断）</td></tr>
<tr><td>绘图时间轴</td><td>评价 NetCDF 中 warmup 后的测试窗（约 2006-10-01 至 2014-09-30）</td></tr>
</table>
</section>

<section id="methods">
<h2>5. 方法</h2>
<h3>5.1 XAJ-MZ</h3>
<p>
Xin’anjiang model（新安江模型）的 hydromodel 实现，配合 Muskingum–Zhao 汇流，15 个率定参数，无雪蓄变量。全部降水按液态输入产流模块。
</p>
<h3>5.2 CemaNeige-style 融雪层与符号</h3>
<p>
XAJ-Snow 在 XAJ-MZ 前增加集总单带度日融雪层（Valéry et al., 2014；非严格 airGR 复现）。
固定 Ts=0°C、Tr=1°C。自由参数：
</p>
<ul>
  <li><strong>Kf</strong>：度日因子（mm °C<sup>−1</sup> d<sup>−1</sup>），越大则同等正温下融雪越快；搜索 [0,10]。</li>
  <li><strong>CTG</strong>：冷含量/热状态惯性 [-]，∈[0,1]；越大则对既往寒冷记忆越强、融雪启动越滞后。</li>
</ul>
<p>符号：P 降水，T 气温，G 热状态，MeltPot 潜在融雪，Gratio 雪盖因子，M 融雪，SWE 雪水当量。质量守恒要求雨+雪=P（分割后），融雪不超过 SWE。</p>
<p class="eq">rain, snow ← partition(P, T; Ts, Tr)</p>
<p class="eq">SWE ← SWE + snow；G ← min(0, CTG·G + (1−CTG)·T)</p>
<p class="eq">仅当等温（G≈0）时 MeltPot ← min(SWE, max(0, Kf·T))；否则 MeltPot=0</p>
<p class="eq">Gratio ← min(1, SWE/G<sub>threshold</sub>)；M ← min(SWE, (0.9·Gratio+0.1)·MeltPot)</p>
<p>
未外供数组时，G<sub>threshold</sub> 在<strong>每一次</strong>雪模块调用内按该次降雪序列估计为 0.9×年均降雪（雪无流域有极小地板）。因训练/测试分段加载，pilot 会在各时段分别重算阈值，而非把训练期阈值冻结到评价期——属须披露的协议选择，而非率定参数向量中的隐变量。
</p>
<p>
NSE/KGE 越接近 1 越好；NSE&lt;0 表示不如用观测均值作预报。本实验主目标函数为训练期 KGE，报告测试期 NSE 与 KGE。
Kf≈3.5 落在文献常见度日量级（约 2–6）且未贴边，但在无 SWE 约束时仍是<strong>有效参数</strong>而非独立物理辨识。
</p>
<h3>5.3 率定协议</h3>
<p>
算法 SCE-UA（spotpy），目标 KGE；两模型两流域均用 medium 设置 <code>rep</code>=800、<code>ngs</code>=15（成对可比）。
<strong>注意：</strong>匹配预算≠已证明收敛公平；更高 rep、多种子、固定雪参消融等仍为“待补充”，不得把 rep=800 写成充分公平基线。
smoke 曾用 rep=120 仅验证流水线。
<strong>已完成补充：</strong>01013500 上 SciPy NSE refine（Snow NSE={fmt(nse_rf_sn,4)}；MZ NSE={fmt(nse_rf_mz,4)}）；rep=2000 敏感性（MZ NSE={fmt(nse_mz_2000,4)}；Snow NSE={fmt(nse_sn_2000,4)}）；batch1 n=14 @rep=200 分层 first-look。
<strong>仍未完成：</strong>rep=5000；143@rep=2000；冻结 80 站 medium 全量；SWE 一致性；factorial。
</p>
<h3>5.4 模型结构对比</h3>
<table>
<tr><th>项目</th><th>XAJ-MZ</th><th>XAJ-Snow</th></tr>
<tr><td>雪过程</td><td>无</td><td>单带 CemaNeige-style</td></tr>
<tr><td>输入特征</td><td>P, PET</td><td>P, PET, T</td></tr>
<tr><td>参数个数</td><td>15</td><td>17（+Kf,+CTG）</td></tr>
<tr><td>核心产汇流</td><td>XAJ-MZ</td><td>同左（融雪后调用）</td></tr>
</table>
</section>

<section id="process">
<h2>6. 研究过程</h2>
<ol>
  <li>属性诊断否定纯人类活动解释；提出雪过程结构缺失假说。</li>
  <li>工程修复：minicache 写入气温；数据加载 VAR_MAPPING；InvalidIndexError 等相关修复见 diagnostics。</li>
  <li>实现 snow.py / xaj_snow.py 并注册模型；单元测试 8/8。</li>
  <li>smoke（rep=120）验证 pipeline：010 snow NSE 已升至约 0.436。</li>
  <li>medium（rep=800）正式 go/no-go：雪区大幅提升、负对照中性。</li>
  <li>010 SciPy NSE refine 完成；rep=2000（仅 010）完成；batch1 n=14 @rep=200 完成。</li>
  <li>SciencePlots 出图；本脚本汇总为正式报告与论文初稿；consultation 简报供外部顾问阅读。</li>
</ol>
<table>
<tr><th>研究问题</th><th>证据</th><th>当前状态</th></tr>
<tr><td>雪区是否因无融雪而失效？</td><td>010 ΔNSE≈+0.96；过程线春峰改善</td><td>成对协议下支持</td></tr>
<tr><td>是否到处虚假增益？</td><td>143 ΔNSE≈−0.006；batch1 无雪中位≈−0.007</td><td>单对照+first-look 支持中性</td></tr>
<tr><td>大样本适用边界？</td><td>batch1 分层中位；冻结 80 站未全跑</td><td class="todo">待补充：冻结样本 medium</td></tr>
<tr><td>SWE 状态一致性？</td><td>—</td><td class="todo">待补充</td></tr>
<tr><td>优化预算/自由度公平性？</td><td>010@2000 部分完成</td><td class="todo">待补充 factorial / 5000</td></tr>
</table>
</section>

<section id="results">
<h2>7. 结果展示</h2>
<p><strong>表：成对测试期指标（真实 CSV）</strong></p>
{metrics_table_html(data, "zh")}
<table>
<tr><th>流域</th><th>Kf</th><th>CTG</th><th>备注</th></tr>
<tr><td>01013500</td><td class="num">{fmt(p010['Kf'],4)}</td><td class="num">{fmt(p010['CTG'],6)}</td><td>主诊断；未贴边</td></tr>
<tr><td>14306500</td><td class="num">{fmt(p143['Kf'],4)}</td><td class="num">{fmt(p143['CTG'],6)}</td><td>负对照；无雪时参数可退化/欠约束</td></tr>
</table>
<p class="src">参数来源：basins_denorm_params.csv</p>
<p><strong>补充表：01013500 SciPy NSE refine（真实 CSV）</strong></p>
<table>
<tr><th>模型</th><th>NSE</th><th>KGE</th><th>备注</th></tr>
<tr><td>XAJ-Snow refine</td><td class="num">{fmt(nse_rf_sn,4)}</td><td class="num">{fmt(rf[("01013500","snow")]["KGE"],4)}</td><td>补充展示，非成对主结论</td></tr>
<tr><td>XAJ-MZ refine</td><td class="num">{fmt(nse_rf_mz,4)}</td><td class="num">{fmt(rf[("01013500","mz")]["KGE"],4)}</td><td>同左</td></tr>
</table>
<p><strong>Batch1 first-look（n={b1['n']}，rep=200）分层中位 ΔNSE</strong>：雪区≥0.1 → {fmt(b1['snow_ge_med_d'],4)}（n={b1['snow_ge_n']}）；无雪&lt;0.1 → {fmt(b1['snow_lt_med_d'],4)}（n={b1['snow_lt_n']}）；S2&gt;0.3 → {fmt(b1['s2_med_d'],4)}。来源：batch1_paired_metrics.csv / applicability_first_look.md。</p>
"""
    for fig in FIGURES:
        body += figure_block("rep", data, fig, "zh")
        body += report_figure_explain(fig["id"])

    body += f"""
</section>

<section id="figdetail">
<h2>8. 图表超详细解释（汇总说明）</h2>
<p>
上一节已对图 1–7 逐图给出解读。图 1–5 为双站 pilot；图 6–7 为 batch1 first-look。
本报告<strong>不新造</strong>无数据支撑的示意图。工程命令与长跑续跑说明见 diagnostics 下 long-run 文档。
</p>
</section>

<section id="discussion">
<h2>9. 分析与讨论</h2>
<p>
<strong>机制：</strong>雪区增益与春峰改善同向，符合“降雪被当雨”的结构缺陷叙事；负对照中性降低“纯参数个数涨分”嫌疑，但尚未被 factorial 终证。
<strong>与文献：</strong>相对 Tan/Ju/Dong/Wu，尤其相对 Chen et al.（2025，CAMELS 531 流域 dMXAJ+CemaNeige），我们强调诊断—最小修正—负对照—边界，而非宣称首次融雪 XAJ、首次 XAJ–CemaNeige 或首次大样本 XAJ 融雪。
Chen et al.（2025）已证明大样本上加 CemaNeige/可微学习可抬高中位技巧；本工作若完成分层样本，应回答“何时最小融雪结构成为必要”，而不是重复“加雪能涨分”。
<strong>替代解释：</strong>Caravan 强迫偏差、PET 选择、单带气温代表性、土壤参数吞掉雪误差、未观测到的水库调节等仍开放。
</p>
</section>

<section id="conclusions">
<h2>10. 主要结论</h2>
<ol>
  <li>在成对 SCE-UA+KGE（rep=800）协议下，XAJ-Snow 使 01013500 测试 NSE 从 {fmt(nse_mz,3)} 提升至 {fmt(nse_sn,3)}，KGE 从 {fmt(kge_mz,3)} 至 {fmt(kge_sn,3)}。</li>
  <li>负对照 14306500 上技巧基本不变（ΔNSE≈{delta(nse_c_sn,nse_c_mz)}），支持选择性增益。</li>
  <li>Batch1（n=14，rep=200）雪区中位 ΔNSE≈{fmt(b1['snow_ge_med_d'],2)}，无雪≈{fmt(b1['snow_lt_med_d'],3)}——仅作 first-look。</li>
  <li>工程上判定 GO，可继续冻结样本 medium；科学上尚不能给出全球/多区域适用边界终结论。</li>
</ol>
</section>

<section id="limits">
<h2>11. 局限与展望</h2>
<div class="todo">
<strong>待补充实验矩阵</strong>
<table>
<tr><th>实验</th><th>目的</th><th>状态</th></tr>
<tr><td>分层冻结样本 medium 率定</td><td>RQ1–RQ2 总体推断</td><td>已冻结 80 站；全量未完成（batch1=14@200 完成）</td></tr>
<tr><td>ERA5-Land SWE 辅助一致性</td><td>状态约束，非独立验证</td><td>未完成</td></tr>
<tr><td>优化预算倍数 × seeds</td><td>公平性</td><td>部分：010@2000 完成；5000 / 143@2000 未跑</td></tr>
<tr><td>固定雪参 vs 自由雪参</td><td>额外自由度</td><td>未完成</td></tr>
<tr><td>scipy NSE refine</td><td>补充展示</td><td><strong>已完成</strong>（010）</td></tr>
<tr><td>属性→ΔKGE 适用边界</td><td>RQ3</td><td>未完成</td></tr>
<tr><td>optimizer×sharing factorial</td><td>归因分离</td><td>可选，未做则不出图</td></tr>
</table>
</div>
<p>实现局限：单高程带；Ts/Tr 固定；Gthreshold 默认按<strong>当次调用</strong>降雪序列估计（训练/测试分段加载时各自重算，未冻结训练值）；17 vs 15 参数。</p>
</section>

<section id="repro">
<h2>12. 软件与可复现性</h2>
<p>
公开快照：<a href="https://github.com/Coucou2016/hydromodel-xaj-snow">https://github.com/Coucou2016/hydromodel-xaj-snow</a>
（<code>master</code> @ 生成时 <code>{esc(data['git'])}</code>；含源码/docs/figures/publications/consultation/配置/测试与生成脚本；不含大体积 nc、<code>_portable_data</code>/hydrodata，亦不含完整 SpotPy 率定 dump 树）。
用户须本地准备 Caravan/CAMELS 数据；细节见 <code>docs/local/github_public_repo.md</code>。
</p>
<pre style="white-space:pre-wrap;background:#f6f6f6;border:1px solid #ddd;padding:0.8em;font-size:0.86rem;">
# after cloning the public snapshot and placing Caravan/CAMELS caches locally
$env:HOME = (Get-Location).Path
$env:HYDRO_SETTING_FILE = Join-Path $env:HOME "hydro_setting.yml"
python -m pytest test/test_snow.py -v
.\\RUN_GO_NOGO_XAJ_SNOW.ps1 smoke
.\\RUN_GO_NOGO_XAJ_SNOW.ps1 medium
python scripts/generate_publication_outputs.py
</pre>
<p>关键源码：hydromodel/models/snow.py, xaj_snow.py, xaj.py, model_config.py。本脚本不修改模型计算逻辑。Zenodo DOI：待提交前铸造。</p>
</section>

<section id="refs">
<h2>13. 参考文献</h2>
<p class="src">仅纳入本地已核验 DOI（docs/local/literature_review_xaj_snow.md）。</p>
{refs_html()}
</section>

<section id="appendix">
<h2>14. 附录</h2>
<h3>A. 术语表</h3>
<table>
<tr><th>术语</th><th>全称/含义</th></tr>
<tr><td>XAJ</td><td>Xin’anjiang model，新安江模型</td></tr>
<tr><td>XAJ-MZ</td><td>XAJ + Muskingum–Zhao 汇流，无雪</td></tr>
<tr><td>XAJ-Snow</td><td>XAJ-MZ + CemaNeige-style 融雪层</td></tr>
<tr><td>NSE</td><td>Nash–Sutcliffe efficiency</td></tr>
<tr><td>KGE</td><td>Kling–Gupta efficiency</td></tr>
<tr><td>SCE-UA</td><td>Shuffled Complex Evolution–University of Arizona</td></tr>
<tr><td>PET</td><td>potential evapotranspiration，潜在蒸散发</td></tr>
<tr><td>SWE</td><td>snow water equivalent，雪水当量</td></tr>
<tr><td>Kf</td><td>度日融雪因子</td></tr>
<tr><td>CTG</td><td>冷含量系数</td></tr>
<tr><td>P, T, G, M</td><td>降水、气温、热状态、融雪</td></tr>
</table>
<h3>B. 文件清单（成果）</h3>
<ul>
  <li>results/publications/xaj_snow_manuscript.html|.md|.pdf</li>
  <li>results/publications/report.html|.md|.pdf</li>
</ul>
<h3>C. 审计状态</h3>
<ul>
  <li>指标与 CSV 一致（脚本启动时 assert）</li>
  <li>HTML 图片均为 data URI；CSS 内联；无 CDN</li>
  <li>Git：本轮允许 commit/push 公开仓（不含大 nc / hydrodata）</li>
</ul>
</section>

<div class="footer-note">生成时间 {esc(data['generated'])}。数字来自真实 evaluation CSV；待补充项已显式标注。</div>
</article>
"""
    return (
        "<!DOCTYPE html>\n<html lang=\"zh-CN\">\n<head>\n"
        "<meta charset=\"utf-8\"/>\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>\n"
        "<title>XAJ-Snow 完整科研报告</title>\n"
        f"<style>{shared_css()}</style>\n"
        "</head>\n<body>\n"
        f"{body}\n"
        "</body>\n</html>\n"
    )


def html_to_markdownish(title: str, lang: str, data: dict, which: str) -> str:
    """Produce a full Markdown sibling; images use relative paths (not self-contained)."""
    m = data["metrics"]
    lines = [
        f"# {title}",
        "",
        f"> Generated: {data['generated']}",
        ">",
        "> **Note:** HTML/PDF are fully self-contained (base64 figures). "
        "This Markdown uses relative image paths for in-repo reading.",
        "",
    ]
    if which == "ms":
        lines += [
            "## Abstract",
            "",
            "See the HTML manuscript for the full English Abstract, Introduction, Methods, "
            "pilot Results, Discussion, Conclusions, and verified References. "
            "Large-sample Results remain pending.",
            "",
            "## Table: pilot metrics (from basins_metrics.csv)",
            "",
            "| Basin | Model | NSE | KGE | RMSE |",
            "|---|---|---:|---:|---:|",
        ]
        for basin, model, key in [
            ("01013500", "XAJ-MZ", ("01013500", "mz")),
            ("01013500", "XAJ-Snow", ("01013500", "snow")),
            ("14306500", "XAJ-MZ", ("14306500", "mz")),
            ("14306500", "XAJ-Snow", ("14306500", "snow")),
        ]:
            d = m[key]
            lines.append(
                f"| {basin} | {model} | {fmt(d['NSE'],4)} | {fmt(d['KGE'],4)} | {fmt(d['RMSE'],4)} |"
            )
        lines += ["", "## Figures", ""]
        for fig in FIGURES:
            lines += [
                f"### Figure {fig['id'].replace('fig','')}. {fig['ms_title']}",
                "",
                f"![{fig['ms_title']}](../figures/{fig['file']})",
                "",
                f"*Data source:* {fig['source']}",
                "",
            ]
        lines += [
            "## Pending",
            "",
            "- Stratified large-sample experiments",
            "- SWE auxiliary consistency",
            "- Optimizer / parameter-freedom fairness & factorial",
            "- Code/data DOI; author contributions; acknowledgements",
            "",
            "## References",
            "",
            "Verified DOIs listed in `docs/local/literature_review_xaj_snow.md` "
            "and mirrored in the HTML manuscript.",
            "",
        ]
    else:
        lines += [
            "## 执行摘要",
            "",
            f"- 01013500: XAJ-MZ NSE={fmt(m[('01013500','mz')]['NSE'],4)}, "
            f"XAJ-Snow NSE={fmt(m[('01013500','snow')]['NSE'],4)}",
            f"- 14306500: XAJ-MZ NSE={fmt(m[('14306500','mz')]['NSE'],4)}, "
            f"XAJ-Snow NSE={fmt(m[('14306500','snow')]['NSE'],4)}",
            f"- Kf≈{fmt(data['params']['01013500']['Kf'],2)}, "
            f"CTG≈{fmt(data['params']['01013500']['CTG'],3)}；测试 8/8 PASS；工程 GO",
            "",
            "完整章节（背景、假设转向、数据、方法、过程、讨论、局限、术语表）见 HTML 报告；"
            "以下给出指标表与图件链接，图注解释与 HTML 一致。",
            "",
            "## 成对指标表",
            "",
            "| 流域 | 模型 | NSE | KGE | RMSE |",
            "|---|---|---:|---:|---:|",
        ]
        for basin, model, key in [
            ("01013500", "XAJ-MZ", ("01013500", "mz")),
            ("01013500", "XAJ-Snow", ("01013500", "snow")),
            ("14306500", "XAJ-MZ", ("14306500", "mz")),
            ("14306500", "XAJ-Snow", ("14306500", "snow")),
        ]:
            d = m[key]
            lines.append(
                f"| {basin} | {model} | {fmt(d['NSE'],4)} | {fmt(d['KGE'],4)} | {fmt(d['RMSE'],4)} |"
            )
        lines += ["", "## 图件与解读要点", ""]
        explain_short = {
            "fig1": "成对 NSE/KGE 总览；雪区升高、对照平坦。",
            "fig2": "010 全时段过程线；春汛改善。",
            "fig3": "2010–2012 春季放大。",
            "fig4": "143 负对照过程线接近重合。",
            "fig5": "010 观测-模拟散点更贴 1:1。",
        }
        for fig in FIGURES:
            n = fig["id"].replace("fig", "")
            lines += [
                f"### 图 {n}. {fig['rep_title']}",
                "",
                f"![{fig['rep_title']}](../figures/{fig['file']})",
                "",
                f"- 来源：{fig['source']}",
                f"- 解读：{explain_short[fig['id']]}（完整来龙去脉见 HTML）",
                "",
            ]
        lines += [
            "## 待补充",
            "",
            "- 分层大样本、SWE 一致性、公平性/factorial、scipy refine、区域化适用边界",
            "",
            "## 参考文献",
            "",
            "见 `docs/local/literature_review_xaj_snow.md`（已核验 DOI）。",
            "",
        ]
    # Expand MD with more complete prose extracted from HTML text content for parity
    return "\n".join(lines)


def _cell_text(cell_html: str) -> str:
    t = re.sub(r"<br\s*/?>", " ", cell_html, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    return html.unescape(t).replace("|", "\\|").strip()


def _table_to_md(table_html: str) -> str:
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_html, flags=re.S | re.I)
    md_rows = []
    for row in rows:
        cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, flags=re.S | re.I)
        md_rows.append("| " + " | ".join(_cell_text(c) for c in cells) + " |")
    if not md_rows:
        return ""
    ncols = md_rows[0].count("|") - 1
    sep = "| " + " | ".join(["---"] * max(ncols, 1)) + " |"
    return "\n".join([md_rows[0], sep, *md_rows[1:]]) + "\n\n"


def expand_markdown_from_html(html_text: str, title: str, data: dict, which: str) -> str:
    """Build Markdown sibling: tables preserved, figures as relative paths."""
    text = re.sub(r"<style>.*?</style>", "", html_text, flags=re.S | re.I)
    text = re.sub(r"<script>.*?</script>", "", text, flags=re.S | re.I)
    text = re.sub(r"<head>.*?</head>", "", text, flags=re.S | re.I)

    fig_iter = iter(FIGURES)

    def _img_repl(_m):
        try:
            fig = next(fig_iter)
        except StopIteration:
            return ""
        label = fig["ms_title"] if which == "ms" else fig["rep_title"]
        return f"\n\n![{label}](../figures/{fig['file']})\n\n"

    def _table_repl(m):
        return "\n\n" + _table_to_md(m.group(0))

    text = re.sub(r"<table\b.*?</table>", _table_repl, text, flags=re.S | re.I)
    text = re.sub(r"<img\b[^>]*>", _img_repl, text, flags=re.I)
    text = re.sub(r"<h1[^>]*>(.*?)</h1>", r"\n# \1\n", text, flags=re.S | re.I)
    text = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n## \1\n", text, flags=re.S | re.I)
    text = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n### \1\n", text, flags=re.S | re.I)
    text = re.sub(r"<h4[^>]*>(.*?)</h4>", r"\n#### \1\n", text, flags=re.S | re.I)
    text = re.sub(r"<li[^>]*>(.*?)</li>", lambda m: "- " + _cell_text(m.group(1)) + "\n", text, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</?(strong|b)>", "**", text, flags=re.I)
    text = re.sub(r"</?(em|i)>", "*", text, flags=re.I)
    text = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", text, flags=re.S | re.I)
    text = re.sub(r"<a[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", r"[\2](\1)", text, flags=re.S | re.I)
    text = re.sub(r"<p[^>]*>", "\n", text, flags=re.I)
    text = re.sub(r"</p>", "\n", text, flags=re.I)
    text = re.sub(r"<pre[^>]*>(.*?)</pre>", r"\n```\n\1\n```\n", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    header = (
        f"<!-- Markdown sibling of {title}. "
        "HTML/PDF are the fully self-contained deliverables (base64 figures + inline CSS). "
        "This Markdown keeps relative image paths for in-repo reading. -->\n\n"
    )
    return header + text.strip() + "\n"


def print_pdf(html_path: Path, pdf_path: Path) -> None:
    chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    edge = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    browser = chrome if chrome.exists() else edge
    if not browser.exists():
        raise RuntimeError("No Chrome/Edge found for print-to-pdf")
    html_uri = html_path.resolve().as_uri()
    # Prefer new headless; allow local file access for self-contained HTML.
    cmd = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--allow-file-access-from-files",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path.resolve()}",
        html_uri,
    ]
    subprocess.run(cmd, check=True, cwd=str(REPO))
    if not pdf_path.exists() or pdf_path.stat().st_size < 10_000:
        raise RuntimeError(f"PDF not created properly: {pdf_path}")


def validate_html(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    problems = []
    for req in ("<!DOCTYPE html>", "<html", "<head", "<style", "<body"):
        if req.lower() not in text.lower() and req not in text:
            problems.append(f"missing {req}")
    # external resource deps in tags (allow https in references text)
    for m in re.finditer(r"<img\b[^>]*src=['\"]([^'\"]+)['\"]", text, flags=re.I):
        src = m.group(1)
        if not src.startswith("data:image/"):
            problems.append(f"non-data img src: {src[:80]}")
    if re.search(r"<link[^>]+href=['\"]https?://", text, flags=re.I):
        problems.append("external link stylesheet")
    if re.search(r"<script[^>]+src=['\"]https?://", text, flags=re.I):
        problems.append("external script")
    if 'src="results/' in text or "src='results/" in text:
        problems.append("local relative results/ image path found")
    return problems


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    data = load_all()
    print("Metrics OK; figures encoded.")

    ms_html = build_manuscript_html(data)
    rep_html = build_report_html(data)

    paths = {
        "ms_html": OUT / "xaj_snow_manuscript.html",
        "ms_md": OUT / "xaj_snow_manuscript.md",
        "ms_pdf": OUT / "xaj_snow_manuscript.pdf",
        "rep_html": OUT / "report.html",
        "rep_md": OUT / "report.md",
        "rep_pdf": OUT / "report.pdf",
    }
    paths["ms_html"].write_text(ms_html, encoding="utf-8")
    paths["rep_html"].write_text(rep_html, encoding="utf-8")
    paths["ms_md"].write_text(
        expand_markdown_from_html(ms_html, "XAJ-Snow manuscript", data, "ms"),
        encoding="utf-8",
    )
    paths["rep_md"].write_text(
        expand_markdown_from_html(rep_html, "XAJ-Snow report", data, "rep"),
        encoding="utf-8",
    )

    for label, p in (("manuscript", paths["ms_html"]), ("report", paths["rep_html"])):
        probs = validate_html(p)
        if probs:
            raise SystemExit(f"HTML validation failed for {label}: {probs}")
        print(f"HTML validation OK: {p.name}")

    print("Printing PDFs via headless Chrome/Edge...")
    print_pdf(paths["ms_html"], paths["ms_pdf"])
    print_pdf(paths["rep_html"], paths["rep_pdf"])

    print("\nOutputs:")
    for k, p in paths.items():
        print(f"  {k}: {p}  ({p.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
