"""
pepq.metrics.regression._core
=============================

Core utilities for regression reporting (array coercion + basic stats).
"""

from __future__ import annotations

from typing import Any, Dict, Sequence, Tuple

import numpy as np

try:
    from sklearn.metrics import mean_absolute_error, r2_score
except Exception as e:  # pragma: no cover
    raise ImportError(
        "pepq.metrics.regression requires scikit-learn for r2_score/MAE."
    ) from e

try:
    from scipy import stats as _scipy_stats
except Exception:  # pragma: no cover
    _scipy_stats = None


def require_scipy() -> None:
    """
    Raise an informative error if SciPy is required but not installed.
    """
    if _scipy_stats is None:  # pragma: no cover
        raise ImportError(
            "pepq.metrics.regression requires SciPy for Pearson r and QQ-plot "
            "(scipy.stats). Please install scipy."
        )


def ensure_reg_arrays(
    y_true: Sequence,
    y_pred: Sequence,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert regression targets/predictions to 1D float arrays and validate shapes.

    :param y_true: True values.
    :param y_pred: Predicted values.
    :returns: (y_true_arr, y_pred_arr) as 1D float arrays.
    :raises ValueError: If sizes mismatch or arrays are empty.
    """
    y_true_arr = np.asarray(y_true, dtype=float).ravel()
    y_pred_arr = np.asarray(y_pred, dtype=float).ravel()

    if y_true_arr.shape[0] != y_pred_arr.shape[0]:
        raise ValueError(
            "y_true and y_pred must have the same length, "
            f"got {y_true_arr.shape[0]} and {y_pred_arr.shape[0]}."
        )
    if y_true_arr.size == 0:
        raise ValueError("y_true / y_pred are empty.")

    return y_true_arr, y_pred_arr


def basic_reg_stats(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> Dict[str, Any]:
    """
    Compute basic regression summary statistics.

    Stats:
      - n
      - mean_true / mean_pred
      - std_true / std_pred (ddof=1 when n>1)
      - r (Pearson; NaN for constant vectors)
      - r2, mae, rmse

    :param y_true: 1D array of true values.
    :param y_pred: 1D array of predicted values.
    :returns: dict of statistics.
    :raises ValueError: If sizes mismatch.
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()

    if y_true.shape[0] != y_pred.shape[0]:
        raise ValueError(
            "basic_reg_stats: y_true and y_pred must have same length, "
            f"got {y_true.shape[0]} and {y_pred.shape[0]}."
        )

    n = int(y_true.size)
    diff = y_pred - y_true

    # Pearson r (handle constant arrays)
    if np.allclose(np.std(y_true), 0) or np.allclose(np.std(y_pred), 0):
        r = np.nan
    else:
        require_scipy()
        r, _ = _scipy_stats.pearsonr(y_true, y_pred)

    stats: Dict[str, Any] = {
        "n": n,
        "mean_true": float(np.mean(y_true)),
        "mean_pred": float(np.mean(y_pred)),
        "std_true": float(np.std(y_true, ddof=1)) if n > 1 else np.nan,
        "std_pred": float(np.std(y_pred, ddof=1)) if n > 1 else np.nan,
        "r": float(r),
        "r2": float(r2_score(y_true, y_pred)),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(np.mean(diff**2))),
    }
    return stats
