"""
pepq.metrics.plot_classification
--------------------------------

Lightweight plotting utilities for classification diagnostics.

This file is a slightly refactored version of the original module.
Key changes:
- Reduced complexity of `plot_classification_report` by moving validation
  and panel-selection logic to small helpers.
- All lines <= 100 characters to satisfy E501.
- Behaviour and visual defaults preserved.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (
    confusion_matrix,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    average_precision_score,
)
from sklearn.calibration import calibration_curve

# Colors
COLOR_NEG = "#0B4F6C"
COLOR_POS = "#FF6B6B"
ACCENT = "#FFB000"
COLOR_ROC = "#225E8E"
COLOR_PR = "#1E9A82"
COLOR_BASELINE = "#9CA3AF"


# -------------------------
# Input helpers
# -------------------------
def _unpack_inputs(
    df: Optional[pd.DataFrame],
    *,
    y_true: Optional[Sequence] = None,
    y_pred: Optional[Sequence] = None,
    y_proba: Optional[Sequence] = None,
    label_col: str = "label",
    y_pred_col: Optional[str] = None,
    y_proba_col: Optional[str] = None,
) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Normalize inputs: DataFrame mode or array mode -> numpy arrays.
    """
    if df is not None:
        if label_col not in df.columns:
            raise ValueError(f"Label column '{label_col}' not found in DataFrame.")
        y_true_arr = np.asarray(df[label_col].values)
        y_pred_arr = None if y_pred_col is None else np.asarray(df[y_pred_col].values)
        y_proba_arr = (
            None
            if y_proba_col is None
            else np.asarray(df[y_proba_col].values, dtype=float)
        )
        return y_true_arr, y_pred_arr, y_proba_arr

    if y_true is None:
        raise ValueError("y_true must be provided in array mode.")
    y_true_arr = np.asarray(y_true)
    y_pred_arr = None if y_pred is None else np.asarray(y_pred)
    y_proba_arr = None if y_proba is None else np.asarray(y_proba, dtype=float)
    return y_true_arr, y_pred_arr, y_proba_arr


def _positive_score_from_proba(y_proba: np.ndarray) -> np.ndarray:
    """
    Return 1D positive-class scores from y_proba.
    """
    arr = np.asarray(y_proba)
    if arr.ndim == 1:
        return arr.ravel()
    if arr.ndim == 2:
        if arr.shape[1] == 2:
            return arr[:, 1]
        raise ValueError(
            "y_proba has more than 2 columns: pass a 1D positive-score array."
        )
    raise ValueError(f"Unsupported y_proba shape: {arr.shape}")


# -------------------------
# Panel drawing helpers
# -------------------------
def _draw_confusion(
    ax: plt.Axes,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    *,
    normalize: Optional[str] = None,
    class_names: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
) -> None:
    cm = confusion_matrix(y_true, y_pred, normalize=normalize)
    cmap = plt.cm.Blues
    im = ax.imshow(cm, interpolation="nearest", cmap=cmap, aspect="auto")
    n = cm.shape[0]
    if class_names is None:
        class_names = [str(i) for i in range(n)]
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_xticklabels(class_names)
    ax.set_yticklabels(class_names)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title or "Confusion matrix")
    ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=2)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fmt = ".2f" if normalize else "d"
    thresh = cm.max() / 2.0 if cm.size else 0.0
    for i in range(n):
        for j in range(n):
            ax.text(
                j,
                i,
                format(cm[i, j], fmt),
                ha="center",
                va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontsize=12,
                fontweight="bold",
            )
    plt.colorbar(im, ax=ax, fraction=0.05, pad=0.02)


