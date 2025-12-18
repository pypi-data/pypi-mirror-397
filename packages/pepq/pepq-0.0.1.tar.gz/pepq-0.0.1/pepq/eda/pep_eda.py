from __future__ import annotations

from typing import Any, Optional, Sequence, Tuple

import numpy as np
from sklearn.metrics import (
    roc_curve,
    auc,
    precision_recall_curve,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
)

import seaborn as sns
import matplotlib.pyplot as plt

from .base import BaseEDA


class PepEDA(BaseEDA):
    """
    EDA helper specialised for protein–peptide docking summaries.

    This subclass adds domain-oriented visualisations on top of
    :class:`pepq.eda.base.BaseEDA`, in particular a 2×2
    overview panel** and label-aware feature–target plots.

    Expected columns include, for example::

        prot_plddt, pep_plddt, PTM, PAE, iptm, composite_ptm,
        actifptm, label, dockq

    The interface is fluent: computation and plotting methods return
    :class:`PepEDA` and results are retrieved via properties on the
    base class (e.g. :pyattr:`figures`).

    Typical usage
    -------------

    Regression + label (e.g. DockQ + success/fail)::

        eda = (
            PepEDA(df, target_col="dockq", secondary_target_col="label")
            .compute_missing_summary()
            .compute_basic_stats()
            .compute_correlations(with_target_only=True)
        )

        # Optionally, attach model-based feature importances
        eda.set_feature_importance_from_model(fitted_rf)

        eda.plot_overview(top_k=6, figsize=(9.0, 7.0))
        eda.figures["overview"].savefig(
            "eda_overview.png", dpi=300, bbox_inches="tight"
        )

        # Label-aware plots
        eda.plot_label_violins()
        eda.plot_distributions(hue="label")
        eda.plot_pca(color="label")
        eda.plot_pairwise(
            features=eda._top_k_features_by_target_corr(6),
            kind="reg",
            hue="label",
            sample=1500,
        )
        eda.plot_corr_clustermap()
        eda.plot_hexbin(x="iptm", y="composite_ptm", c="dockq")

    Pure regression (no secondary label)::

        eda = (
            PepEDA(df, target_col="dockq")
            .compute_missing_summary()
            .compute_basic_stats()
            .compute_correlations(with_target_only=True)
        )
        eda.plot_overview(top_k=6)

    In the pure regression case (no ``secondary_target_col``), panel D of
    :meth:`plot_overview` will also display Pearson :math:`r`, :math:`R^2`
    and RMSE for the best-correlated feature vs. target.
    """

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _annotate_regression_stats(
        self,
        ax: plt.Axes,
        x: np.ndarray,
        y: np.ndarray,
        loc: str = "lower right",
        fontsize: float = 7.0,
    ) -> None:
        """
        Annotate an axes with Pearson r, R² and RMSE for (x, y).

        NaNs are dropped before fitting a simple linear model ``y = a x + b``.

        :param ax: Matplotlib axes to annotate.
        :type ax: matplotlib.axes.Axes
        :param x: 1D array of feature values.
        :type x: numpy.ndarray
        :param y: 1D array of target values.
        :type y: numpy.ndarray
        :param loc: Location of annotation box; currently supports
            ``"lower right"`` or ``"upper left"``.
        :type loc: str
        :param fontsize: Font size for annotation text.
        :type fontsize: float
        """
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        mask = np.isfinite(x) & np.isfinite(y)
        if mask.sum() <= 1:
            return

        xv = x[mask]
        yv = y[mask]

        # Correlation and simple linear fit
        r = float(np.corrcoef(xv, yv)[0, 1])
        r2 = r**2
        a, b = np.polyfit(xv, yv, 1)
        y_pred = a * xv + b
        rmse = float(np.sqrt(np.mean((yv - y_pred) ** 2)))

        txt = f"r = {r: .2f}\nR² = {r2: .2f}\nRMSE = {rmse: .2f}"

        if loc == "lower right":
            x_pos, y_pos = 0.97, 0.03
            ha, va = "right", "bottom"
        elif loc == "upper left":
            x_pos, y_pos = 0.03, 0.97
            ha, va = "left", "top"
        else:
            x_pos, y_pos = 0.97, 0.03
            ha, va = "right", "bottom"

        ax.text(
            x_pos,
            y_pos,
            txt,
            transform=ax.transAxes,
            ha=ha,
            va=va,
            fontsize=fontsize,
            bbox={
                "boxstyle": "round,pad=0.2",
                "facecolor": "white",
                "alpha": 0.7,
                "edgecolor": "none",
            },
        )

    # ------------------------------------------------------------------
    # Label-aware plots
    # ------------------------------------------------------------------
    def plot_feature_target_grid(
        self,
        top_k: int = 4,
        show_stats: bool = True,
    ) -> "PepEDA":
        """
        Plot a grid of feature–target relationships for the top-k features.

        - Continuous target: scatter + LOWESS regression line, with optional
          overlay of Pearson correlation, R² and RMSE.
        - Classification target: boxplot + jitter overlay.

        :param top_k: Number of features to show.
        :type top_k: int
        :param show_stats: Whether to display correlation / R² / RMSE for
            continuous targets in a small annotation box.
        :type show_stats: bool
        :return: Self for fluent chaining.
        :rtype: PepEDA
        """
        if self.target_col is None or self.target_col not in self.df.columns:
            return self

        feats = self._top_k_features_by_target_corr(top_k)
        if not feats:
            feats = self._get_numeric_features()[:top_k]
        if not feats:
            return self

        is_class = self._is_classification_target()
        target = self.target_col

        n = len(feats)
        # Layout: up to 2 cols for <=4, then 3 cols for more
        if n <= 2:
            n_cols = n
        elif n <= 4:
            n_cols = 2
        else:
            n_cols = 3
        n_rows = int(np.ceil(n / n_cols))

        fig, axes = plt.subplots(
            n_rows,
            n_cols,
            figsize=(3.2 * n_cols, 2.6 * n_rows),
        )
        axes = np.atleast_1d(axes).flatten()

        for ax, feat in zip(axes, feats):
            x = self.df[feat]
            y = self.df[target]

            if is_class:
                sns.boxplot(
                    data=self.df,
                    x=target,
                    y=feat,
                    ax=ax,
                    color=self._muted_fill,
                    linewidth=0.7,
                    fliersize=0,
                )
                sns.stripplot(
                    data=self.df,
                    x=target,
                    y=feat,
                    ax=ax,
                    color=self._primary_color,
                    size=2.5,
                    alpha=0.6,
                )
                ax.set_xlabel(target)
                ax.set_ylabel(feat)
            else:
                sns.regplot(
                    data=self.df,
                    x=feat,
                    y=target,
                    ax=ax,
                    scatter_kws={
                        "s": 10,
                        "alpha": 0.5,
                        "color": self._primary_color,
                    },
                    line_kws={"lw": 1.2, "color": self._accent_color},
                    lowess=True,
                )
                ax.set_xlabel(feat)
                ax.set_ylabel(target)

                if show_stats:
                    self._annotate_regression_stats(
                        ax,
                        x.to_numpy(),
                        y.to_numpy(),
                        loc="lower right",
                        fontsize=7.0,
                    )

            ax.set_title(f"{feat} vs {target}", pad=4)

        for ax in axes[len(feats) :]:  # noqa
            ax.axis("off")

        fig.tight_layout()
        self._store_figure("feature_target_grid", fig)
        return self

    def plot_label_violins(
        self,
        features: Optional[Sequence[str]] = None,
        label_col: Optional[str] = None,
    ) -> "PepEDA":
        """
        Plot violin + strip plots for a categorical label (e.g. ``label``).

        Unlike :meth:`plot_feature_target_grid`, this method does not use
        :pyattr:`target_col`; instead it focuses on a label column which
        can be supplied explicitly or inferred via :meth:`_get_label_column`.

        This combines naturally with other label-aware methods such as
        :meth:`plot_distributions`, :meth:`plot_pca`,
        :meth:`plot_pairwise`, and :meth:`plot_hexbin`.

        :param features: Subset of numeric features to plot. If ``None``,
            all numeric features are used.
        :type features: Optional[Sequence[str]]
        :param label_col: Column name to use as label (x-axis). If ``None``,
            :meth:`_get_label_column` is used to choose a suitable column.
        :type label_col: Optional[str]
        :return: Self for fluent chaining.
        :rtype: PepEDA
        """
        label_col = label_col or self._get_label_column()
        if label_col is None or label_col not in self.df.columns:
            return self

        feats = list(features) if features is not None else self._get_numeric_features()
        if not feats:
            return self

        n = len(feats)
        n_cols = 3 if n > 2 else n
        n_rows = int(np.ceil(n / n_cols))

        fig, axes = plt.subplots(
            n_rows,
            n_cols,
            figsize=(3.0 * n_cols, 2.4 * n_rows),
        )
        axes = np.atleast_1d(axes).flatten()

        for ax, feat in zip(axes, feats):
            sns.violinplot(
                data=self.df,
                x=label_col,
                y=feat,
                ax=ax,
                inner="quartile",
                cut=0,
                linewidth=0.7,
                color=self._muted_fill,
            )
            sns.stripplot(
                data=self.df,
                x=label_col,
                y=feat,
                ax=ax,
                size=2.0,
                alpha=0.5,
                color=self._primary_color,
            )
            ax.set_title(feat, pad=4)
            ax.set_xlabel(label_col)
            ax.set_ylabel(None)

        for ax in axes[len(feats) :]:  # noqa
            ax.axis("off")

        fig.tight_layout()
        self._store_figure("label_violins", fig)
        return self

    # ------------------------------------------------------------------
    # Overview (2×2 or 2×3, panels labelled A–F)
    # ------------------------------------------------------------------
    # ------------------------------------------------------------------
    # Overview panel helpers (refactored to reduce complexity)
    # ------------------------------------------------------------------
    def _make_overview_figure(self, layout: str, figsize: Tuple[float, float]):
        if layout == "2x2":
            fig, axes = plt.subplots(
                2,
                2,
                figsize=figsize,
                gridspec_kw={
                    "height_ratios": [1.0, 1.0],
                    "wspace": 0.45,
                    "hspace": 0.55,
                },
            )
            axes = axes.flatten()
            axA, axB, axC, axD = axes
            axE = axF = None
        else:
            fig, axes = plt.subplots(
                2,
                3,
                figsize=figsize,
                gridspec_kw={
                    "height_ratios": [1.0, 1.0],
                    "wspace": 0.45,
                    "hspace": 0.55,
                },
            )
            axes = axes.flatten()
            axA, axB, axC, axD, axE, axF = axes
        return fig, (axA, axB, axC, axD, axE, axF)

    def _panel_A_feature_kdes(self, ax, feats, standardize):
        plot_df = self.df[feats].dropna()
        if standardize and not plot_df.empty:
            plot_df = (plot_df - plot_df.mean()) / plot_df.std(ddof=0)
            x_label = "Standardised value (z-score)"
        else:
            x_label = "Value"
        for feat in feats:
            if feat not in plot_df.columns:
                continue
            sns.kdeplot(plot_df[feat], ax=ax, lw=1.4, fill=False, label=feat)
        ax.set_xlabel(x_label)
        ax.set_ylabel("Density")
        if len(feats) > 1:
            ax.legend(frameon=False, fontsize=7)
        self._add_panel_label(ax, "A")

    def _panel_B_corr_heatmap(self, ax, feats, annot_corr):
        corr = self.corr_matrix
        if corr is None or corr.empty:
            ax.axis("off")
            self._add_panel_label(ax, "B")
            return
        cols = list(
            dict.fromkeys(
                feats + ([self.target_col] if self.target_col in corr.columns else [])
            )
        )
        cols = [c for c in cols if c in corr.columns]
        corr_sub = corr.loc[cols, cols] if cols else corr
        mask = np.tril(np.ones_like(corr_sub, dtype=bool))
        sns.heatmap(
            corr_sub,
            mask=mask,
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            center=0,
            square=True,
            linewidths=0.4,
            cbar_kws={"shrink": 0.7, "label": "r"},
            annot=annot_corr,
            fmt=".2f" if annot_corr else "",
            ax=ax,
        )
        self._add_panel_label(ax, "B")

    def _panel_C_importance(self, ax, top_k):
        if self.feature_importance is not None and not self.feature_importance.empty:
            imp = (
                self.feature_importance.copy()
                .rename("importance")
                .to_frame()
                .sort_values("importance", ascending=True)
            )
            imp = imp.tail(top_k)
            sns.barplot(
                data=imp,
                x="importance",
                y=imp.index,
                ax=ax,
                color=self._primary_color,
                orient="h",
            )
            ax.set_xlabel("Feature importance")
            ax.set_ylabel("")
            self._add_panel_label(ax, "C")
            return

        if self.target_correlations is not None:
            feature_list = self._get_numeric_features()
            corr_series = self.target_correlations.reindex(feature_list).dropna()
            if not corr_series.empty:
                corr_df = (
                    corr_series.rename("r")
                    .to_frame()
                    .assign(abs_r=lambda d: d["r"].abs())
                    .sort_values("abs_r", ascending=True)
                )
                corr_df = corr_df.tail(top_k)
                sns.barplot(
                    data=corr_df,
                    x="abs_r",
                    y=corr_df.index,
                    ax=ax,
                    color=self._primary_color,
                    orient="h",
                )
                ax.set_xlabel("|r(feature, target)|")
                ax.set_ylabel("")
                self._add_panel_label(ax, "C")
                return

        ax.axis("off")
        self._add_panel_label(ax, "C")

    def _panel_D_best_vs_target(self, ax, feats, label_col, secondary):
        target = self.target_col
        if not target or target not in self.df.columns:
            ax.axis("off")
            self._add_panel_label(ax, "D")
            return

        best_feat = feats[0]
        cols_bt = [c for c in (best_feat, target) if c in self.df.columns]
        plot_df2 = self.df[cols_bt].dropna()
        if label_col and label_col in self.df.columns:
            plot_df2[label_col] = self.df.loc[plot_df2.index, label_col]

        if np.issubdtype(self.df[target].dtype, np.number) and not plot_df2.empty:
            if label_col and label_col in plot_df2.columns:
                sns.scatterplot(
                    data=plot_df2,
                    x=best_feat,
                    y=target,
                    hue=label_col,
                    ax=ax,
                    s=12,
                    alpha=0.7,
                )
                sns.regplot(
                    data=plot_df2,
                    x=best_feat,
                    y=target,
                    scatter=False,
                    ax=ax,
                    line_kws={"lw": 1.4, "color": self._accent_color},
                    lowess=True,
                )
            else:
                sns.regplot(
                    data=plot_df2,
                    x=best_feat,
                    y=target,
                    ax=ax,
                    scatter_kws={"s": 12, "alpha": 0.6},
                    line_kws={"lw": 1.4, "color": self._accent_color},
                    lowess=True,
                )

            if secondary is None:
                self._annotate_regression_stats(
                    ax,
                    plot_df2[best_feat].to_numpy(),
                    plot_df2[target].to_numpy(),
                    loc="lower right",
                    fontsize=7.0,
                )
            ax.set_xlabel(best_feat)
            ax.set_ylabel(target)
        else:
            ax.axis("off")
        self._add_panel_label(ax, "D")

    def _panel_E_target_dist(self, ax):
        target = self.target_col
        if not target or target not in self.df.columns:
            ax.axis("off")
            self._add_panel_label(ax, "E")
            return
        target_vals = self.df[target].dropna()
        if np.issubdtype(target_vals.dtype, np.number) and not target_vals.empty:
            sns.histplot(
                target_vals,
                bins=40,
                kde=True,
                stat="density",
                color=self._primary_color,
                alpha=0.7,
                edgecolor="white",
                linewidth=0.3,
                ax=ax,
            )
            ax.set_xlabel(target)
            ax.set_ylabel("Density")
        else:
            ax.axis("off")
        self._add_panel_label(ax, "E")

    def _panel_F_target_vs_label_or_second(self, ax, feats, label_col):
        target = self.target_col
        if label_col and label_col in self.df.columns and target in self.df.columns:
            sns.violinplot(
                data=self.df,
                x=label_col,
                y=target,
                ax=ax,
                inner="quartile",
                cut=0,
                linewidth=0.7,
                color=self._muted_fill,
            )
            sns.stripplot(
                data=self.df,
                x=label_col,
                y=target,
                ax=ax,
                size=2.0,
                alpha=0.5,
                color=self._primary_color,
            )
            ax.set_xlabel(label_col)
            ax.set_ylabel(target)
            self._add_panel_label(ax, "F")
            return

        # fallback to second-best feature vs target
        if len(feats) > 1 and target and target in self.df.columns:
            second_feat = feats[1]
            cols_2 = [c for c in (second_feat, target) if c in self.df.columns]
            plot_df3 = self.df[cols_2].dropna()
            if np.issubdtype(self.df[target].dtype, np.number) and not plot_df3.empty:
                sns.regplot(
                    data=plot_df3,
                    x=second_feat,
                    y=target,
                    ax=ax,
                    scatter_kws={"s": 10, "alpha": 0.6},
                    line_kws={"lw": 1.2, "color": self._accent_color},
                    lowess=True,
                )
                ax.set_xlabel(second_feat)
                ax.set_ylabel(target)
                self._add_panel_label(ax, "F")
                return

        ax.axis("off")
        self._add_panel_label(ax, "F")

    # ------------------------------------------------------------------
    # Refactored plot_overview (uses the small helpers above)
    # ------------------------------------------------------------------
    def plot_overview(
        self,
        top_k: int = 4,
        standardize: bool = True,
        annot_corr: bool = False,
        figsize: Tuple[float, float] = (8.0, 6.0),
        layout: str = "2x2",
    ) -> "PepEDA":
        """
        Generate a compact, overview figure.

        Refactored to reduce cyclomatic complexity by delegating panels
        to small helper methods.
        """
        layout = layout.lower()
        if layout not in {"2x2", "2x3"}:
            raise ValueError("Unsupported layout; use '2x2' or '2x3'.")

        if self.corr_matrix is None or self.target_correlations is None:
            self.compute_correlations(with_target_only=True)

        feats = self._top_k_features_by_target_corr(top_k)
        if not feats:
            feats = self._get_numeric_features()[:top_k]
        if not feats:
            return self

        label_col = self._get_label_column()
        secondary = getattr(self, "secondary_target_col", None)

        fig, (axA, axB, axC, axD, axE, axF) = self._make_overview_figure(
            layout, figsize
        )

        # Panel A
        self._panel_A_feature_kdes(axA, feats, standardize)

        # Panel B
        self._panel_B_corr_heatmap(axB, feats, annot_corr)

        # Panel C
        self._panel_C_importance(axC, top_k)

        # Panel D
        self._panel_D_best_vs_target(axD, feats, label_col, secondary)

        # Panels E, F (only in 2x3)
        if layout == "2x3":
            self._panel_E_target_dist(axE)
            self._panel_F_target_vs_label_or_second(axF, feats, label_col)

        fig.tight_layout()
        self._store_figure("overview", fig)
        return self

    def plot_residuals(
        self,
        model: Any,
        features: Optional[Sequence[str]] = None,
        figsize: Tuple[float, float] = (8.0, 3.5),
    ) -> "PepEDA":
        """
        Plot residual diagnostics for a regression model on the current data.

        Two panels are shown:

        - predicted vs residuals (bias / heteroscedasticity),
        - histogram of residuals.

        :param model: Fitted scikit-learn-style model exposing ``predict``.
        :type model: Any
        :param features: Feature columns to use. If ``None``, all numeric
            features inferred by :meth:`BaseEDA._get_numeric_features` are used.
        :type features: Optional[Sequence[str]]
        :param figsize: Figure size in inches ``(width, height)``.
        :type figsize: Tuple[float, float]
        :return: Self for fluent chaining.
        :rtype: PepEDA
        """
        if self.target_col is None or self.target_col not in self.df.columns:
            return self

        feats = list(features) if features is not None else self._get_numeric_features()
        if not feats:
            return self

        X = self.df[feats].values
        y = self.df[self.target_col].values
        y_pred = model.predict(X)

        residuals = y - y_pred

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        ax1.scatter(y_pred, residuals, s=10, alpha=0.6, color=self._primary_color)
        ax1.axhline(0.0, color="black", linewidth=0.8, linestyle="--")
        ax1.set_xlabel("Predicted")
        ax1.set_ylabel("Residual (y - ŷ)")
        ax1.set_title("Residuals vs predicted", pad=6)

        sns.histplot(
            residuals,
            bins=40,
            kde=True,
            stat="density",
            color=self._primary_color,
            alpha=0.7,
            edgecolor="white",
            linewidth=0.3,
            ax=ax2,
        )
        ax2.set_xlabel("Residual")
        ax2.set_ylabel("Density")
        ax2.set_title("Residual distribution", pad=6)

        fig.tight_layout()
        self._store_figure("residuals", fig)
        return self

    def plot_enrichment(
        self,
        y_true_col: str,
        score_col: str,
        top_fracs: Sequence[float] = (0.01, 0.05, 0.10),
        figsize: Tuple[float, float] = (5.0, 4.0),
    ) -> "PepEDA":
        """
        Plot an enrichment / accumulation curve for ranking performance.

        The curve shows the fraction of positives recovered as a function
        of the screened fraction of the library (sorted by score). Enrichment
        factors at selected top fractions are annotated.

        :param y_true_col: Column with binary ground-truth labels (0/1).
        :type y_true_col: str
        :param score_col: Column with ranking scores (higher = better).
        :type score_col: str
        :param top_fracs: Fractions of the dataset (e.g. 0.01, 0.05, 0.10)
            at which enrichment factors are computed.
        :type top_fracs: Sequence[float]
        :param figsize: Figure size in inches ``(width, height)``.
        :type figsize: Tuple[float, float]
        :return: Self for fluent chaining.
        :rtype: PepEDA
        """
        if y_true_col not in self.df.columns or score_col not in self.df.columns:
            return self

        df = self.df[[y_true_col, score_col]].dropna()
        if df.empty:
            return self

        # ensure binary labels 0/1
        y_true = df[y_true_col].astype(int).values
        scores = df[score_col].values

        # sort by descending score
        order = np.argsort(-scores)
        y_true_sorted = y_true[order]

        n = len(y_true_sorted)
        cum_pos = np.cumsum(y_true_sorted)
        total_pos = y_true_sorted.sum()
        if total_pos == 0:
            return self

        frac_screened = np.arange(1, n + 1) / float(n)
        frac_recalled = cum_pos / float(total_pos)

        # compute enrichment factors at requested fractions
        ef_lines = []
        for f in top_fracs:
            if f <= 0 or f > 1:
                continue
            idx = max(1, int(np.round(f * n)))
            recall_at_f = frac_recalled[idx - 1]
            ef = recall_at_f / f
            ef_lines.append((f, ef))

        fig, ax = plt.subplots(figsize=figsize)
        ax.plot(
            frac_screened,
            frac_recalled,
            label="Model",
            color=self._primary_color,
            lw=1.5,
        )
        ax.plot(
            frac_screened,
            frac_screened,
            label="Random",
            color=self._muted_gray,
            lw=1.0,
            linestyle="--",
        )

        for f, ef in ef_lines:
            ax.axvline(f, color="#BBBBBB", lw=0.8, linestyle=":")
            ax.text(
                f,
                0.05,
                f"EF@{int(100*f)}% = {ef:.1f}",
                rotation=90,
                va="bottom",
                ha="right",
                fontsize=7,
            )

        ax.set_xlabel("Fraction of library screened")
        ax.set_ylabel("Fraction of positives recovered")
        ax.set_title("Enrichment curve", pad=6)
        ax.legend(frameon=False)

        fig.tight_layout()
        self._store_figure("enrichment", fig)
        return self

    def plot_roc_pr(
        self,
        y_true_col: str,
        score_col: str,
        figsize: Tuple[float, float] = (10.0, 4.0),
    ) -> "PepEDA":
        """
        Plot ROC and Precision–Recall curves for a binary classifier.

        :param y_true_col: Column with binary ground-truth labels (0/1).
        :type y_true_col: str
        :param score_col: Column with predicted scores or probabilities
            (higher = more likely positive).
        :type score_col: str
        :param figsize: Figure size in inches ``(width, height)``.
        :type figsize: Tuple[float, float]
        :return: Self for fluent chaining.
        :rtype: PepEDA
        """
        if y_true_col not in self.df.columns or score_col not in self.df.columns:
            return self

        df = self.df[[y_true_col, score_col]].dropna()
        if df.empty:
            return self

        y_true = df[y_true_col].astype(int).values
        scores = df[score_col].values

        fpr, tpr, _ = roc_curve(y_true, scores)
        roc_auc = auc(fpr, tpr)

        precision, recall, _ = precision_recall_curve(y_true, scores)
        ap = average_precision_score(y_true, scores)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # ROC
        ax1.plot(
            fpr, tpr, color=self._primary_color, lw=1.5, label=f"AUC = {roc_auc:.3f}"
        )
        ax1.plot([0, 1], [0, 1], color=self._muted_gray, lw=1.0, linestyle="--")
        ax1.set_xlabel("False positive rate")
        ax1.set_ylabel("True positive rate")
        ax1.set_title("ROC curve", pad=6)
        ax1.legend(frameon=False)

        # PR
        ax2.plot(
            recall, precision, color=self._primary_color, lw=1.5, label=f"AP = {ap:.3f}"
        )
        ax2.set_xlabel("Recall")
        ax2.set_ylabel("Precision")
        ax2.set_title("Precision–Recall curve", pad=6)
        ax2.legend(frameon=False)

        fig.tight_layout()
        self._store_figure("roc_pr", fig)
        return self

    def plot_threshold_metrics(
        self,
        y_true_col: str,
        score_col: str,
        metrics: Sequence[str] = ("precision", "recall", "f1"),
        n_points: int = 50,
        figsize: Tuple[float, float] = (6.0, 4.0),
    ) -> "PepEDA":
        """
        Plot classifier metrics as a function of decision threshold.

        :param y_true_col: Column with binary ground-truth labels (0/1).
        :type y_true_col: str
        :param score_col: Column with predicted scores or probabilities
            (higher = more likely positive).
        :type score_col: str
        :param metrics: Sequence of metric names to plot. Supported:
            ``"precision"``, ``"recall"``, ``"f1"``.
        :type metrics: Sequence[str]
        :param n_points: Number of thresholds to evaluate between min and max
            observed scores.
        :type n_points: int
        :param figsize: Figure size in inches ``(width, height)``.
        :type figsize: Tuple[float, float]
        :return: Self for fluent chaining.
        :rtype: PepEDA
        """
        if y_true_col not in self.df.columns or score_col not in self.df.columns:
            return self

        df = self.df[[y_true_col, score_col]].dropna()
        if df.empty:
            return self

        y_true = df[y_true_col].astype(int).values
        scores = df[score_col].values

        thr_vals = np.linspace(scores.min(), scores.max(), n_points)
        curves = {m: [] for m in metrics}

        for thr in thr_vals:
            y_pred = (scores >= thr).astype(int)
            if "precision" in metrics:
                curves["precision"].append(
                    precision_score(y_true, y_pred, zero_division=0)
                )
            if "recall" in metrics:
                curves["recall"].append(recall_score(y_true, y_pred, zero_division=0))
            if "f1" in metrics:
                curves["f1"].append(f1_score(y_true, y_pred, zero_division=0))

        fig, ax = plt.subplots(figsize=figsize)
        for m in metrics:
            ax.plot(thr_vals, curves[m], label=m)

        ax.set_xlabel("Decision threshold")
        ax.set_ylabel("Metric value")
        ax.set_ylim(0.0, 1.05)
        ax.set_title("Threshold-dependent metrics", pad=6)
        ax.legend(frameon=False)

        fig.tight_layout()
        self._store_figure("threshold_metrics", fig)
        return self

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover - simple convenience
        n = len(self.df) if getattr(self, "df", None) is not None else "?"
        tgt = getattr(self, "target_col", None)
        sec = getattr(self, "secondary_target_col", None)
        return (
            f"{self.__class__.__name__}(n={n}, "
            f"target={tgt!r}, secondary_target={sec!r})"
        )
