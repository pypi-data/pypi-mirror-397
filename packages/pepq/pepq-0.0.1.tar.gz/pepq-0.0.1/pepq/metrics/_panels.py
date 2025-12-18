"""
pepq.metrics.regression._panels
===============================

Panel-drawing helpers for the regression report.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

import numpy as np
import matplotlib.pyplot as plt

from ._core import require_scipy

try:
    from scipy import stats as _scipy_stats
except Exception:  # pragma: no cover
    _scipy_stats = None


def panel_pred_vs_true(
    ax: plt.Axes,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    stats: Optional[Dict[str, Any]] = None,
    *,
    show_stats: bool = True,
    accent: str = "#FFB000",
    scatter_kwargs: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Panel: predicted vs true scatter with identity line and optional stats box.

    :param ax: Matplotlib axes.
    :param y_true: True values (1D array).
    :param y_pred: Predicted values (1D array).
    :param stats: Optional stats dict (from basic_reg_stats).
    :param show_stats: If True, display stats box.
    :param accent: Accent color (currently used only by default scatter styling).
    :param scatter_kwargs: Optional kwargs passed to ax.scatter().
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()

    scatter_kwargs = {} if scatter_kwargs is None else dict(scatter_kwargs)
    defaults = {
        "s": 18,
        "alpha": 0.55,
        "linewidths": 0.3,
        "edgecolors": "white",
        "color": accent,
    }
    for k, v in defaults.items():
        scatter_kwargs.setdefault(k, v)

    ax.scatter(y_true, y_pred, **scatter_kwargs)

    lo = float(np.nanmin([y_true.min(), y_pred.min()]))
    hi = float(np.nanmax([y_true.max(), y_pred.max()]))
    pad = 0.02 * (hi - lo if hi > lo else 1.0)
    lo, hi = lo - pad, hi + pad

    ax.plot(
        [lo, hi],
        [lo, hi],
        linestyle="--",
        color="#555555",
        linewidth=1.0,
        alpha=0.8,
    )
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)

    ax.set_xlabel("True")
    ax.set_ylabel("Predicted")

    if show_stats and stats is not None:
        txt = (
            f"$n$ = {stats['n']}\n"
            f"$r$ = {stats['r']:.3f}\n"
            f"$R^2$ = {stats['r2']:.3f}\n"
            f"MAE = {stats['mae']:.3f}\n"
            f"RMSE = {stats['rmse']:.3f}"
        )
        ax.text(
            0.97,
            0.03,
            txt,
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=8.5,
            bbox={
                "boxstyle": "round,pad=0.25",
                "facecolor": "white",
                "edgecolor": "none",
                "alpha": 0.85,
            },
        )

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def panel_residuals_hist(
    ax: plt.Axes,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    bins: int = 30,
    accent: str = "#FFB000",
    hist_kwargs: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Panel: residual histogram.

    :param ax: Matplotlib axes.
    :param y_true: True values.
    :param y_pred: Predicted values.
    :param bins: Number of histogram bins.
    :param accent: Histogram fill color.
    :param hist_kwargs: Optional kwargs passed to ax.hist().
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    resid = y_pred - y_true

    hist_kwargs = {} if hist_kwargs is None else dict(hist_kwargs)
    hist_kwargs.setdefault("alpha", 0.75)
    hist_kwargs.setdefault("edgecolor", "white")

    ax.hist(resid, bins=bins, color=accent, **hist_kwargs)
    ax.axvline(0.0, color="#333333", linestyle="--", linewidth=1.0)

    ax.set_xlabel("Residual (pred - true)")
    ax.set_ylabel("Count")

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def panel_residuals_vs_pred(
    ax: plt.Axes,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    accent: str = "#FFB000",
) -> None:
    """
    Panel: residuals vs predicted.

    :param ax: Matplotlib axes.
    :param y_true: True values.
    :param y_pred: Predicted values.
    :param accent: Scatter color.
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    resid = y_pred - y_true

    ax.scatter(
        y_pred,
        resid,
        s=16,
        alpha=0.55,
        linewidths=0.3,
        edgecolors="white",
        color=accent,
    )
    ax.axhline(0.0, color="#333333", linestyle="--", linewidth=1.0)

    ax.set_xlabel("Predicted")
    ax.set_ylabel("Residual")

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def panel_qq(
    ax: plt.Axes,
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> None:
    """
    Panel: QQ-plot of residuals vs normal.

    :param ax: Matplotlib axes.
    :param y_true: True values.
    :param y_pred: Predicted values.
    """
    require_scipy()
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    resid = y_pred - y_true

    osm, osr = _scipy_stats.probplot(resid, dist="norm", plot=None)
    theo_q = osm[0]
    sample_q = osm[1]

    ax.scatter(
        theo_q,
        sample_q,
        s=16,
        alpha=0.6,
        edgecolors="white",
        linewidths=0.3,
        color="#4C72B0",
    )

    lo = float(np.nanmin([theo_q.min(), sample_q.min()]))
    hi = float(np.nanmax([theo_q.max(), sample_q.max()]))
    ax.plot([lo, hi], [lo, hi], linestyle="--", color="#555555", linewidth=1.0)

    ax.set_xlabel("Theoretical quantiles")
    ax.set_ylabel("Sample quantiles")

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def panel_density(
    ax: plt.Axes,
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> None:
    """
    Panel: marginal distributions of true vs predicted (overlaid histograms).

    :param ax: Matplotlib axes.
    :param y_true: True values.
    :param y_pred: Predicted values.
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()

    lo = float(np.nanmin([y_true.min(), y_pred.min()]))
    hi = float(np.nanmax([y_true.max(), y_pred.max()]))
    bins = np.linspace(lo, hi, 30)

    ax.hist(
        y_true,
        bins=bins,
        density=True,
        alpha=0.45,
        label="True",
        color="#4C72B0",
        edgecolor="white",
        linewidth=0.3,
    )
    ax.hist(
        y_pred,
        bins=bins,
        density=True,
        alpha=0.45,
        label="Predicted",
        color="#DD8452",
        edgecolor="white",
        linewidth=0.3,
    )

    ax.set_xlabel("Value")
    ax.set_ylabel("Density")
    ax.legend(frameon=False)

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def panel_tolerance_curve(
    ax: plt.Axes,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    tolerances: Optional[Sequence[float]] = None,
) -> None:
    """
    Panel: within-tolerance curve vs |pred - true|.

    :param ax: Matplotlib axes.
    :param y_true: True values.
    :param y_pred: Predicted values.
    :param tolerances: Optional tolerance grid; auto-derived if None.
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    abs_err = np.abs(y_pred - y_true)

    if tolerances is None:
        max_err = float(np.nanpercentile(abs_err, 99.0))
        max_err = max(max_err, 1e-6)
        tolerances_arr = np.linspace(0.0, max_err, 40)
    else:
        tolerances_arr = np.asarray(list(tolerances), dtype=float)

    frac_within = np.array([(abs_err <= t).mean() for t in tolerances_arr], dtype=float)

    ax.plot(
        tolerances_arr,
        frac_within,
        marker="o",
        markersize=4,
        linestyle="-",
        linewidth=1.5,
        color="#4C72B0",
    )

    ax.set_xlabel("Tolerance (|pred - true|)")
    ax.set_ylabel("Fraction within tolerance")
    ax.set_ylim(0.0, 1.0)

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def panel_interval_coverage(
    ax: plt.Axes,
    y_true: np.ndarray,
    y_lower: np.ndarray,
    y_upper: np.ndarray,
) -> None:
    """
    Panel: interval width distribution + overall coverage annotation.

    :param ax: Matplotlib axes.
    :param y_true: True values.
    :param y_lower: Lower bounds.
    :param y_upper: Upper bounds.
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_lower = np.asarray(y_lower, dtype=float).ravel()
    y_upper = np.asarray(y_upper, dtype=float).ravel()

    width = y_upper - y_lower
    in_interval = (y_true >= y_lower) & (y_true <= y_upper)
    coverage = float(in_interval.mean())

    ax.hist(
        width,
        bins=30,
        alpha=0.75,
        edgecolor="white",
        color="#4C72B0",
    )
    ax.axvline(
        float(np.mean(width)),
        color="#DD8452",
        linestyle="--",
        linewidth=1.2,
        label=f"mean width = {np.mean(width):.3f}",
    )

    ax.set_xlabel("Interval width")
    ax.set_ylabel("Count")

    ax.text(
        0.97,
        0.95,
        f"Coverage = {coverage:.3f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=8.5,
        bbox={
            "boxstyle": "round,pad=0.25",
            "facecolor": "white",
            "edgecolor": "none",
            "alpha": 0.9,
        },
    )
    ax.legend(frameon=False, loc="upper left")

    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