def _draw_score_hist(
    ax: plt.Axes,
    y_true: np.ndarray,
    scores: np.ndarray,
    *,
    bins: int = 20,
    title: Optional[str] = None,
) -> None:
    mask_pos = np.asarray(y_true) == 1
    mask_neg = ~mask_pos
    ax.hist(
        scores[mask_neg],
        bins=bins,
        range=(0, 1),
        density=True,
        alpha=0.65,
        color=COLOR_NEG,
        label="0",
        edgecolor="none",
    )
    ax.hist(
        scores[mask_pos],
        bins=bins,
        range=(0, 1),
        density=True,
        alpha=0.65,
        color=COLOR_POS,
        label="1",
        edgecolor="none",
    )
    ax.set_xlabel("Predicted probability (class 1)")
    ax.set_ylabel("Density")
    ax.set_title(title or "Score distribution by true class")
    ax.legend(frameon=False, title="label")


def _draw_calibration(
    ax: plt.Axes,
    y_true: np.ndarray,
    scores: np.ndarray,
    *,
    n_bins: int = 10,
    title: Optional[str] = None,
) -> None:
    prob_true, prob_pred = calibration_curve(
        y_true, scores, n_bins=n_bins, strategy="uniform"
    )
    ax.plot(prob_pred, prob_true, marker="o", linewidth=1.5, color=COLOR_ROC)
    ax.plot([0, 1], [0, 1], linestyle="--", color=COLOR_BASELINE, linewidth=1.2)
    ax.set_xlabel("Predicted probability")
    ax.set_ylabel("Observed frequency")
    ax.set_title(title or "Calibration curve")


def _draw_roc(
    ax: plt.Axes,
    y_true: np.ndarray,
    scores: np.ndarray,
    *,
    color: str = COLOR_ROC,
    title: Optional[str] = None,
) -> None:
    fpr, tpr, _ = roc_curve(y_true, scores)
    auc = roc_auc_score(y_true, scores)
    ax.plot(fpr, tpr, lw=2, color=color, label=f"Model (AUC = {auc:.3f})")
    ax.fill_between(fpr, tpr, alpha=0.12, color=color, step="pre")
    ax.plot([0, 1], [0, 1], linestyle="--", color=COLOR_BASELINE, linewidth=1.25)
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_title(title or "ROC curve")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.05)
    ax.legend(loc="lower right", frameon=False)


def _draw_pr(
    ax: plt.Axes,
    y_true: np.ndarray,
    scores: np.ndarray,
    *,
    color: str = COLOR_PR,
    pos_label: int = 1,
    title: Optional[str] = None,
) -> None:
    precision, recall, _ = precision_recall_curve(y_true, scores)
    ap = average_precision_score(y_true, scores, pos_label=pos_label)
    pos_rate = float(np.mean(np.asarray(y_true) == pos_label))
    ax.plot(recall, precision, lw=2, color=color, label=f"Model (AP = {ap:.3f})")
    ax.fill_between(recall, precision, alpha=0.12, color=color, step="pre")
    ax.hlines(
        pos_rate,
        0.0,
        1.0,
        linestyle="--",
        color=COLOR_BASELINE,
        linewidth=1.2,
    )
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title(title or "Precision–Recall curve")
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.05)
    ax.legend(loc="lower right", frameon=False)


# -------------------------
# plot_classification_report
# -------------------------
def _validate_and_prepare_panels(
    include: Optional[Sequence[str]],
    include_titles: Optional[Sequence[str]],
) -> Tuple[List[str], Optional[List[str]]]:
    allowed = {"confusion", "score_hist", "calibration", "roc", "pr"}
    if include is None:
        include_list = ["confusion", "score_hist", "roc", "pr"]
    else:
        include_list = list(include)

    unknown = [p for p in include_list if p not in allowed]
    if unknown:
        raise ValueError(f"Unknown panels requested: {unknown}")

    if include_titles is not None:
        if len(include_titles) != len(include_list):
            raise ValueError(
                "include_titles must have the same length as include when provided."
            )
        return include_list, list(include_titles)
    return include_list, None


