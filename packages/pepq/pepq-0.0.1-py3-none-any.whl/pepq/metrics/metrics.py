"""
metrics.py
==========

Extended reporting utilities for classification and regression (numeric only).

This module provides:

* Reusable CV summary helpers (``classification_cv_summary``,
  ``regression_cv_summary``) — lightweight wrappers around scikit-learn.
* High-level reporting helpers:
  - ``classification_report_dict`` / ``classification_report_df``
  - ``regression_report_dict`` / ``regression_report_df``
* JSON export helpers:
  - ``to_json_serializable``
  - ``dump_report_to_json``

The reporting functions accept either:

* **DataFrame mode**: pass a :class:`pandas.DataFrame` and the name of the
  label/target column.
* **Array mode**: pass ``y_true`` and ``y_pred`` (and optionally
  ``y_proba``, ``y_lower``, ``y_upper``).

All functions return simple Python dicts with numeric summaries and
:class:`pandas.DataFrame` objects for tabular export.

Examples
--------

.. code-block:: python

   from pepq.model.metrics import classification_report_df
   import pandas as pd

   df = pd.DataFrame({'f1':[0.1, 0.2],
                      'f2':[0.3, 0.4],
                      'label':[0, 1],
                      'y_proba':[0.2, 0.9]})

   report = classification_report_df(df=df,
                                     label_col='label',
                                     y_pred_col=None,
                                     y_proba_col='y_proba')
   print(report['metrics_df'])
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Sequence, Iterable

import json
import numpy as np
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    roc_auc_score,
    brier_score_loss,
    log_loss,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import (
    RepeatedKFold,
    RepeatedStratifiedKFold,
    cross_val_score,
)


# ---------------------------------------------------------------------------
# CV summary helpers
# ---------------------------------------------------------------------------


def classification_cv_summary(
    estimator,
    X,
    y,
    n_splits: int,
    n_repeats: int,
    random_state: Optional[int],
) -> Dict[str, float]:
    """
    Cross-validation summary for classification.

    Uses :class:`RepeatedStratifiedKFold` and reports mean/std of
    accuracy and ROC-AUC.

    :param estimator: sklearn-compatible estimator with ``fit`` and ``score``.
    :param X: Feature matrix of shape ``(n_samples, n_features)``.
    :param y: Label vector of shape ``(n_samples,)``.
    :param n_splits: Number of folds per repeat.
    :param n_repeats: Number of repeats.
    :param random_state: Random seed for CV splitting.
    :returns: Dictionary with keys
        ``cv_accuracy_mean``, ``cv_accuracy_std``,
        ``cv_roc_auc_mean``, ``cv_roc_auc_std``, ``n_samples``.
    """
    cv = RepeatedStratifiedKFold(
        n_splits=n_splits,
        n_repeats=n_repeats,
        random_state=random_state,
    )
    acc = cross_val_score(estimator, X, y, cv=cv, scoring="accuracy", n_jobs=-1)
    roc = cross_val_score(estimator, X, y, cv=cv, scoring="roc_auc", n_jobs=-1)
    return {
        "cv_accuracy_mean": float(np.mean(acc)),
        "cv_accuracy_std": float(np.std(acc)),
        "cv_roc_auc_mean": float(np.mean(roc)),
        "cv_roc_auc_std": float(np.std(roc)),
        "n_samples": int(len(y)),
    }


def regression_cv_summary(
    estimator,
    X,
    y,
    n_splits: int,
    n_repeats: int,
    random_state: Optional[int],
) -> Dict[str, float]:
    """
    Cross-validation summary for regression.

    Uses :class:`RepeatedKFold` and reports mean/std of MAE, RMSE and R².

    :param estimator: sklearn-compatible regressor with ``fit`` and ``score``.
    :param X: Feature matrix of shape ``(n_samples, n_features)``.
    :param y: Target vector of shape ``(n_samples,)``.
    :param n_splits: Number of folds per repeat.
    :param n_repeats: Number of repeats.
    :param random_state: Random seed for CV splitting.
    :returns: Dictionary with keys
        ``cv_mae_mean``, ``cv_mae_std``,
        ``cv_rmse_mean``, ``cv_rmse_std``,
        ``cv_r2_mean``, ``cv_r2_std``, ``n_samples``.
    """
    cv = RepeatedKFold(
        n_splits=n_splits,
        n_repeats=n_repeats,
        random_state=random_state,
    )
    mae = -cross_val_score(
        estimator, X, y, cv=cv, scoring="neg_mean_absolute_error", n_jobs=-1
    )
    rmse = -cross_val_score(
        estimator, X, y, cv=cv, scoring="neg_root_mean_squared_error", n_jobs=-1
    )
    r2 = cross_val_score(estimator, X, y, cv=cv, scoring="r2", n_jobs=-1)
    return {
        "cv_mae_mean": float(np.mean(mae)),
        "cv_mae_std": float(np.std(mae)),
        "cv_rmse_mean": float(np.mean(rmse)),
        "cv_rmse_std": float(np.std(rmse)),
        "cv_r2_mean": float(np.mean(r2)),
        "cv_r2_std": float(np.std(r2)),
        "n_samples": int(len(y)),
    }


# ---------------------------------------------------------------------------
# Classification reporting
# ---------------------------------------------------------------------------


def _unpack_df_or_arrays_classification(
    df: Optional[pd.DataFrame],
    *,
    y_true: Optional[Sequence] = None,
    y_pred: Optional[Sequence] = None,
    y_proba: Optional[Sequence] = None,
    label_col: str = "label",
    y_pred_col: Optional[str] = None,
    y_proba_col: Optional[str] = None,
) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]:
    """
    Normalise classification inputs to arrays.

    Either DataFrame mode ``df`` or explicit array mode is supported.

    :param df: DataFrame containing labels/predictions/probabilities, or ``None``.
    :param y_true: True labels in array mode.
    :param y_pred: Predicted labels in array mode.
    :param y_proba: Predicted probabilities in array mode.
    :param label_col: Label column name in DataFrame mode.
    :param y_pred_col: Prediction column name in DataFrame mode.
    :param y_proba_col: Probability column name in DataFrame mode.
    :returns: Tuple ``(y_true, y_pred, y_proba)`` as numpy arrays, where
              ``y_proba`` may be ``None``.
    """
    if df is not None:
        if label_col not in df.columns:
            raise ValueError(f"Label column '{label_col}' not found in dataframe.")
        y_true_arr = df[label_col].astype(int).values

        if y_pred_col is not None:
            if y_pred_col not in df.columns:
                raise ValueError(f"y_pred_col '{y_pred_col}' not found in dataframe.")
            y_pred_arr = df[y_pred_col].astype(int).values
        else:
            y_pred_arr = None

        if y_proba_col is not None:
            if y_proba_col not in df.columns:
                raise ValueError(f"y_proba_col '{y_proba_col}' not found in dataframe.")
            y_proba_arr = np.asarray(df[y_proba_col].values, dtype=float)
        else:
            y_proba_arr = None

        return y_true_arr, y_pred_arr, y_proba_arr

    # array mode
    if y_true is None:
        raise ValueError("y_true must be provided in array mode.")
    y_true_arr = np.asarray(y_true).astype(int).ravel()
    y_pred_arr = None if y_pred is None else np.asarray(y_pred).astype(int).ravel()
    y_proba_arr = None if y_proba is None else np.asarray(y_proba).astype(float).ravel()
    return y_true_arr, y_pred_arr, y_proba_arr


def classification_report_dict(
    df: Optional[pd.DataFrame] = None,
    *,
    y_true: Optional[Sequence] = None,
    y_pred: Optional[Sequence] = None,
    y_proba: Optional[Sequence] = None,
    label_col: str = "label",
    y_pred_col: Optional[str] = None,
    y_proba_col: Optional[str] = None,
    pos_label: int = 1,
) -> Dict[str, Any]:
    """
    Produce a dictionary-style classification report.

    Supports both DataFrame and array mode. In DataFrame mode, predictions
    and probabilities are read from labelled columns; in array mode they are
    passed directly.

    :param df: Input DataFrame or ``None``.
    :param y_true: True labels in array mode.
    :param y_pred: Predicted labels in array mode.
    :param y_proba: Predicted probabilities in array mode.
    :param label_col: Label column name in DataFrame mode.
    :param y_pred_col: Prediction column name in DataFrame mode.
    :param y_proba_col: Probability column name in DataFrame mode.
    :param pos_label: Positive-label index (currently unused, reserved).
    :returns: Dictionary with keys:

        * ``metrics`` – dict with overall metrics
          (``accuracy``, ``roc_auc``, ``brier``, ``logloss``).
        * ``per_label`` – DataFrame with precision/recall/F1/support per label.
        * ``confusion`` – confusion matrix as DataFrame.
        * ``y_true`` – numpy array of true labels.
        * ``y_pred`` – numpy array of predicted labels.
        * ``y_proba`` – numpy array of probabilities (or ``None``).
    """
    y_true_arr, y_pred_arr, y_proba_arr = _unpack_df_or_arrays_classification(
        df,
        y_true=y_true,
        y_pred=y_pred,
        y_proba=y_proba,
        label_col=label_col,
        y_pred_col=y_pred_col,
        y_proba_col=y_proba_col,
    )

    # If predictions missing but probabilities exist, derive predictions
    if y_pred_arr is None and y_proba_arr is not None:
        y_pred_arr = (y_proba_arr >= 0.5).astype(int)

    if y_pred_arr is None:
        raise ValueError("y_pred must be provided either directly or via y_proba.")

    acc = float(accuracy_score(y_true_arr, y_pred_arr))
    prec, rec, f1, sup = precision_recall_fscore_support(
        y_true_arr, y_pred_arr, zero_division=0
    )
    per_label_df = pd.DataFrame(
        {
            "label": list(range(len(prec))),
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "support": sup,
        }
    )

    conf = confusion_matrix(y_true_arr, y_pred_arr)
    conf_df = pd.DataFrame(
        conf,
        index=[f"true_{i}" for i in range(conf.shape[0])],
        columns=[f"pred_{i}" for i in range(conf.shape[1])],
    )

    roc_auc = None
    brier = None
    logloss_v = None
    if y_proba_arr is not None:
        try:
            # if multiclass, attempt positive-class AUC for binary
            if y_proba_arr.ndim == 2:
                if y_proba_arr.shape[1] == 2:
                    pos_proba = y_proba_arr[:, 1]
                else:
                    pos_proba = np.max(y_proba_arr, axis=1)
            else:
                pos_proba = y_proba_arr

            roc_auc = float(roc_auc_score(y_true_arr, pos_proba))
            brier = float(brier_score_loss(y_true_arr, pos_proba))
            logloss_v = float(log_loss(y_true_arr, pos_proba))
        except Exception:
            roc_auc = None

    metrics = {
        "accuracy": acc,
        "roc_auc": roc_auc,
        "brier": brier,
        "logloss": logloss_v,
    }

    return {
        "metrics": metrics,
        "per_label": per_label_df,
        "confusion": conf_df,
        "y_true": y_true_arr,
        "y_pred": y_pred_arr,
        "y_proba": y_proba_arr,
    }


def classification_report_df(*args, **kwargs) -> Dict[str, Any]:
    """
    Wrapper around :func:`classification_report_dict` that adds a metric table.

    :returns: Same dictionary as :func:`classification_report_dict`, with an
        additional key ``metrics_df`` containing a one-row
        :class:`pandas.DataFrame` of numeric metrics.
    """
    rep = classification_report_dict(*args, **kwargs)
    metrics = rep["metrics"]
    metrics_norm = {k: (v if v is not None else np.nan) for k, v in metrics.items()}
    metrics_df = pd.DataFrame([metrics_norm])
    rep["metrics_df"] = metrics_df
    return rep


# ---------------------------------------------------------------------------
# Regression reporting
# ---------------------------------------------------------------------------


def _unpack_df_or_arrays_regression(
    df: Optional[pd.DataFrame],
    *,
    y_true: Optional[Sequence] = None,
    y_pred: Optional[Sequence] = None,
    y_lower: Optional[Sequence] = None,
    y_upper: Optional[Sequence] = None,
    target_col: str = "target",
    y_pred_col: Optional[str] = None,
    y_lower_col: Optional[str] = None,
    y_upper_col: Optional[str] = None,
) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Normalise regression inputs to arrays.

    :param df: DataFrame with true/predicted/interval columns or ``None``.
    :param y_true: True values in array mode.
    :param y_pred: Predicted values in array mode.
    :param y_lower: Lower prediction interval in array mode.
    :param y_upper: Upper prediction interval in array mode.
    :param target_col: Column name for true values in DataFrame mode.
    :param y_pred_col: Column name for predictions in DataFrame mode.
    :param y_lower_col: Column name for lower bounds in DataFrame mode.
    :param y_upper_col: Column name for upper bounds in DataFrame mode.
    :returns: Tuple ``(y_true, y_pred, y_lower, y_upper)`` arrays where the
        last two entries may be ``None``.
    """
    if df is not None:
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataframe.")
        y_true_arr = df[target_col].astype(float).values
        y_pred_arr = (
            None
            if y_pred_col is None
            else np.asarray(df[y_pred_col].values, dtype=float)
        )
        y_lower_arr = (
            None
            if y_lower_col is None
            else np.asarray(df[y_lower_col].values, dtype=float)
        )
        y_upper_arr = (
            None
            if y_upper_col is None
            else np.asarray(df[y_upper_col].values, dtype=float)
        )
        return y_true_arr, y_pred_arr, y_lower_arr, y_upper_arr

    if y_true is None:
        raise ValueError("y_true must be provided in array mode.")
    y_true_arr = np.asarray(y_true).astype(float).ravel()
    y_pred_arr = None if y_pred is None else np.asarray(y_pred).astype(float).ravel()
    y_lower_arr = None if y_lower is None else np.asarray(y_lower).astype(float).ravel()
    y_upper_arr = None if y_upper is None else np.asarray(y_upper).astype(float).ravel()
    return y_true_arr, y_pred_arr, y_lower_arr, y_upper_arr


