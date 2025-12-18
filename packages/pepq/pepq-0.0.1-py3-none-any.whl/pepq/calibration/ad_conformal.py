from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

try:  # optional but preferred
    from scipy.stats import pearsonr, spearmanr

    _HAVE_SCIPY = True
except Exception:  # pragma: no cover - optional
    pearsonr = None
    spearmanr = None
    _HAVE_SCIPY = False


class ADConformal:
    """
    Applicability domain based on conformal prediction intervals.

    This class assumes that the wrapped regression model exposes a
    :meth:`predict_with_interval` method::

        y_pred, y_lower, y_upper = model.predict_with_interval(X, alpha)

    It then uses the **interval width** as an uncertainty score to
    define an applicability domain:

    * calibration set (``X_cal, y_cal``) is used to estimate interval
      widths and derive a width threshold via a chosen quantile,
    * for labelled evaluation sets, :meth:`predict` computes coverage
      and regression metrics both over all samples and restricted to the
      in-domain subset (width <= threshold),
    * for unlabelled new samples, the width alone serves as a
      **conformal AD score** (large widths → more out-of-domain),
    * :meth:`scan_width_tradeoff` scans width thresholds (based on
      calibration quantiles) and evaluates coverage / Pearson / Spearman
      trade-offs on an external set,
    * :meth:`predict_confident_with_threshold` uses a chosen width
      threshold (or quantile) to obtain **confident predictions** on a
      new test set and exposes them via :attr:`confident_predictions`.

    Parameters
    ----------
    alpha : float, optional
        Miscoverage level for prediction intervals (default: 0.05 for
        95 % intervals).
    width_quantile : float, optional
        Calibration quantile used to define the default width-based
        applicability-domain threshold (default: 0.90).
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    def __init__(self, alpha: float = 0.05, width_quantile: float = 0.90) -> None:
        self.alpha = float(alpha)
        self.width_quantile = float(width_quantile)

        # learned state
        self.model_: Any = None
        self._width_cal: Optional[np.ndarray] = None
        self._width_threshold: Optional[float] = None

        self._y_cal: Optional[np.ndarray] = None
        self._y_cal_pred: Optional[np.ndarray] = None

        self._calib_metrics: Optional[Dict[str, float]] = None
        self._eval_metrics: Optional[Dict[str, float]] = None
        self._tradeoff_table: Optional[pd.DataFrame] = None

        # last labelled prediction state (from .predict)
        self._last_y_true: Optional[np.ndarray] = None
        self._last_y_pred: Optional[np.ndarray] = None
        self._last_y_lower: Optional[np.ndarray] = None
        self._last_y_upper: Optional[np.ndarray] = None
        self._last_widths: Optional[np.ndarray] = None
        self._last_in_mask: Optional[np.ndarray] = None

        # last confident prediction state (from .predict_confident_with_threshold)
        self._conf_threshold: Optional[float] = None
        self._conf_y_pred: Optional[np.ndarray] = None
        self._conf_y_lower: Optional[np.ndarray] = None
        self._conf_y_upper: Optional[np.ndarray] = None
        self._conf_widths: Optional[np.ndarray] = None
        self._conf_mask: Optional[np.ndarray] = None

    # ------------------------------------------------------------------
    # Basic introspection
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"alpha={self.alpha:.3f}, "
            f"width_quantile={self.width_quantile:.3f})"
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def width_threshold(self) -> Optional[float]:
        """
        Width-based applicability-domain threshold.

        This is derived from calibration widths via
        :attr:`width_quantile`.

        :return: Current width threshold or ``None`` if not fitted.
        :rtype: Optional[float]
        """
        return self._width_threshold

    @property
    def calib_metrics(self) -> Optional[Dict[str, float]]:
        """
        Summary metrics on the calibration set.

        Includes coverage, mean/median width, Winkler score, and
        regression metrics (R², MAE, RMSE, Pearson r, Spearman ρ),
        computed over all calibration samples.

        :return: Dictionary of calibration metrics.
        :rtype: Optional[Dict[str, float]]
        """
        return self._calib_metrics

    @property
    def eval_metrics(self) -> Optional[Dict[str, float]]:
        """
        Summary metrics on the last labelled prediction set.

        Populated by :meth:`predict`. Contains metrics both over all
        samples and restricted to the in-domain subset
        (width <= :attr:`width_threshold` or a custom threshold).

        :return: Dictionary of evaluation metrics.
        :rtype: Optional[Dict[str, float]]
        """
        return self._eval_metrics

    @property
    def tradeoff_table(self) -> Optional[pd.DataFrame]:
        """
        Coverage–performance trade-off table on an evaluation set.

        Filled by :meth:`scan_width_tradeoff`. Each row contains:

        * ``quantile`` – calibration width quantile,
        * ``threshold`` – width threshold derived from calibration,
        * ``coverage`` – fraction of evaluation samples in-domain,
        * ``coverage_interval`` – interval coverage on in-domain samples,
        * ``pearson_r_in_domain`` – Pearson r on in-domain subset,
        * ``spearman_rho_in_domain`` – Spearman ρ on in-domain subset,
        * ``score`` – combined coverage–Pearson score (gmean or Fβ),
        * ``n_in_domain`` – number of in-domain samples.

        :return: Trade-off table or ``None`` if not computed.
        :rtype: Optional[pd.DataFrame]
        """
        return self._tradeoff_table

    @property
    def last_predictions(self) -> Optional[Dict[str, np.ndarray]]:
        """
        Last labelled predictions and in-domain mask.

        Populated by :meth:`predict`.

        Returned dictionary keys
        ------------------------
        y_true : numpy.ndarray
            True targets.
        y_pred : numpy.ndarray
            Point predictions.
        y_lower : numpy.ndarray
            Lower interval bounds.
        y_upper : numpy.ndarray
            Upper interval bounds.
        width : numpy.ndarray
            Interval widths.
        in_domain_mask : numpy.ndarray
            Boolean mask for in-domain samples (width <= threshold).

        :return: Dictionary with arrays, or ``None`` if :meth:`predict`
            has not been called.
        :rtype: Optional[Dict[str, numpy.ndarray]]
        """
        if self._last_y_pred is None:
            return None
        return {
            "y_true": self._last_y_true,
            "y_pred": self._last_y_pred,
            "y_lower": self._last_y_lower,
            "y_upper": self._last_y_upper,
            "width": self._last_widths,
            "in_domain_mask": self._last_in_mask,
        }

    @property
    def confident_predictions(self) -> Optional[Dict[str, np.ndarray]]:
        """
        Last confident predictions obtained via width thresholding.

        Populated by :meth:`predict_confident_with_threshold`. This is
        intended for **test / unlabelled** sets where you apply a chosen
        width cutoff (e.g. selected from a calibration trade-off table).

        Returned dictionary keys
        ------------------------
        threshold : float
            Width threshold that defined the in-domain set.
        y_pred : numpy.ndarray
            Point predictions for all samples.
        y_lower : numpy.ndarray
            Lower interval bounds for all samples.
        y_upper : numpy.ndarray
            Upper interval bounds for all samples.
        width : numpy.ndarray
            Interval widths for all samples.
        in_domain_mask : numpy.ndarray
            Boolean mask for in-domain samples (width <= threshold).

        :return: Dictionary with arrays, or ``None`` if
            :meth:`predict_confident_with_threshold` has not been called.
        :rtype: Optional[Dict[str, numpy.ndarray]]
        """
        if self._conf_y_pred is None:
            return None
        return {
            "threshold": np.array(self._conf_threshold, ndmin=1),
            "y_pred": self._conf_y_pred,
            "y_lower": self._conf_y_lower,
            "y_upper": self._conf_y_upper,
            "width": self._conf_widths,
            "in_domain_mask": self._conf_mask,
        }

    # ------------------------------------------------------------------
    # Core fitting
    # ------------------------------------------------------------------
    def fit(
        self,
        model: Any,
        X_cal: np.ndarray,
        y_cal: np.ndarray,
    ) -> "ADConformal":
        """
        Fit the conformal AD using a calibration set.

        This method assumes that ``model`` has already been trained on a
        separate training set and exposes :meth:`predict_with_interval`.

        It computes conformal prediction intervals on the calibration
        set, stores the interval widths, and derives a width threshold
        based on :attr:`width_quantile`.

        :param model: Fitted regression model with
            :meth:`predict_with_interval`.
        :type model: Any
        :param X_cal: Calibration features, shape ``(n_cal, n_features)``.
        :type X_cal: numpy.ndarray
        :param y_cal: Calibration targets, shape ``(n_cal,)``.
        :type y_cal: numpy.ndarray
        :return: The fitted :class:`ADConformal` instance.
        :rtype: ADConformal
        """
        if not hasattr(model, "predict_with_interval"):
            raise RuntimeError("Model must implement predict_with_interval(X, alpha).")

        self.model_ = model

        X_cal = np.asarray(X_cal)
        y_cal = np.asarray(y_cal)

        y_pred, y_lower, y_upper = self.model_.predict_with_interval(
            X_cal, alpha=self.alpha
        )
        y_pred = np.asarray(y_pred)
        y_lower = np.asarray(y_lower)
        y_upper = np.asarray(y_upper)

        self._y_cal = y_cal
        self._y_cal_pred = y_pred

        self._width_cal = (y_upper - y_lower).astype(float)
        self._width_threshold = float(np.quantile(self._width_cal, self.width_quantile))

        self._calib_metrics = self._interval_metrics(
            y_true=y_cal,
            y_pred=y_pred,
            y_lower=y_lower,
            y_upper=y_upper,
            prefix="cal_",
        )
        return self

    # ------------------------------------------------------------------
    # Internal metric helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _pearson_spearman(
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> Dict[str, float]:
        """
        Compute Pearson r and Spearman ρ.

        Uses :mod:`scipy.stats` if available; otherwise uses NumPy
        correlation and rank-based Spearman approximation.

        :param y_true: True targets.
        :type y_true: numpy.ndarray
        :param y_pred: Predicted targets.
        :type y_pred: numpy.ndarray
        :return: Dictionary with ``pearson_r`` and ``spearman_rho``.
        :rtype: Dict[str, float]
        """
        y_true = np.asarray(y_true, dtype=float)
        y_pred = np.asarray(y_pred, dtype=float)

        if y_true.size < 2:
            return {"pearson_r": np.nan, "spearman_rho": np.nan}

        if _HAVE_SCIPY:
            r_p = float(pearsonr(y_true, y_pred)[0])
            r_s = float(spearmanr(y_true, y_pred)[0])
        else:
            r_p = float(np.corrcoef(y_true, y_pred)[0, 1])
            ranks_true = np.argsort(np.argsort(y_true))
            ranks_pred = np.argsort(np.argsort(y_pred))
            r_s = float(np.corrcoef(ranks_true, ranks_pred)[0, 1])

        return {"pearson_r": r_p, "spearman_rho": r_s}

    @classmethod
    def _regression_metrics(
        cls,
        y_true: np.ndarray,
        y_pred: np.ndarray,
    ) -> Dict[str, float]:
        """
        Compute standard regression metrics.

        Includes R², MAE, RMSE, Pearson r, Spearman ρ.

        :param y_true: True targets.
        :type y_true: numpy.ndarray
        :param y_pred: Predicted targets.
        :type y_pred: numpy.ndarray
        :return: Dictionary of regression metrics.
        :rtype: Dict[str, float]
        """
        y_true = np.asarray(y_true, dtype=float)
        y_pred = np.asarray(y_pred, dtype=float)

        if y_true.size == 0:
            return {
                "r2": np.nan,
                "mae": np.nan,
                "rmse": np.nan,
                "pearson_r": np.nan,
                "spearman_rho": np.nan,
            }

        r2 = float(r2_score(y_true, y_pred))
        mae = float(mean_absolute_error(y_true, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        corr = cls._pearson_spearman(y_true, y_pred)

        out = {"r2": r2, "mae": mae, "rmse": rmse}
        out.update(corr)
        return out

    @classmethod
    def _interval_metrics(
        cls,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_lower: np.ndarray,
        y_upper: np.ndarray,
        prefix: str = "",
    ) -> Dict[str, float]:
        """
        Compute summary metrics for prediction intervals.

        Metrics:

        * coverage (fraction of points where ``y_lower <= y_true <= y_upper``),
        * mean / median width,
        * mean Winkler-like score,
        * regression metrics on point predictions.

        :param y_true: True targets.
        :type y_true: numpy.ndarray
        :param y_pred: Point predictions.
        :type y_pred: numpy.ndarray
        :param y_lower: Lower interval bounds.
        :type y_lower: numpy.ndarray
        :param y_upper: Upper interval bounds.
        :type y_upper: numpy.ndarray
        :param prefix: Optional prefix for metric names.
        :type prefix: str
        :return: Dictionary of interval and regression metrics.
        :rtype: Dict[str, float]
        """
        y_true = np.asarray(y_true, dtype=float)
        y_pred = np.asarray(y_pred, dtype=float)
        y_lower = np.asarray(y_lower, dtype=float)
        y_upper = np.asarray(y_upper, dtype=float)

        if y_true.size == 0:
            return {}

        width = y_upper - y_lower
        coverage_mask = (y_true >= y_lower) & (y_true <= y_upper)
        coverage = float(coverage_mask.mean())

        mean_width = float(width.mean())
        median_width = float(np.median(width))

        # Simple Winkler-like score for regression intervals
        penalty_lower = np.where(y_true < y_lower, y_lower - y_true, 0.0)
        penalty_upper = np.where(y_true > y_upper, y_true - y_upper, 0.0)
        winkler = width + 2.0 * (penalty_lower + penalty_upper)
        mean_winkler = float(winkler.mean())

        reg = cls._regression_metrics(y_true, y_pred)

        out = {
            f"{prefix}coverage": coverage,
            f"{prefix}mean_width": mean_width,
            f"{prefix}median_width": median_width,
            f"{prefix}mean_winkler": mean_winkler,
        }
        for k, v in reg.items():
            out[f"{prefix}{k}"] = v
        return out

    # ------------------------------------------------------------------
    # Width scores and in-domain mask
    # ------------------------------------------------------------------
    def width_score(self, X: np.ndarray) -> np.ndarray:
        """
        Compute conformal width scores for new samples.

        The width of the prediction interval is used as an uncertainty
        / out-of-domain score (larger width → more uncertain).

        :param X: Feature matrix, shape ``(n_samples, n_features)``.
        :type X: numpy.ndarray
        :return: Interval widths for each sample.
        :rtype: numpy.ndarray
        """
        if self.model_ is None:
            raise RuntimeError("ADConformal has not been fitted yet.")
        X = np.asarray(X)
        _, y_lower, y_upper = self.model_.predict_with_interval(X, alpha=self.alpha)
        return (np.asarray(y_upper) - np.asarray(y_lower)).astype(float)

    def in_domain(self, X: np.ndarray, threshold: Optional[float] = None) -> np.ndarray:
        """
        Determine which samples are in-domain based on interval width.

        A sample is considered in-domain if its width is less than or
        equal to a width threshold. If :param:`threshold` is ``None``,
        :attr:`width_threshold` (derived from calibration) is used.

        :param X: Feature matrix, shape ``(n_samples, n_features)``.
        :type X: numpy.ndarray
        :param threshold: Optional custom width threshold.
        :type threshold: Optional[float]
        :return: Boolean mask (True = in-domain).
        :rtype: numpy.ndarray
        """
        X = np.asarray(X)
        widths = self.width_score(X)

        thr = self._width_threshold if threshold is None else threshold
        if thr is None:
            raise RuntimeError("Width threshold is not set; fit ADConformal first.")

        return widths <= float(thr)

    # ------------------------------------------------------------------
    # Prediction on labelled sets (replaces .evaluate)
    # ------------------------------------------------------------------
    def predict(
        self,
        X: np.ndarray,
        y: np.ndarray,
        *,
        threshold: Optional[float] = None,
    ) -> "ADConformal":
        """
        Predict intervals and compute metrics on a labelled set.

        This is the labelled counterpart of :meth:`width_score`. It:

        * computes prediction intervals and widths on ``(X, y)``,
        * defines an in-domain mask based on a width threshold, and
        * stores interval + regression metrics in :attr:`eval_metrics`.

        Metrics are reported:

        * over all samples (prefix ``all_``), and
        * over the in-domain subset (prefix ``in_``).

        The method also populates :attr:`last_predictions`.

        :param X: Evaluation features, shape ``(n_eval, n_features)``.
        :type X: numpy.ndarray
        :param y: Evaluation targets, shape ``(n_eval,)``.
        :type y: numpy.ndarray
        :param threshold: Optional custom width threshold. If ``None``,
            uses :attr:`width_threshold`.
        :type threshold: Optional[float]
        :return: The :class:`ADConformal` instance with updated
            :attr:`eval_metrics` and :attr:`last_predictions`.
        :rtype: ADConformal
        """
        if self.model_ is None:
            raise RuntimeError("ADConformal has not been fitted yet.")

        X = np.asarray(X)
        y = np.asarray(y)

        y_pred, y_lower, y_upper = self.model_.predict_with_interval(
            X, alpha=self.alpha
        )
        y_pred = np.asarray(y_pred)
        y_lower = np.asarray(y_lower)
        y_upper = np.asarray(y_upper)

        widths = (y_upper - y_lower).astype(float)

        thr = self._width_threshold if threshold is None else threshold
        if thr is None:
            raise RuntimeError("Width threshold is not set; fit ADConformal first.")
        thr = float(thr)

        mask = widths <= thr

        metrics_all = self._interval_metrics(
            y_true=y,
            y_pred=y_pred,
            y_lower=y_lower,
            y_upper=y_upper,
            prefix="all_",
        )
        metrics_in = self._interval_metrics(
            y_true=y[mask],
            y_pred=y_pred[mask],
            y_lower=y_lower[mask],
            y_upper=y_upper[mask],
            prefix="in_",
        )

        self._eval_metrics = {
            **metrics_all,
            **metrics_in,
            "in_coverage_fraction": float(mask.mean()),
            "in_n_samples": int(mask.sum()),
            "all_n_samples": int(mask.size),
        }

        # store last labelled prediction state
        self._last_y_true = y
        self._last_y_pred = y_pred
        self._last_y_lower = y_lower
        self._last_y_upper = y_upper
        self._last_widths = widths
        self._last_in_mask = mask

        return self

    # ------------------------------------------------------------------
    # Confident prediction on (typically) test sets
    # ------------------------------------------------------------------
    def predict_confident_with_threshold(
        self,
        X: np.ndarray,
        *,
        threshold: Optional[float] = None,
        quantile: Optional[float] = None,
    ) -> "ADConformal":
        """
        Predict intervals and select confident samples via a width cutoff.

        This method is designed for **test / deployment** scenarios:

        * You first derive an optimal width-based threshold from a
          calibration trade-off table (e.g. using
          :meth:`scan_width_tradeoff` and selecting a row with high
          score),
        * you then apply this threshold to a new set ``X`` via this
          method to obtain confident predictions.

        The method does **not** require target values and therefore does
        not compute regression metrics; instead it populates
        :attr:`confident_predictions`.

        Threshold selection logic
        -------------------------
        Exactly one of the following should be provided (or none to fall
        back to :attr:`width_threshold`):

        * ``threshold`` – direct width cutoff in target units,
        * ``quantile`` – calibration quantile in ``[0, 1]``; the actual
          cutoff is computed as
          ``quantile(self._width_cal, quantile)``,

        If both are ``None``, :attr:`width_threshold` is used.

        Typical usage with a precomputed trade-off table
        ------------------------------------------------

        For example, given a trade-off table from calibration::

            best = ad.tradeoff_table.loc[ad.tradeoff_table['score'].idxmax()]
            thr = float(best['threshold'])

        you can then apply this threshold on a test set::

            ad.predict_confident_with_threshold(X_test, threshold=thr)
            conf = ad.confident_predictions
            y_pred_confident = conf["y_pred"][conf["in_domain_mask"]]

        :param X: Feature matrix, shape ``(n_samples, n_features)``.
        :type X: numpy.ndarray
        :param threshold: Direct width threshold. If provided, overrides
            :attr:`width_threshold`.
        :type threshold: Optional[float]
        :param quantile: Calibration quantile in ``[0, 1]``. If
            provided, a fresh threshold is computed from calibration
            widths.
        :type quantile: Optional[float]
        :return: The :class:`ADConformal` instance with updated
            :attr:`confident_predictions`.
        :rtype: ADConformal
        """
        if self.model_ is None:
            raise RuntimeError("ADConformal has not been fitted yet.")

        if threshold is not None and quantile is not None:
            raise ValueError("Provide at most one of 'threshold' or 'quantile'.")

        X = np.asarray(X)

        if quantile is not None:
            if self._width_cal is None:
                raise RuntimeError(
                    "Calibration widths are not available; fit ADConformal first "
                    "before using quantile-based thresholds."
                )
            thr = float(np.quantile(self._width_cal, float(quantile)))
        elif threshold is not None:
            thr = float(threshold)
        else:
            if self._width_threshold is None:
                raise RuntimeError(
                    "Width threshold is not set; either call fit() or pass an "
                    "explicit threshold/quantile."
                )
            thr = float(self._width_threshold)

        y_pred, y_lower, y_upper = self.model_.predict_with_interval(
            X, alpha=self.alpha
        )
        y_pred = np.asarray(y_pred)
        y_lower = np.asarray(y_lower)
        y_upper = np.asarray(y_upper)

        widths = (y_upper - y_lower).astype(float)
        mask = widths <= thr

        self._conf_threshold = thr
        self._conf_y_pred = y_pred
        self._conf_y_lower = y_lower
        self._conf_y_upper = y_upper
        self._conf_widths = widths
        self._conf_mask = mask

        return self

    # ------------------------------------------------------------------
    # Width-based coverage–performance trade-off
    # ------------------------------------------------------------------
    def scan_width_tradeoff(
        self,
        X_eval: np.ndarray,
        y_eval: np.ndarray,
        *,
        quantiles: Optional[Sequence[float]] = None,
        score_type: str = "gmean",
        use_abs_pearson: bool = False,
        beta: float = 1.0,
        lambda_cov: float = 0.5,
    ) -> "ADConformal":
        """
        Scan coverage–performance trade-offs using width thresholds.

        Width thresholds are defined from **calibration widths** via
        quantiles, while metrics are computed on a separate evaluation
        set ``(X_eval, y_eval)``.

        Supported score types
        ---------------------
        * ``"gmean"``:
          ``sqrt(coverage * pearson_clipped)``
        * ``"f1"`` / ``"fbeta"``: F_beta-style combination of coverage
          and pearson_clipped (beta > 1 favours Pearson; beta < 1
          favours coverage)
        * ``"delta"``: compares against the no-AD baseline:

          * ``pearson_gain = pearson_in_domain - pearson_all``
          * ``coverage_loss = 1 - coverage``
          * ``score = pearson_gain - lambda_cov * coverage_loss``

          This tends to produce a **non-monotonic** trade-off curve and
          highlights intermediate thresholds where Pearson improves over
          baseline without sacrificing too much coverage.

        The resulting table can be used to pick a quantile / threshold,
        which can then be applied on an independent test set via
        :meth:`predict_confident_with_threshold`.

        :param X_eval: Evaluation features, shape
            ``(n_eval, n_features)``.
        :type X_eval: numpy.ndarray
        :param y_eval: Evaluation targets, shape ``(n_eval,)``.
        :type y_eval: numpy.ndarray
        :param quantiles: Sequence of calibration quantiles in ``[0, 1]``
            to scan. If ``None``, uses 20 values from 0.01 to 1.00
            inclusive.
        :type quantiles: Optional[Sequence[float]]
        :param score_type: Combination strategy: ``"gmean"``, ``"f1"``,
            ``"fbeta"``, or ``"delta"``.
        :type score_type: str
        :param use_abs_pearson: If ``True``, uses ``|r|`` instead of
            ``max(r, 0)`` when combining coverage and Pearson.
        :type use_abs_pearson: bool
        :param beta: F_beta parameter for ``"fbeta"`` mode.
        :type beta: float
        :param lambda_cov: Coverage penalty weight in ``"delta"`` mode.
        :type lambda_cov: float
        :return: The :class:`ADConformal` instance with updated
            :attr:`tradeoff_table`.
        :rtype: ADConformal
        """
        if self.model_ is None or self._width_cal is None:
            raise RuntimeError("ADConformal must be fitted on calibration first.")

        X_eval = np.asarray(X_eval)
        y_eval = np.asarray(y_eval)

        if quantiles is None:
            # include 1.00 to mirror calibration tables that run 0.01 → 1.00
            quantiles = np.linspace(0.01, 1.00, 20)
        quantiles = np.asarray(list(quantiles), dtype=float)

        y_pred_eval, y_lower_eval, y_upper_eval = self.model_.predict_with_interval(
            X_eval, alpha=self.alpha
        )
        y_pred_eval = np.asarray(y_pred_eval)
        y_lower_eval = np.asarray(y_lower_eval)
        y_upper_eval = np.asarray(y_upper_eval)

        width_eval = (y_upper_eval - y_lower_eval).astype(float)

        score_type_lower = score_type.lower()
        if score_type_lower not in {"gmean", "f1", "fbeta", "delta"}:
            raise ValueError("score_type must be 'gmean', 'f1', 'fbeta', or 'delta'.")

        beta2 = float(beta) ** 2

        # --- baseline metrics (no AD) for "delta" mode ---
        metrics_all = self._interval_metrics(
            y_true=y_eval,
            y_pred=y_pred_eval,
            y_lower=y_lower_eval,
            y_upper=y_upper_eval,
            prefix="all_",
        )
        pearson_all = metrics_all.get("all_pearson_r", np.nan)
        cov_all = 1.0  # by definition, using all points

        records = []
        for q in quantiles:
            thr = float(np.quantile(self._width_cal, q))
            mask = width_eval <= thr

            if mask.sum() == 0:
                records.append(
                    {
                        "quantile": q,
                        "threshold": thr,
                        "coverage": 0.0,
                        "coverage_interval": np.nan,
                        "pearson_r_in_domain": np.nan,
                        "spearman_rho_in_domain": np.nan,
                        "score": 0.0,
                        "n_in_domain": 0,
                    }
                )
                continue

            metrics_in = self._interval_metrics(
                y_true=y_eval[mask],
                y_pred=y_pred_eval[mask],
                y_lower=y_lower_eval[mask],
                y_upper=y_upper_eval[mask],
                prefix="in_",
            )

            pearson = metrics_in.get("in_pearson_r", np.nan)
            spearman = metrics_in.get("in_spearman_rho", np.nan)
            coverage = float(mask.mean())

            # effective pearson for gmean / fbeta
            if np.isnan(pearson):
                pearson_eff = 0.0
            else:
                pearson_eff = abs(pearson) if use_abs_pearson else max(pearson, 0.0)

            cov_c = float(np.clip(coverage, 0.0, 1.0))
            pear_c = float(np.clip(pearson_eff, 0.0, 1.0))

            if score_type_lower == "gmean":
                score = float(np.sqrt(cov_c * pear_c))
            elif score_type_lower in {"f1", "fbeta"}:
                denom = beta2 * cov_c + pear_c
                if denom == 0.0:
                    score = 0.0
                else:
                    score = float((1.0 + beta2) * cov_c * pear_c / denom)
            else:  # "delta"
                # compare against baseline (no AD)
                if np.isnan(pearson) or np.isnan(pearson_all):
                    pearson_gain = 0.0
                else:
                    pearson_gain = pearson - pearson_all

                coverage_loss = cov_all - coverage  # = 1 - coverage
                score = float(pearson_gain - lambda_cov * coverage_loss)

            records.append(
                {
                    "quantile": q,
                    "threshold": thr,
                    "coverage": coverage,
                    "coverage_interval": metrics_in.get("in_coverage", np.nan),
                    "pearson_r_in_domain": pearson,
                    "spearman_rho_in_domain": spearman,
                    "score": score,
                    "n_in_domain": int(mask.sum()),
                }
            )

        self._tradeoff_table = pd.DataFrame.from_records(records)
        return self
