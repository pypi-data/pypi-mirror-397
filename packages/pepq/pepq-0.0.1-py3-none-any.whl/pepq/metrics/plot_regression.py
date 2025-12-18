"""
pepq.metrics.plot_regression
============================

Public API for the regression report plot.

Example
-------

.. code-block:: python

    from pepq.metrics.plot_regression import plot_regression_report

    fig, axes = plot_regression_report(
        y_true=y_true,
        y_pred=y_pred,
        include=["pred_vs_true", "resid_hist", "qq"],
        layout=(1, 3),
        title="My regression report",
    )
    fig.show()
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ._core import basic_reg_stats, ensure_reg_arrays
from . import _panels as panels


_ALLOWED_PANELS = {
    "pred_vs_true",
    "resid_hist",
    "resid_vs_pred",
    "qq",
    "density",
    "tolerance",
    "interval_coverage",
    "pred_vs_true_in_domain",
    "resid_hist_in_domain",
}

_DEFAULT_TITLES: Dict[str, str] = {
    "pred_vs_true": "Predicted vs True",
    "resid_hist": "Residuals distribution",
    "resid_vs_pred": "Residuals vs Predicted",
    "qq": "Residuals QQ-plot",
    "density": "Marginal distributions",
    "tolerance": "Within-tolerance curve",
    "interval_coverage": "Prediction interval coverage",
    "pred_vs_true_in_domain": "Predicted vs True (in-domain)",
    "resid_hist_in_domain": "Residuals distribution (in-domain)",
}


@dataclass
class RegressionReport:
    """
    Build and render a multi-panel regression report figure.

    Mutator methods return ``self``; use properties to retrieve results.

    :param target_col: Column name for true values in DataFrame mode.
    :param y_pred_col: Column name for predicted values in DataFrame mode.
    :param y_lower_col: Column name for lower interval bounds in DataFrame mode.
    :param y_upper_col: Column name for upper interval bounds in DataFrame mode.
    """

    target_col: str = "target"
    y_pred_col: str = "y_pred"
    y_lower_col: str = "y_lower"
    y_upper_col: str = "y_upper"

    _y_true: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _y_pred: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _y_lower: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _y_upper: Optional[np.ndarray] = field(default=None, init=False, repr=False)

    _y_true_in: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _y_pred_in: Optional[np.ndarray] = field(default=None, init=False, repr=False)

    _fig: Optional[plt.Figure] = field(default=None, init=False, repr=False)
    _axes: List[plt.Axes] = field(default_factory=list, init=False, repr=False)

    def __repr__(self) -> str:
        fitted = self._y_true is not None and self._y_pred is not None
        status = "fitted" if fitted else "unfitted"
        n = None if self._y_true is None else int(self._y_true.size)
        return f"{type(self).__name__}([{status}], n={n})"

    # ------------------------------------------------------------------
    # Data setters
    # ------------------------------------------------------------------

    def from_dataframe(
        self,
        df: pd.DataFrame,
        *,
        target_col: Optional[str] = None,
        y_pred_col: Optional[str] = None,
        y_lower_col: Optional[str] = None,
        y_upper_col: Optional[str] = None,
    ) -> "RegressionReport":
        """
        Load data in DataFrame mode.

        :param df: Input DataFrame.
        :param target_col: Override for true column.
        :param y_pred_col: Override for pred column.
        :param y_lower_col: Override for lower interval column.
        :param y_upper_col: Override for upper interval column.
        :returns: self
        """
        tcol = target_col or self.target_col
        pcol = y_pred_col or self.y_pred_col
        lcol = y_lower_col or self.y_lower_col
        ucol = y_upper_col or self.y_upper_col

        if tcol not in df.columns:
            raise ValueError(f"target_col '{tcol}' not found in DataFrame.")
        if pcol not in df.columns:
            raise ValueError(f"y_pred_col '{pcol}' not found in DataFrame.")

        self._y_true = np.asarray(df[tcol].values, dtype=float).ravel()
        self._y_pred = np.asarray(df[pcol].values, dtype=float).ravel()

        self._y_lower = None
        self._y_upper = None
        if lcol in df.columns:
            self._y_lower = np.asarray(df[lcol].values, dtype=float).ravel()
        if ucol in df.columns:
            self._y_upper = np.asarray(df[ucol].values, dtype=float).ravel()

        self._invalidate_outputs()
        return self

    def from_arrays(
        self,
        *,
        y_true: Sequence,
        y_pred: Sequence,
        y_lower: Optional[Sequence] = None,
        y_upper: Optional[Sequence] = None,
    ) -> "RegressionReport":
        """
        Load data in array mode.

        :param y_true: True values.
        :param y_pred: Predicted values.
        :param y_lower: Optional lower interval bounds.
        :param y_upper: Optional upper interval bounds.
        :returns: self
        """
        self._y_true, self._y_pred = ensure_reg_arrays(y_true, y_pred)
        self._y_lower = (
            None if y_lower is None else np.asarray(y_lower, dtype=float).ravel()
        )
        self._y_upper = (
            None if y_upper is None else np.asarray(y_upper, dtype=float).ravel()
        )
        self._invalidate_outputs()
        return self

    def set_in_domain(
        self,
        *,
        y_true_in_domain: Sequence,
        y_pred_in_domain: Sequence,
    ) -> "RegressionReport":
        """
        Set in-domain subset arrays (for *_in_domain panels).

        :param y_true_in_domain: In-domain true values.
        :param y_pred_in_domain: In-domain predicted values.
        :returns: self
        """
        self._y_true_in, self._y_pred_in = ensure_reg_arrays(
            y_true_in_domain,
            y_pred_in_domain,
        )
        self._invalidate_outputs()
        return self

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------

    def plot(
        self,
        *,
        include: Optional[Sequence[str]] = None,
        include_titles: Optional[Sequence[Optional[str]]] = None,
        layout: Optional[Tuple[int, int]] = None,
        figsize: Tuple[float, float] = (10.0, 4.5),
        bins: int = 30,
        tolerances: Optional[Sequence[float]] = None,
        show_stats: bool = True,
        accent: str = "#0522A3",
        title: Optional[str] = None,
        dpi: int = 150,
        add_panel_letters: bool = True,
    ) -> "RegressionReport":
        """
        Render the regression report and store outputs in this instance.

        :param include: Panel names to include.
        :param include_titles: Optional per-panel titles aligned to include.
        :param layout: Optional (n_rows, n_cols).
        :param figsize: Figure size in inches.
        :param bins: Histogram bins for residuals.
        :param tolerances: Tolerance grid for tolerance panel.
        :param show_stats: Whether to show stats in pred_vs_true panels.
        :param accent: Accent color for primary marks.
        :param title: Optional overall title.
        :param dpi: Figure dpi.
        :param add_panel_letters: Add A–F labels to used axes.
        :returns: self
        """
        y_true, y_pred = self._require_xy()

        include_list = self._normalize_include(include)
        titles_list = self._normalize_titles(include_titles, include_list)

        self._validate_request(include_list)
        stats, stats_in = self._compute_stats(y_true, y_pred)

        n_rows, n_cols = self._resolve_layout(layout, len(include_list))
        rc = self._default_rc()

        with plt.rc_context(rc):
            fig, axes_all = self._create_figure(
                n_rows=n_rows,
                n_cols=n_cols,
                figsize=figsize,
                dpi=dpi,
            )
            axes_used = axes_all[: len(include_list)]

            drawers = self._panel_drawers(
                stats=stats,
                stats_in=stats_in,
                bins=bins,
                tolerances=tolerances,
                show_stats=show_stats,
                accent=accent,
            )
            self._render_panels(
                axes=axes_used,
                include=include_list,
                include_titles=titles_list,
                drawers=drawers,
            )
            self._finalize_figure(
                fig=fig,
                axes_all=axes_all,
                n_panels=len(include_list),
                title=title,
                add_panel_letters=add_panel_letters,
            )

        self._fig = fig
        self._axes = list(axes_used)
        return self

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def figure(self) -> plt.Figure:
        """
        Return the last rendered figure.

        :raises RuntimeError: If plot() was not called yet.
        """
        if self._fig is None:
            raise RuntimeError("No figure available. Call .plot(...) first.")
        return self._fig

    @property
    def axes(self) -> List[plt.Axes]:
        """
        Return the list of axes used for the last rendered figure.

        :raises RuntimeError: If plot() was not called yet.
        """
        if not self._axes:
            raise RuntimeError("No axes available. Call .plot(...) first.")
        return list(self._axes)

    # ------------------------------------------------------------------
    # Internals (small helpers to keep plot() simple)
    # ------------------------------------------------------------------

    def _invalidate_outputs(self) -> None:
        self._fig = None
        self._axes = []

    def _require_xy(self) -> Tuple[np.ndarray, np.ndarray]:
        if self._y_true is None or self._y_pred is None:
            raise RuntimeError(
                "No data set. Use from_dataframe(...) or from_arrays(...)."
            )
        if self._y_true.shape[0] != self._y_pred.shape[0]:
            raise ValueError("y_true and y_pred must have the same length.")
        return self._y_true, self._y_pred

    @staticmethod
    def _normalize_include(include: Optional[Sequence[str]]) -> List[str]:
        if include is None:
            return ["pred_vs_true", "resid_hist"]
        return [str(x) for x in include]

    @staticmethod
    def _normalize_titles(
        include_titles: Optional[Sequence[Optional[str]]],
        include_list: List[str],
    ) -> List[Optional[str]]:
        if include_titles is None:
            return [None] * len(include_list)

        titles = list(include_titles)
        if len(titles) < len(include_list):
            titles = titles + [None] * (len(include_list) - len(titles))
        return titles[: len(include_list)]

    def _validate_request(self, include_list: List[str]) -> None:
        unknown = [p for p in include_list if p not in _ALLOWED_PANELS]
        if unknown:
            raise ValueError(f"Unknown panel names in include: {unknown}")

        if "interval_coverage" in include_list:
            if self._y_lower is None or self._y_upper is None:
                raise ValueError(
                    "Panel 'interval_coverage' requested but y_lower/y_upper "
                    "are missing."
                )

        needs_in = any(p.endswith("_in_domain") for p in include_list)
        if needs_in and (self._y_true_in is None or self._y_pred_in is None):
            raise ValueError(
                "Panels with '_in_domain' requested but in-domain arrays are "
                "not set. Call set_in_domain(...)."
            )

    @staticmethod
    def _compute_stats(
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        stats = basic_reg_stats(y_true, y_pred)
        return stats, None

    def _compute_stats_in_domain(self) -> Optional[Dict[str, Any]]:
        if self._y_true_in is None or self._y_pred_in is None:
            return None
        return basic_reg_stats(self._y_true_in, self._y_pred_in)

    @staticmethod
    def _default_rc() -> Dict[str, Any]:
        return {
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "axes.edgecolor": "#111827",
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
        }

    @staticmethod
    def _flatten_axes(axes_grid) -> List[plt.Axes]:
        if isinstance(axes_grid, plt.Axes):
            return [axes_grid]
        return list(np.ravel(axes_grid))

    @staticmethod
    def _resolve_layout(
        layout: Optional[Tuple[int, int]],
        n_panels: int,
    ) -> Tuple[int, int]:
        if layout is not None:
            n_rows, n_cols = layout
            if n_rows <= 0 or n_cols <= 0:
                raise ValueError("layout must be positive (n_rows, n_cols).")
            if n_rows * n_cols < n_panels:
                raise ValueError(f"layout {layout} cannot fit {n_panels} panels.")
            return n_rows, n_cols

        # default 2×3
        n_rows, n_cols = 2, 3
        if n_panels > n_rows * n_cols:
            raise ValueError(
                f"Requested {n_panels} panels, but default layout fits at most 6. "
                "Pass layout=(n_rows, n_cols)."
            )
        return n_rows, n_cols

    def _create_figure(
        self,
        *,
        n_rows: int,
        n_cols: int,
        figsize: Tuple[float, float],
        dpi: int,
    ) -> Tuple[plt.Figure, List[plt.Axes]]:
        fig, axes_grid = plt.subplots(n_rows, n_cols, figsize=figsize, dpi=dpi)
        axes_all = self._flatten_axes(axes_grid)
        return fig, axes_all

    def _panel_drawers(
        self,
        *,
        stats: Dict[str, Any],
        stats_in: Optional[Dict[str, Any]],
        bins: int,
        tolerances: Optional[Sequence[float]],
        show_stats: bool,
        accent: str,
    ) -> Dict[str, Callable[[plt.Axes], None]]:
        y_true, y_pred = self._require_xy()
        stats_in_final = (
            self._compute_stats_in_domain() if stats_in is None else stats_in
        )

        def _pred_vs_true(ax: plt.Axes) -> None:
            panels.panel_pred_vs_true(
                ax,
                y_true,
                y_pred,
                stats,
                show_stats=show_stats,
                accent=accent,
            )

        def _resid_hist(ax: plt.Axes) -> None:
            panels.panel_residuals_hist(
                ax,
                y_true,
                y_pred,
                bins=bins,
                accent=accent,
            )

        def _resid_vs_pred(ax: plt.Axes) -> None:
            panels.panel_residuals_vs_pred(ax, y_true, y_pred, accent=accent)

        def _qq(ax: plt.Axes) -> None:
            panels.panel_qq(ax, y_true, y_pred)

        def _density(ax: plt.Axes) -> None:
            panels.panel_density(ax, y_true, y_pred)

        def _tolerance(ax: plt.Axes) -> None:
            panels.panel_tolerance_curve(
                ax,
                y_true,
                y_pred,
                tolerances=tolerances,
            )

        def _interval(ax: plt.Axes) -> None:
            assert self._y_lower is not None and self._y_upper is not None
            panels.panel_interval_coverage(ax, y_true, self._y_lower, self._y_upper)

        def _pred_vs_true_in(ax: plt.Axes) -> None:
            assert self._y_true_in is not None and self._y_pred_in is not None
            panels.panel_pred_vs_true(
                ax,
                self._y_true_in,
                self._y_pred_in,
                stats_in_final,
                show_stats=show_stats,
                accent=accent,
            )

        def _resid_hist_in(ax: plt.Axes) -> None:
            assert self._y_true_in is not None and self._y_pred_in is not None
            panels.panel_residuals_hist(
                ax,
                self._y_true_in,
                self._y_pred_in,
                bins=bins,
                accent=accent,
            )

        return {
            "pred_vs_true": _pred_vs_true,
            "resid_hist": _resid_hist,
            "resid_vs_pred": _resid_vs_pred,
            "qq": _qq,
            "density": _density,
            "tolerance": _tolerance,
            "interval_coverage": _interval,
            "pred_vs_true_in_domain": _pred_vs_true_in,
            "resid_hist_in_domain": _resid_hist_in,
        }

    @staticmethod
    def _panel_title(name: str, custom: Optional[str]) -> Optional[str]:
        if custom is not None and str(custom).strip():
            return str(custom)
        return _DEFAULT_TITLES.get(name)

    def _render_panels(
        self,
        *,
        axes: List[plt.Axes],
        include: List[str],
        include_titles: List[Optional[str]],
        drawers: Dict[str, Callable[[plt.Axes], None]],
    ) -> None:
        for i, name in enumerate(include):
            ax = axes[i]
            drawers[name](ax)

            t = self._panel_title(name, include_titles[i])
            if t:
                ax.set_title(t, pad=6)

    @staticmethod
    def _finalize_figure(
        *,
        fig: plt.Figure,
        axes_all: List[plt.Axes],
        n_panels: int,
        title: Optional[str],
        add_panel_letters: bool,
    ) -> None:
        # turn off unused axes
        for j in range(n_panels, len(axes_all)):
            axes_all[j].set_axis_off()

        if add_panel_letters:
            letters = ["A", "B", "C", "D", "E", "F"]
            for i, ax in enumerate(axes_all[:n_panels]):
                if i >= len(letters):
                    break
                ax.text(
                    0.0,
                    1.02,
                    letters[i],
                    transform=ax.transAxes,
                    ha="left",
                    va="bottom",
                    fontsize=12,
                    fontweight="bold",
                )

        if title:
            fig.suptitle(title, fontsize=12, y=1.02)

        fig.tight_layout()


def plot_regression_report(
    df: Optional[pd.DataFrame] = None,
    *,
    y_true: Optional[Sequence] = None,
    y_pred: Optional[Sequence] = None,
    y_lower: Optional[Sequence] = None,
    y_upper: Optional[Sequence] = None,
    target_col: str = "target",
    y_pred_col: str = "y_pred",
    y_lower_col: str = "y_lower",
    y_upper_col: str = "y_upper",
    include: Optional[Sequence[str]] = None,
    include_titles: Optional[Sequence[Optional[str]]] = None,
    layout: Optional[Tuple[int, int]] = None,
    figsize: Tuple[float, float] = (10.0, 4.5),
    bins: int = 30,
    tolerances: Optional[Sequence[float]] = None,
    show_stats: bool = True,
    accent: str = "#0522A3",
    title: Optional[str] = None,
    dpi: int = 150,
    y_true_in_domain: Optional[Sequence] = None,
    y_pred_in_domain: Optional[Sequence] = None,
    add_panel_letters: bool = True,
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """
    Convenience wrapper returning (fig, axes).

    :returns: (fig, axes) where axes are in the order of include.
    """
    rep = RegressionReport(
        target_col=target_col,
        y_pred_col=y_pred_col,
        y_lower_col=y_lower_col,
        y_upper_col=y_upper_col,
    )

    if df is not None:
        if y_true is not None or y_pred is not None:
            raise ValueError("When df is provided, y_true and y_pred must be None.")
        rep.from_dataframe(
            df,
            target_col=target_col,
            y_pred_col=y_pred_col,
            y_lower_col=y_lower_col,
            y_upper_col=y_upper_col,
        )
    else:
        if y_true is None or y_pred is None:
            raise ValueError("Provide either df or both y_true and y_pred.")
        rep.from_arrays(y_true=y_true, y_pred=y_pred, y_lower=y_lower, y_upper=y_upper)

    if (y_true_in_domain is not None) or (y_pred_in_domain is not None):
        if y_true_in_domain is None or y_pred_in_domain is None:
            raise ValueError(
                "Both y_true_in_domain and y_pred_in_domain must be provided."
            )
        rep.set_in_domain(
            y_true_in_domain=y_true_in_domain,
            y_pred_in_domain=y_pred_in_domain,
        )

    rep.plot(
        include=include,
        include_titles=include_titles,
        layout=layout,
        figsize=figsize,
        bins=bins,
        tolerances=tolerances,
        show_stats=show_stats,
        accent=accent,
        title=title,
        dpi=dpi,
        add_panel_letters=add_panel_letters,
    )
    return rep.figure, rep.axes