def regression_report_dict(
    df: Optional[pd.DataFrame] = None,
    *,
    y_true: Optional[Sequence] = None,
    y_pred: Optional[Sequence] = None,
    y_lower: Optional[Sequence] = None,
    y_upper: Optional[Sequence] = None,
    target_col: str = "target",
    y_pred_col: Optional[str] = None,
    y_lower_col: Optional[str] = None,
    y_upper_col: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Produce a regression report dictionary.

    :param df: Input DataFrame in DataFrame mode, or ``None``.
    :param y_true: True values in array mode.
    :param y_pred: Predicted values in array mode.
    :param y_lower: Lower prediction interval (optional).
    :param y_upper: Upper prediction interval (optional).
    :param target_col: Column name for true values in DataFrame mode.
    :param y_pred_col: Column name for predictions in DataFrame mode.
    :param y_lower_col: Column name for interval lower bounds.
    :param y_upper_col: Column name for interval upper bounds.
    :returns: Dictionary with keys:

        * ``metrics`` – dict with ``mae``, ``rmse``, ``r2``.
        * ``residuals_df`` – DataFrame with columns
          ``['y_true', 'y_pred', 'residual']``.
        * ``interval_stats`` – dict with ``coverage`` and ``mean_width``
          if intervals are provided.
        * ``y_true`` – numpy array of true values.
        * ``y_pred`` – numpy array of predicted values.
    """
    y_true_arr, y_pred_arr, y_lower_arr, y_upper_arr = _unpack_df_or_arrays_regression(
        df,
        y_true=y_true,
        y_pred=y_pred,
        y_lower=y_lower,
        y_upper=y_upper,
        target_col=target_col,
        y_pred_col=y_pred_col,
        y_lower_col=y_lower_col,
        y_upper_col=y_upper_col,
    )

    if y_pred_arr is None:
        raise ValueError("y_pred must be provided directly or via DataFrame columns.")

    mae_v = float(mean_absolute_error(y_true_arr, y_pred_arr))
    rmse_v = float(np.sqrt(mean_squared_error(y_true_arr, y_pred_arr)))
    r2_v = float(r2_score(y_true_arr, y_pred_arr))

    residuals = y_true_arr - y_pred_arr
    residuals_df = pd.DataFrame(
        {"y_true": y_true_arr, "y_pred": y_pred_arr, "residual": residuals}
    )

    interval_stats = {"coverage": None, "mean_width": None}
    if y_lower_arr is not None and y_upper_arr is not None:
        within = (y_true_arr >= y_lower_arr) & (y_true_arr <= y_upper_arr)
        interval_stats["coverage"] = float(np.mean(within))
        interval_stats["mean_width"] = float(np.mean(y_upper_arr - y_lower_arr))

    metrics = {"mae": mae_v, "rmse": rmse_v, "r2": r2_v}
    return {
        "metrics": metrics,
        "residuals_df": residuals_df,
        "interval_stats": interval_stats,
        "y_true": y_true_arr,
        "y_pred": y_pred_arr,
    }


def regression_report_df(*args, **kwargs) -> Dict[str, Any]:
    """
    Wrapper around :func:`regression_report_dict` that adds a metric table.

    :returns: Same dictionary as :func:`regression_report_dict` plus
        ``metrics_df`` (one-row DataFrame of aggregated metrics).
    """
    rep = regression_report_dict(*args, **kwargs)
    metrics = rep["metrics"]
    rep["metrics_df"] = pd.DataFrame([metrics])
    return rep


# ---------------------------------------------------------------------------
# JSON export helpers
# ---------------------------------------------------------------------------


def to_json_serializable(obj: Any) -> Any:
    """
    Convert simple numpy/pandas objects to JSON-serialisable types.

    :param obj: Object to convert.
    :returns: JSON-serialisable representation (numbers, lists, dicts).
    """
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return float(obj)
    if isinstance(obj, (np.ndarray, list)):
        return list(np.asarray(obj).tolist())
    if isinstance(obj, pd.DataFrame):
        return json.loads(obj.to_json(orient="split"))
    if isinstance(obj, pd.Series):
        return obj.to_list()
    return obj


def dump_report_to_json(report: Dict[str, Any], fname: str) -> None:
    """
    Save a report dictionary to disk as JSON.

    :param report: Report dictionary as returned by
        :func:`classification_report_dict` or :func:`regression_report_dict`.
    :param fname: Output filename.
    """
    serial = {k: to_json_serializable(v) for k, v in report.items()}
    with open(fname, "w", encoding="utf-8") as fh:
        json.dump(serial, fh, indent=2)


class MetricsCalculator:
    """
    Compute common regression metrics from true and predicted values.

    This class follows a small OOP / fluent interface: call ``.fit(y_true, y_pred)``
    to compute and store metrics, then access them via the ``metrics`` property.

    :param y_true: Ground-truth target values (1D iterable).
    :type y_true: Iterable[float]
    :param y_pred: Predicted target values (1D iterable).
    :type y_pred: Iterable[float]

    Example
    -------
    >>> mc = MetricsCalculator().fit([1,2,3], [1.1,1.9,3.2])
    >>> mc.metrics
    {'pearson': 0.998..., 'spearman': 0.99..., 'r2': 0.98..., 'mae': 0.1, 'rmse': 0.11}
    """

    def __init__(self) -> None:
        self._y_true: Optional[np.ndarray] = None
        self._y_pred: Optional[np.ndarray] = None
        self._results: Dict[str, float] = {}
        self._n: int = 0

    def __repr__(self) -> str:
        if not self._results:
            return "<MetricsCalculator (empty)>"
        return (
            f"<MetricsCalculator n={self._n} "
            f"pearson={self._results.get('pearson'):.4f} "
            f"spearman={self._results.get('spearman'):.4f} "
            f"r2={self._results.get('r2'):.4f} "
            f"mae={self._results.get('mae'):.4f} "
            f"rmse={self._results.get('rmse'):.4f}>"
        )

    # ---- Public fluent API ----
    def fit(
        self, y_true: Iterable[float], y_pred: Iterable[float]
    ) -> "MetricsCalculator":
        """
        Store inputs and compute metrics.

        :param y_true: Iterable of true values.
        :param y_pred: Iterable of predicted values.
        :returns: self (fluent)
        """
        yt = np.asarray(list(y_true), dtype=float)
        yp = np.asarray(list(y_pred), dtype=float)
        if yt.shape != yp.shape:
            raise ValueError("y_true and y_pred must have the same shape.")
        self._y_true = yt
        self._y_pred = yp
        self._n = yt.size
        self._compute()
        return self

    # ---- Properties ----
    @property
    def metrics(self) -> Dict[str, float]:
        """Return a dict with computed metrics (Python floats)."""
        # convert numpy floats to Python floats for nicer printing/JSON compatibility
        return {k: float(v) for k, v in self._results.items()}

    @property
    def n(self) -> int:
        """Number of samples."""
        return int(self._n)

    # ---- Internal helpers ----
    def _rankdata(self, a: np.ndarray) -> np.ndarray:
        """
        Compute ranks (average ranks for ties), 1-based ranking.
        Pure-numpy implementation to avoid scipy dependency.
        """
        if a.size == 0:
            return a
        order = np.argsort(a, kind="mergesort")  # stable
        ranks = np.empty(a.size, dtype=float)
        # temporary ordinal ranks
        ranks[order] = np.arange(1, a.size + 1)
        # handle ties: find groups of equal values in the sorted array
        sorted_a = a[order]
        i = 0
        while i < a.size:
            j = i + 1
            while j < a.size and sorted_a[j] == sorted_a[i]:
                j += 1
            if j - i > 1:
                # average rank for the block [i, j)
                avg_rank = (i + 1 + j) / 2.0
                ranks[order[i:j]] = avg_rank
            i = j
        return ranks

    def _pearson(self, x: np.ndarray, y: np.ndarray) -> float:
        """Pearson correlation using numpy, returns nan if undefined."""
        if x.size == 0:
            return float("nan")
        # subtract means
        xm = x - x.mean()
        ym = y - y.mean()
        denom = np.sqrt((xm**2).sum() * (ym**2).sum())
        if denom == 0:
            return float("nan")
        return float((xm * ym).sum() / denom)

    def _compute(self) -> None:
        """Compute all metrics and store results in self._results."""
        yt = self._y_true
        yp = self._y_pred
        if yt is None or yp is None:
            raise RuntimeError("No data. Call fit() first.")

        # basic diffs
        diff = yt - yp
        abs_diff = np.abs(diff)
        sq_diff = diff**2

        # pearson
        pear = self._pearson(yt, yp)

        # spearman: rank the arrays then compute Pearson on ranks
        r_yt = self._rankdata(yt)
        r_yp = self._rankdata(yp)
        spearman = self._pearson(r_yt, r_yp)

        # r2 (coefficient of determination)
        ss_res = sq_diff.sum()
        ss_tot = ((yt - yt.mean()) ** 2).sum()
        if ss_tot == 0:
            r2 = float("nan")
        else:
            r2 = 1.0 - (ss_res / ss_tot)

        # mae and rmse
        mae = abs_diff.mean() if abs_diff.size > 0 else float("nan")
        rmse = float(np.sqrt(sq_diff.mean())) if sq_diff.size > 0 else float("nan")

        self._results = {
            "pearson": pear,
            "spearman": spearman,
            "r2": r2,
            "mae": mae,
            "rmse": rmse,
        }
