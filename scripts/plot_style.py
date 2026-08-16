"""Unified SciencePlots + Times New Roman style for reports and papers.

Always use the ``science`` + ``no-latex`` style combination so environments
without a TeX installation do not fail on ``usetex``.
"""

from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Import registers SciencePlots styles with matplotlib.
import scienceplots  # noqa: F401

PREFERRED_SERIF = ("Times New Roman", "Times", "Nimbus Roman", "Liberation Serif", "DejaVu Serif")

# Colorblind-friendly accents used across report / paper figures.
COLORS = {
    "obs": "#111111",
    "mz": "#0072B2",
    "snow": "#D55E00",
    "nse": "#0072B2",
    "kge": "#009E73",
    "grid": "#B0B0B0",
    "spring": "#56B4E9",
}


def _available_fonts() -> set[str]:
    return {f.name for f in fm.fontManager.ttflist}


def resolve_serif_font(candidates: Sequence[str] = PREFERRED_SERIF) -> str:
    available = _available_fonts()
    for name in candidates:
        if name in available:
            return name
    return "DejaVu Serif"


ACTIVE_SERIF_FONT = resolve_serif_font()


def apply_plot_style(*, base_size: float = 10.0) -> str:
    """Apply SciencePlots (no-latex) + Times New Roman (or fallback) rcParams.

    Returns the serif font family actually selected.
    """
    plt.style.use(["science", "no-latex"])
    font = resolve_serif_font()
    global ACTIVE_SERIF_FONT
    ACTIVE_SERIF_FONT = font
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": [font, "DejaVu Serif", "serif"],
            "mathtext.fontset": "stix",
            "font.size": base_size,
            "axes.titlesize": base_size + 1,
            "axes.labelsize": base_size,
            "xtick.labelsize": base_size - 1,
            "ytick.labelsize": base_size - 1,
            "legend.fontsize": base_size - 1.5,
            "legend.frameon": False,
            "axes.linewidth": 0.8,
            "lines.linewidth": 1.0,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.size": 3.5,
            "ytick.major.size": 3.5,
            "figure.dpi": 150,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "axes.unicode_minus": False,
            "text.usetex": False,
        }
    )
    return font


def save_fig(
    fig: plt.Figure,
    stem: str | Path,
    *,
    dpi: int = 300,
    formats: Iterable[str] = ("png", "pdf"),
    close: bool = False,
) -> list[Path]:
    """Save figure to PNG (default 300 dpi) and PDF (and optional SVG)."""
    stem_path = Path(stem)
    stem_path.parent.mkdir(parents=True, exist_ok=True)
    # Drop suffix if caller passed a path with extension.
    if stem_path.suffix.lower() in {".png", ".pdf", ".svg"}:
        stem_path = stem_path.with_suffix("")
    out_paths: list[Path] = []
    for fmt in formats:
        out = stem_path.with_suffix(f".{fmt}")
        kw = {"bbox_inches": "tight", "facecolor": "white"}
        if fmt == "png":
            kw["dpi"] = dpi
        fig.savefig(out, format=fmt, **kw)
        out_paths.append(out)
    if close:
        plt.close(fig)
    return out_paths


def fig_to_png_b64(fig: plt.Figure, *, dpi: int = 300, close: bool = True) -> str:
    """Encode a figure as a base64 PNG for single-file HTML reports."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    if close:
        plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def style_notes() -> str:
    return (
        f"SciencePlots styles: science + no-latex; "
        f"serif font in use: {ACTIVE_SERIF_FONT}; "
        f"PNG dpi>=300; PDF fonttype=42 (editable)."
    )
