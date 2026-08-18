"""
make_charts.py

Generates the report charts from bug_counts.csv:

  - charts/patches_and_fixes_per_year.png : two stacked panels — patches released
                                            and security-labeled fixes, per year
  - charts/product_breakdown.png          : horizontal bar of security fixes by product
  - charts/timeline.png                   : Portal/Server patches over time, sized by fix count

A dark-mode twin of each is written to charts/dark/.

Design rules applied (see the dataviz method):
  - One y-axis per plot. Never two scales on one set of marks.
  - Categorical hues assigned in fixed slot order and capped: on the all-pairs
    forms (scatter) only slots 1-2 carry identity, everything else is neutral.
    Palette validated with validate_palette.js in both modes.
  - Legends list exactly the colors the chart actually draws.
  - Selective direct labels, never a number on every mark.
  - Recessive hairline grid, no top/right spines, marks ringed in the surface
    color so overlapping dots stay separable.
  - Footnotes are hard-wrapped so the saved canvas keeps its intended aspect
    ratio (bbox_inches="tight" otherwise stretches the figure to fit one long
    line and squeezes the plot into a corner).

Run:  python make_charts.py
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
COUNTS_CSV = ROOT / "bug_counts.csv"
CHART_DIR = ROOT / "charts"

# The two products that carry the story; everything else is deliberately neutral.
FOCUS_PORTAL = "Portal for ArcGIS"
FOCUS_SERVER = "ArcGIS Server"


# --- Theme -------------------------------------------------------------------


@dataclass(frozen=True)
class Theme:
    """One rendering mode. Both palettes pass the six colour checks against their
    own surface (validate_palette.js, --pairs all)."""

    name: str
    surface: str
    series_1: str  # categorical slot 1 — Portal for ArcGIS / single-series bars
    series_2: str  # categorical slot 2 — ArcGIS Server
    neutral: str   # non-focus categories; carries no identity
    text_primary: str
    text_secondary: str
    text_muted: str
    grid: str
    subdir: str


LIGHT = Theme(
    name="light",
    surface="#fcfcfb",
    series_1="#2a78d6",
    series_2="#eb6834",
    neutral="#9a9992",
    text_primary="#0b0b0b",
    text_secondary="#52514e",
    text_muted="#75746e",
    grid="#e6e5e0",
    subdir="",
)

DARK = Theme(
    name="dark",
    surface="#1a1a19",
    series_1="#3987e5",
    series_2="#d95926",
    neutral="#8a8981",
    text_primary="#ffffff",
    text_secondary="#c3c2b7",
    text_muted="#9d9c93",
    grid="#333330",
    subdir="dark",
)


# --- Helpers -----------------------------------------------------------------


def style_axes(ax: plt.Axes, t: Theme, *, grid_axis: str = "y") -> None:
    """Strip chartjunk: no top/right spines, hairline recessive grid and axes."""
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("bottom", "left"):
        ax.spines[spine].set_color(t.grid)
        ax.spines[spine].set_linewidth(0.8)
    ax.tick_params(colors=t.text_secondary, length=0, labelsize=9.5)
    ax.grid(False)
    if grid_axis in ("x", "both"):
        ax.xaxis.grid(True, color=t.grid, linewidth=0.8, linestyle="-", zorder=0)
    if grid_axis in ("y", "both"):
        ax.yaxis.grid(True, color=t.grid, linewidth=0.8, linestyle="-", zorder=0)
    ax.set_axisbelow(True)
    ax.set_facecolor(t.surface)


def _block_height(fig: plt.Figure, n_lines: int, fontsize: float,
                  linespacing: float) -> float:
    """Height of an n-line text block as a fraction of the figure height.

    Measured from the font metrics rather than assumed, so a headline that wraps
    to two lines pushes the deck down instead of printing on top of it.
    """
    return n_lines * fontsize * linespacing / (72.0 * fig.get_figheight())


def titles(fig: plt.Figure, t: Theme, title: str, subtitle: str,
           width: int = 96) -> float:
    """Headline + deck, left-aligned to the figure in a strong hierarchy.

    Anchored to the figure rather than the axes so a long headline is not pushed
    off the right edge by a wide left margin (the product chart needs a 30%
    margin for its category labels). Returns the y of the bottom of the block so
    the caller can set its top margin below it.
    """
    nl = "\n"
    top = 0.982
    title_lines = textwrap.wrap(title, width=width - 20)
    fig.text(0.012, top, nl.join(title_lines), fontsize=14, fontweight="bold",
             color=t.text_primary, ha="left", va="top", linespacing=1.25)

    y = top - _block_height(fig, len(title_lines), 14, 1.25) - 0.012
    subtitle_lines = textwrap.wrap(subtitle, width=width)
    fig.text(0.012, y, nl.join(subtitle_lines), fontsize=9.5,
             color=t.text_secondary, ha="left", va="top", linespacing=1.5)
    return y - _block_height(fig, len(subtitle_lines), 9.5, 1.5)


def add_footer(fig: plt.Figure, t: Theme, source: str, note: str = "",
               width: int = 118) -> float:
    """Source line plus methodology note at the bottom-left, hard-wrapped.

    Wrapping matters for more than tidiness: with bbox_inches="tight" an
    unwrapped one-line note widens the whole saved canvas to fit it, which is
    what squashed the earlier versions of these charts into the left third of
    a 3800px-wide image. Returns the y of the top of the block so the caller can
    set its bottom margin above it.
    """
    lines = textwrap.wrap(f"Source: {source}", width=width)
    if note:
        lines += textwrap.wrap(f"Note: {note}", width=width)
    top = 0.014 + _block_height(fig, len(lines), 7.5, 1.5)
    fig.text(0.012, top, "\n".join(lines), fontsize=7.5, color=t.text_muted,
             ha="left", va="top", linespacing=1.5)
    return top


def save(fig: plt.Figure, t: Theme, name: str) -> None:
    out_dir = CHART_DIR / t.subdir if t.subdir else CHART_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / name
    fig.savefig(out, dpi=200, facecolor=t.surface)
    plt.close(fig)
    print(f"wrote {out.relative_to(ROOT)}")


def year_labels(years) -> list[str]:
    return [f"{int(y)}\nYTD" if int(y) == 2026 else str(int(y)) for y in years]


# --- Chart 1: patches released and security fixes per year -------------------


def chart_patches_and_fixes_per_year(counts: pd.DataFrame, t: Theme) -> None:
    """Two panels stacked on a shared year axis.

    These are different units (patch releases vs. individual BUG-IDs), so they
    get one axis each rather than being overlaid on a twin axis — the alignment
    of two y-scales is arbitrary and invents a correlation the data doesn't
    have. Stacking them on a shared x still lets the eye compare the shapes,
    which is the whole point: 2022 released the most patches, 2025 fixed the
    most bugs.
    """
    by_year = (
        counts.groupby("year")
        .agg(patches=("security_bugs", "size"), fixes=("security_bugs", "sum"))
        .reset_index()
        .sort_values("year")
    )

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(9.5, 7.4), sharex=True,
        gridspec_kw={"hspace": 0.34},
    )
    fig.patch.set_facecolor(t.surface)

    x = np.arange(len(by_year))
    is_partial = by_year["year"].astype(int).values == 2026

    panels = [
        (ax_top, by_year["patches"].values.astype(int), "Patches released",
         "Patches released per year"),
        (ax_bot, by_year["fixes"].values.astype(int), "Bug fixes",
         "Security-labeled bug fixes introduced per year"),
    ]

    for ax, values, ylabel, panel_title in panels:
        style_axes(ax, t)
        # A partial year is drawn hollow rather than in a second hue: it is the
        # same series measured over less time, not a different category.
        ax.bar(x[~is_partial], values[~is_partial], width=0.52,
               color=t.series_1, zorder=2)
        ax.bar(x[is_partial], values[is_partial], width=0.52,
               facecolor=t.surface, edgecolor=t.series_1, linewidth=1.8,
               hatch="///", zorder=2)

        headroom = max(values.max() * 1.24, 1)
        ax.set_ylim(0, headroom)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True, nbins=5))
        ax.set_ylabel(ylabel, color=t.text_secondary, fontsize=9.5, labelpad=8)
        for xi, v in zip(x, values):
            ax.text(xi, v + headroom * 0.03, f"{v}", ha="center", va="bottom",
                    color=t.text_primary, fontsize=10, fontweight="bold")
        ax.text(0, 1.04, panel_title, transform=ax.transAxes, fontsize=10.5,
                fontweight="bold", color=t.text_primary, ha="left", va="bottom")

    ax_bot.set_xticks(x)
    ax_bot.set_xticklabels(year_labels(by_year["year"]), color=t.text_primary,
                           fontsize=10)

    head_bottom = titles(
           fig, t,
           "Patch cadence and security-fix volume tell different stories",
           "Esri ArcGIS Enterprise security patches, 2021–2026 YTD. 2022 shipped the "
           "most patches; 2025 fixed by far the most bugs. Hatched bars are the "
           "partial 2026 year.",
           width=92)

    foot_top = add_footer(
        fig, t,
        source="Esri Support patch pages (support.esri.com/patches-updates) and Esri "
               "patch notification JSON (content.esri.com/patch_notification/patches.json), "
               "Aug 2026.",
        note="Patches: one row per consolidated patch name per year; per-version URLs "
             "for the same patch (e.g. Log4j, Notebook Server) are consolidated. Bug "
             "fixes: only the security-labeled BUG-IDs each patch introduces; cumulative "
             "“To avoid conflicts” re-lists are excluded. 2026 covers Jan 1 – Aug 18 only. "
             "Full values are in bug_counts.csv.",
    )
    # Panels live between the measured headline block and the measured footnote
    # block, so neither can ever overlap the plot however the text wraps.
    fig.subplots_adjust(top=head_bottom - 0.035, bottom=foot_top + 0.055,
                        left=0.09, right=0.98)
    save(fig, t, "patches_and_fixes_per_year.png")


# --- Chart 2: security fixes by product --------------------------------------


def chart_product_breakdown(counts: pd.DataFrame, t: Theme) -> None:
    """Horizontal bar, sorted. Portal and Server are the story, so they carry the
    series hue and the long tail is neutral — emphasis, not a value ramp."""
    by_product = (
        counts.groupby("product")
        .agg(fixes=("security_bugs", "sum"))
        .reset_index()
    )
    by_product = by_product[by_product["fixes"] > 0].sort_values("fixes")

    total = int(by_product["fixes"].sum())
    focus = {FOCUS_PORTAL, FOCUS_SERVER}
    focus_share = int(by_product[by_product["product"].isin(focus)]["fixes"].sum())
    colors = [t.series_1 if p in focus else t.neutral for p in by_product["product"]]

    fig, ax = plt.subplots(figsize=(9.5, 6.2))
    fig.patch.set_facecolor(t.surface)
    style_axes(ax, t, grid_axis="x")

    y = np.arange(len(by_product))
    ax.barh(y, by_product["fixes"], color=colors, zorder=2, height=0.6)

    xmax = by_product["fixes"].max()
    ax.set_xlim(0, xmax * 1.18)
    for i, (p, v) in enumerate(zip(by_product["product"], by_product["fixes"])):
        share = f"   ({v / total:.0%})" if p in focus else ""
        ax.text(v + xmax * 0.013, i, f"{int(v)}{share}", va="center", ha="left",
                color=t.text_primary if p in focus else t.text_secondary,
                fontsize=9.5, fontweight="bold" if p in focus else "normal")

    ax.set_yticks(y)
    ax.set_yticklabels(by_product["product"], color=t.text_primary, fontsize=9.5)
    ax.set_xlabel("Security-labeled bug fixes, 2021–2026 YTD",
                  color=t.text_secondary, fontsize=9.5, labelpad=8)

    handles = [
        plt.Rectangle((0, 0), 1, 1, color=t.series_1,
                      label="Portal for ArcGIS and ArcGIS Server"),
        plt.Rectangle((0, 0), 1, 1, color=t.neutral, label="All other products"),
    ]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=9,
              labelcolor=t.text_secondary)

    head_bottom = titles(
        fig, t,
        f"Portal for ArcGIS and ArcGIS Server account for "
        f"{focus_share / total:.0%} of all security fixes",
        f"Security-labeled bug fixes introduced by Esri security patches, by product "
        f"(n={total} fixes across {len(counts)} patches, 2021-2026 YTD)",
    )

    foot_top = add_footer(
        fig, t,
        source="Esri Support patch pages (support.esri.com/patches-updates), scraped Aug 2026.",
        note="Only security-labeled bug fixes are shown; non-security defect fixes listed "
             "on the same patch pages are excluded, as is ArcGIS Web Adaptor (zero "
             "security-labeled fixes). A fix is security-labeled when its description "
             "contains keywords such as XSS, SQL injection, directory traversal, SSRF, "
             "CSRF, unvalidated redirect or log4j — see README.md for the full keyword "
             "list. Per-product values are in bug_counts.csv.",
    )
    fig.subplots_adjust(top=head_bottom - 0.030, bottom=foot_top + 0.090,
                        left=0.295, right=0.98)
    save(fig, t, "product_breakdown.png")


# --- Chart 3: timeline of patches ---------------------------------------------


def chart_timeline(counts: pd.DataFrame, t: Theme) -> None:
    """One dot per patch: release date vs. how many security fixes it introduced.

    Scatter is an all-pairs form, so identity is capped at the two validated
    focus hues and every other product is neutral — the previous version's
    ten-colour scheme had a legend that named colours the plot never drew
    (GeoEvent was gold on the plot but teal in the legend).
    """
    df = counts.copy()
    df["date"] = pd.to_datetime(df["release_date"])
    # Scope: the two products that carry 91% of the security fixes, and only
    # patches that actually introduced one. The long tail of single-fix products
    # and the advisory-only patches are in product_breakdown.png and
    # bug_counts.csv; here they were only adding marks with nothing to say.
    df = df[df["product"].isin([FOCUS_PORTAL, FOCUS_SERVER])]
    df = df[df["security_bugs"] > 0].sort_values("date")

    product_color = {FOCUS_PORTAL: t.series_1, FOCUS_SERVER: t.series_2}

    fig, ax = plt.subplots(figsize=(11, 6.0))
    fig.patch.set_facecolor(t.surface)
    style_axes(ax, t)

    # Area proportional to the fix count, with a floor so a 1-fix patch is still
    # a comfortable mark. Surface-coloured ring keeps overlapping dots separable.
    for name in (FOCUS_PORTAL, FOCUS_SERVER):
        sub = df[df["product"] == name]
        if sub.empty:
            continue
        ax.scatter(sub["date"], sub["security_bugs"],
                   s=40 + sub["security_bugs"] * 26,
                   c=product_color[name], alpha=0.85,
                   edgecolor=t.surface, linewidth=2, zorder=3, label=name)

    ymax = int(df["security_bugs"].max())
    ax.set_ylim(0, ymax * 1.32)
    ax.set_ylabel("Security-labeled fixes per patch",
                  color=t.text_secondary, fontsize=9.5, labelpad=8)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(5))

    ax.set_xlim(datetime(2020, 10, 1), datetime(2027, 1, 31))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(axis="x", colors=t.text_secondary, labelsize=10)

    # Direct-label only the outliers, each placed on the side that has room, so
    # the two 25-fix patches eight months apart no longer print over each other.
    annotations = [
        # (row title, short label, side the label extends toward, y offset in pt).
        # Sides are chosen so the four labels never share horizontal space: the
        # two 25-fix patches eight months apart point away from each other.
        ("ArcGIS Server Security 2025 Update 1",
         "ArcGIS Server 2025 Update 1", "left", 10),
        # Both 25-fix patches point left; this one is lifted a line so the two
        # labels stack rather than collide, and so it clears the right edge.
        ("Portal for ArcGIS Security 2025 Update 3 Patch",
         "Portal 2025 Update 3", "left", 34),
        ("Portal for ArcGIS Security 2026 Update 3 Patch",
         "Portal 2026 Update 3", "left", 8),
        ("Portal for ArcGIS Security 2024 Update 2 Patch",
         "Portal 2024 Update 2", "left", 8),
    ]
    for row_title, label, side, dy in annotations:
        row = df[df["title"] == row_title]
        if row.empty:
            continue
        r = row.iloc[0]
        extends_right = side == "right"
        ax.annotate(
            f"{label} · {int(r['security_bugs'])} fixes",
            xy=(r["date"], r["security_bugs"]),
            xytext=(16 if extends_right else -16, dy),
            textcoords="offset points", fontsize=8.5, color=t.text_secondary,
            ha="left" if extends_right else "right", va="bottom",
        )

    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 1.04), frameon=False,
              fontsize=9, labelcolor=t.text_secondary, ncol=4,
              handletextpad=0.4, columnspacing=1.4, scatterpoints=1)

    # Headline is the finding, not the encoding: before 2025 no single patch
    # carried more than 6 security fixes; from 2025 they reach 25.
    pre_2025_max = int(df[df["date"] < "2025-01-01"]["security_bugs"].max())
    peak = int(df["security_bugs"].max())
    head_bottom = titles(
        fig, t,
        f"Since 2025 a single patch has carried up to {peak} security fixes — "
        f"before that, never more than {pre_2025_max}",
        "Portal for ArcGIS and ArcGIS Server security patches, 2021–2026 YTD — "
        "release date vs. security-labeled fixes; dot area is proportional to the "
        "fix count",
        width=104,
    )

    foot_top = add_footer(
        fig, t,
        source="Esri Support patch pages (support.esri.com/patches-updates), scraped Aug 2026.",
        note="One dot per patch, limited to Portal for ArcGIS and ArcGIS Server "
             "(129 of the 141 security-labeled fixes) and to patches that introduced at "
             "least one. Only the security-labeled BUG-IDs each patch introduces are "
             "counted; cumulative “To avoid conflicts” re-lists of older fixes are "
             "excluded. Other products, and security patches listing no security-labeled "
             "BUG-ID, are covered in product_breakdown.png and bug_counts.csv. 2026 "
             "covers Jan 1 – Aug 18 only.",
        width=132,
    )
    fig.subplots_adjust(top=head_bottom - 0.055, bottom=foot_top + 0.055,
                        left=0.062, right=0.985)
    save(fig, t, "timeline.png")


def main() -> int:
    counts = pd.read_csv(COUNTS_CSV)
    print(f"Loaded {len(counts)} patch rows from {COUNTS_CSV.name}")
    for theme in (LIGHT, DARK):
        chart_patches_and_fixes_per_year(counts, theme)
        chart_product_breakdown(counts, theme)
        chart_timeline(counts, theme)
    print("All charts written to charts/ (light) and charts/dark/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