def plot_classification_report(
    df: Optional[pd.DataFrame] = None,
    *,
    y_true: Optional[Sequence] = None,
    y_pred: Optional[Sequence] = None,
    y_proba: Optional[Sequence] = None,
    label_col: str = "label",
    y_pred_col: Optional[str] = None,
    y_proba_col: Optional[str] = None,
    include: Optional[Sequence[str]] = None,
    include_titles: Optional[Sequence[str]] = None,
    pos_label: int = 1,
    figsize: Tuple[float, float] = (10, 7),
    n_bins: int = 20,
    calibration_bins: int = 10,
    normalize_confusion: Optional[str] = None,
    class_names: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
    dpi: int = 150,
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """
    Build a 2x2 classification diagnostics figure.

    Returns (fig, [axes]) with axes order:
    [confusion, top-right, ROC, PR]
    """
    y_true_arr, y_pred_arr, y_proba_arr = _unpack_inputs(
        df,
        y_true=y_true,
        y_pred=y_pred,
        y_proba=y_proba,
        label_col=label_col,
        y_pred_col=y_pred_col,
        y_proba_col=y_proba_col,
    )

    # derive predictions if not provided but probabilities exist
    if y_pred_arr is None and y_proba_arr is not None:
        scores_tmp = _positive_score_from_proba(y_proba_arr)
        y_pred_arr = (scores_tmp >= 0.5).astype(int)

    if y_pred_arr is None:
        raise ValueError("y_pred must be provided either directly or via y_proba.")

    # validate include / titles
    include_list, titles = _validate_and_prepare_panels(include, include_titles)

    # check probability requirement for some panels
    needs_proba = any(
        p in {"score_hist", "calibration", "roc", "pr"} for p in include_list
    )
    if needs_proba and y_proba_arr is None:
        raise ValueError(
            "Requested panels require probabilities but y_proba is missing."
        )

    scores = None if y_proba_arr is None else _positive_score_from_proba(y_proba_arr)

    # plotting rc for a cleaner look
    rc = {
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
    }
    with plt.rc_context(rc):
        fig, axes_grid = plt.subplots(2, 2, figsize=figsize, dpi=dpi)
        ax_conf, ax_topright, ax_roc, ax_pr = axes_grid.ravel()
        axes: List[plt.Axes] = [ax_conf, ax_topright, ax_roc, ax_pr]

        # top-left: confusion
        if "confusion" in include_list:
            idx = include_list.index("confusion")
            t = titles[idx] if titles is not None else None
            _draw_confusion(
                ax_conf,
                np.asarray(y_true_arr),
                np.asarray(y_pred_arr),
                normalize=normalize_confusion,
                class_names=class_names,
                title=t,
            )
        else:
            ax_conf.set_axis_off()

        # top-right: prefer score_hist then calibration
        if "score_hist" in include_list and scores is not None:
            idx = include_list.index("score_hist")
            t = titles[idx] if titles is not None else None
            _draw_score_hist(
                ax_topright, np.asarray(y_true_arr), scores, bins=n_bins, title=t
            )
        elif "calibration" in include_list and scores is not None:
            idx = include_list.index("calibration")
            t = titles[idx] if titles is not None else None
            _draw_calibration(
                ax_topright,
                np.asarray(y_true_arr),
                scores,
                n_bins=calibration_bins,
                title=t,
            )
        else:
            ax_topright.set_axis_off()

        # bottom-left: ROC
        if "roc" in include_list and scores is not None:
            idx = include_list.index("roc")
            t = titles[idx] if titles is not None else None
            _draw_roc(ax_roc, np.asarray(y_true_arr), scores, color=COLOR_ROC, title=t)
        else:
            ax_roc.set_axis_off()

        # bottom-right: PR
        if "pr" in include_list and scores is not None:
            idx = include_list.index("pr")
            t = titles[idx] if titles is not None else None
            _draw_pr(
                ax_pr,
                np.asarray(y_true_arr),
                scores,
                pos_label=pos_label,
                color=COLOR_PR,
                title=t,
            )
        else:
            ax_pr.set_axis_off()

        if title:
            fig.suptitle(title, fontsize=14, y=1.02)

        fig.tight_layout()
        return fig, axes
