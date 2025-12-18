from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    VotingRegressor,
    StackingRegressor,
)
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold

from .base import _BaseDockQModel
from ..metrics.metrics import regression_cv_summary
from .helpers import ArrayLike, MAPIERegressor, has_mapie_regression

try:  # optional XGBoost
    from xgboost import XGBRegressor  # type: ignore

    _HAS_XGB = True
except Exception:  # pragma: no cover - optional dependency
    XGBRegressor = None  # type: ignore
    _HAS_XGB = False


@dataclass
class DockQRegressor(_BaseDockQModel, BaseEstimator, RegressorMixin):
    """
    Flexible ensemble regressor + conformal prediction intervals for DockQ-like scores.

    Fixes included (vs. prior version):
    - Seeded CV objects for StackingRegressor and MAPIE (instead of passing cv=int).
    - Safe cloning of base estimators before constructing ensembles.
    - Optional central n_jobs control for base estimators / ensembles.

    Parameters
    ----------
    ensemble_type : str, optional
        Ensemble strategy, either ``"voting"`` (default) or ``"stacking"``.
    use_ridge, use_elasticnet, use_gb, use_rf, use_svr, use_xgb : bool, optional
        Enable/disable base learners.
    ...
    mapie_enabled : bool, optional
        If ``True``, attempt to fit MAPIE for conformal prediction intervals.
    cv_shuffle : bool, optional
        Whether internal CV splitters should shuffle. Default is ``True``.
        When ``True``, CV uses ``random_state`` for full reproducibility.
    n_jobs : int, optional
        Parallelism for estimators/ensembles when supported. Default is ``-1``.
        For strict bitwise reproducibility you can set ``n_jobs=1``.
    """

    # ------------------------------------------------------------------
    # Ensemble configuration
    # ------------------------------------------------------------------
    ensemble_type: str = "voting"  # "voting" | "stacking"

    use_ridge: bool = True
    use_elasticnet: bool = False
    use_gb: bool = True
    use_rf: bool = True
    use_svr: bool = False
    use_xgb: bool = False

    ridge_alpha: float = 1.0

    elasticnet_alpha: float = 1.0
    elasticnet_l1_ratio: float = 0.5

    rf_n_estimators: int = 500
    rf_max_depth: Optional[int] = None

    gb_n_estimators: int = 200
    gb_learning_rate: float = 0.05
    gb_max_depth: int = 3

    svr_C: float = 1.0
    svr_epsilon: float = 0.1
    svr_kernel: str = "rbf"

    xgb_n_estimators: int = 300
    xgb_learning_rate: float = 0.05
    xgb_max_depth: int = 4
    xgb_subsample: float = 0.8
    xgb_colsample_bytree: float = 0.8

    stack_final_estimator: str = "ridge"  # "ridge" | "gb" | "rf"
    mapie_enabled: bool = True

    # NEW: make internal CV deterministic
    cv_shuffle: bool = True

    # NEW: centralized parallelism control
    n_jobs: int = -1

    # ------------------------------------------------------------------
    # Internal state (set during fitting)
    # ------------------------------------------------------------------
    _mapie: Optional[MAPIERegressor] = field(default=None, init=False, repr=False)
    _reg: Optional[RegressorMixin] = field(default=None, init=False, repr=False)
    _cp_method_used: Optional[str] = field(default=None, init=False, repr=False)
    _base_estimators: List[Tuple[str, RegressorMixin]] = field(
        default_factory=list, init=False, repr=False
    )
    _last_evaluation: Optional[Dict[str, Any]] = field(
        default=None, init=False, repr=False
    )

    # ------------------------------------------------------------------
    # Representations
    # ------------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        base_flags = []
        if self.use_ridge:
            base_flags.append("ridge")
        if self.use_elasticnet:
            base_flags.append("elasticnet")
        if self.use_gb:
            base_flags.append("gb")
        if self.use_rf:
            base_flags.append("rf")
        if self.use_svr:
            base_flags.append("svr")
        if self.use_xgb:
            base_flags.append("xgb")

        bases = ",".join(base_flags) if base_flags else "none"

        return (
            f"{self.__class__.__name__}("
            f"ensemble_type={self.ensemble_type!r}, "
            f"bases=[{bases}], "
            f"n_splits={self.n_splits}, "
            f"n_repeats={self.n_repeats}, "
            f"random_state={self.random_state}, "
            f"default_alpha={self.default_alpha}, "
            f"cv_shuffle={self.cv_shuffle}, "
            f"n_jobs={self.n_jobs}, "
            f"cp_method_used={self._cp_method_used!r}, "
            f"is_fitted={self._is_fitted})"
        )

    # ------------------------------------------------------------------
    # CV helpers
    # ------------------------------------------------------------------
    def _make_kfold(self, *, n_splits: Optional[int] = None) -> KFold:
        """
        Build a deterministic KFold splitter.

        :param n_splits: Number of folds. If None, uses self.n_splits.
        :returns: KFold instance.
        """
        k = int(n_splits or self.n_splits)
        shuffle = bool(self.cv_shuffle)
        rs = self.random_state if shuffle else None
        return KFold(n_splits=k, shuffle=shuffle, random_state=rs)

    # ------------------------------------------------------------------
    # Base learners
    # ------------------------------------------------------------------
    def _make_ridge_pipeline(self) -> Pipeline:
        """Construct a StandardScaler + Ridge regression pipeline."""
        return Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "ridge",
                    Ridge(alpha=self.ridge_alpha, random_state=self.random_state),
                ),
            ]
        )

    def _make_elasticnet_pipeline(self) -> Pipeline:
        """Construct a StandardScaler + ElasticNet regression pipeline."""
        return Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "elasticnet",
                    ElasticNet(
                        alpha=self.elasticnet_alpha,
                        l1_ratio=self.elasticnet_l1_ratio,
                        random_state=self.random_state,
                    ),
                ),
            ]
        )

    def _make_svr_pipeline(self) -> Pipeline:
        """Construct a StandardScaler + SVR pipeline."""
        return Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                (
                    "svr",
                    SVR(C=self.svr_C, epsilon=self.svr_epsilon, kernel=self.svr_kernel),
                ),
            ]
        )

    def _make_base_estimators(self) -> List[Tuple[str, RegressorMixin]]:
        """
        Build the list of base estimators based on configuration flags.

        :returns: List of ``(name, estimator)`` tuples.
        :raises RuntimeError: If no base estimators are enabled.
        """
        estimators: List[Tuple[str, RegressorMixin]] = []

        if self.use_ridge:
            estimators.append(("ridge", self._make_ridge_pipeline()))
        if self.use_elasticnet:
            estimators.append(("elasticnet", self._make_elasticnet_pipeline()))
        if self.use_gb:
            estimators.append(
                (
                    "gb",
                    GradientBoostingRegressor(
                        n_estimators=self.gb_n_estimators,
                        learning_rate=self.gb_learning_rate,
                        max_depth=self.gb_max_depth,
                        random_state=self.random_state,
                    ),
                )
            )
        if self.use_rf:
            estimators.append(
                (
                    "rf",
                    RandomForestRegressor(
                        n_estimators=self.rf_n_estimators,
                        max_depth=self.rf_max_depth,
                        random_state=self.random_state,
                        n_jobs=self.n_jobs,
                    ),
                )
            )
        if self.use_svr:
            estimators.append(("svr", self._make_svr_pipeline()))
        if self.use_xgb:
            if not _HAS_XGB:
                raise RuntimeError(
                    "use_xgb=True but xgboost is not installed. "
                    "Install it with `pip install xgboost`."
                )
            estimators.append(
                (
                    "xgb",
                    XGBRegressor(
                        n_estimators=self.xgb_n_estimators,
                        learning_rate=self.xgb_learning_rate,
                        max_depth=self.xgb_max_depth,
                        subsample=self.xgb_subsample,
                        colsample_bytree=self.xgb_colsample_bytree,
                        random_state=self.random_state,
                        n_jobs=self.n_jobs,
                    ),
                )
            )

        if not estimators:
            raise RuntimeError(
                "No base estimators are enabled. Enable at least one of "
                "use_ridge/use_elasticnet/use_gb/use_rf/use_svr/use_xgb."
            )

        # store the “template” estimators for introspection
        self._base_estimators = estimators
        return estimators

    def _make_stack_final_estimator(self) -> RegressorMixin:
        """
        Build final estimator for stacking.

        :returns: Configured final estimator.
        :raises ValueError: If ``stack_final_estimator`` is invalid.
        """
        if self.stack_final_estimator == "ridge":
            return Ridge(alpha=self.ridge_alpha, random_state=self.random_state)
        if self.stack_final_estimator == "gb":
            return GradientBoostingRegressor(
                n_estimators=self.gb_n_estimators,
                learning_rate=self.gb_learning_rate,
                max_depth=self.gb_max_depth,
                random_state=self.random_state,
            )
        if self.stack_final_estimator == "rf":
            return RandomForestRegressor(
                n_estimators=self.rf_n_estimators,
                max_depth=self.rf_max_depth,
                random_state=self.random_state,
                n_jobs=self.n_jobs,
            )
        raise ValueError(
            "stack_final_estimator must be one of {'ridge', 'gb', 'rf'}, "
            f"got {self.stack_final_estimator!r}."
        )

    def _make_ensemble_estimator(self) -> RegressorMixin:
        """
        Build the configured ensemble estimator.

        Important: uses cloned base estimators so repeated calls are safe and
        do not share fitted state.
        """
        base_estimators = self._make_base_estimators()
        estimators = [(name, clone(est)) for name, est in base_estimators]

        if self.ensemble_type == "voting":
            return VotingRegressor(estimators=estimators)

        if self.ensemble_type == "stacking":
            final_est = self._make_stack_final_estimator()
            return StackingRegressor(
                estimators=estimators,
                final_estimator=final_est,
                cv=self._make_kfold(n_splits=self.n_splits),  # ✅ seeded CV
                n_jobs=self.n_jobs,
                passthrough=False,
            )

        raise ValueError(
            "ensemble_type must be 'voting' or 'stacking', "
            f"got {self.ensemble_type!r}."
        )

    # ------------------------------------------------------------------
    # Internal helpers for X, y
    # ------------------------------------------------------------------
    def _prepare_xy(
        self,
        X: ArrayLike,
        y: Optional[Sequence] = None,
        target_col: str = "target",
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Normalise X, y input for fit into numpy arrays and set feature names.
        """
        if isinstance(X, pd.DataFrame) and y is None:
            if target_col not in X.columns:
                raise ValueError(
                    f"Target column '{target_col}' not found in dataframe."
                )
            self._feature_names = [c for c in X.columns if c != target_col]
            X_arr = X[self._feature_names].values
            y_arr = X[target_col].astype(float).values
            return X_arr, y_arr

        if y is None:
            raise ValueError(
                "When y is None, X must be a DataFrame with target_col present."
            )

        if isinstance(X, pd.DataFrame):
            self._feature_names = list(X.columns)
            X_arr = X.values
        else:
            X_arr = np.asarray(X)
            if X_arr.ndim == 1:
                X_arr = X_arr.reshape(-1, 1)
            n_features = X_arr.shape[1]
            self._feature_names = [f"f{i}" for i in range(n_features)]

        y_arr = np.asarray(y).astype(float).ravel()
        return X_arr, y_arr

    def _ensure_feature_array(self, X: ArrayLike) -> np.ndarray:
        """Convert input ``X`` at prediction time to a numpy array with correct shape."""
        self._check_is_fitted()
        n_features = len(self._feature_names)

        if isinstance(X, pd.DataFrame):
            missing = [c for c in self._feature_names if c not in X.columns]
            if missing:
                raise ValueError(
                    f"Missing feature columns at prediction time: {missing}"
                )
            X_arr = X[self._feature_names].values
        else:
            X_arr = np.asarray(X)
            if X_arr.ndim == 1:
                X_arr = X_arr.reshape(-1, n_features)
            if X_arr.shape[1] != n_features:
                raise ValueError(
                    f"Expected X with {n_features} features, got shape {X_arr.shape}"
                )
        return X_arr

    # ------------------------------------------------------------------
    # Fit
    # ------------------------------------------------------------------
    def fit(
        self,
        X: ArrayLike,
        y: Optional[Sequence] = None,
        target_col: str = "target",
        n_jobs: int = 8,
    ) -> DockQRegressor:
        """
        Fit the regression ensemble (and MAPIE, if enabled and available).

        :param X: Input data (DataFrame or array-like).
        :param y: Target values for array mode; ignored in DataFrame mode.
        :param target_col: Target column name in DataFrame mode.
        :param n_jobs: Parallelism for MAPIE only (kept for backwards compatibility).
        :returns: self
        """
        X_arr, y_arr = self._prepare_xy(X, y=y, target_col=target_col)

        # CV summary (already uses seeded splitter internally via random_state)
        base_estimator = self._make_ensemble_estimator()
        self._cv_summary = regression_cv_summary(
            base_estimator,
            X_arr,
            y_arr,
            n_splits=self.n_splits,
            n_repeats=self.n_repeats,
            random_state=self.random_state,
        )

        # MAPIE conformal regressor (optional) with seeded CV
        self._mapie = None
        self._cp_method_used = None
        if self.mapie_enabled and has_mapie_regression():
            cv = self._make_kfold(n_splits=self.n_splits)  # ✅ seeded CV for MAPIE
            try:
                mapie = MAPIERegressor(
                    estimator=self._make_ensemble_estimator(),
                    cv=cv,
                    method="plus",
                    n_jobs=n_jobs,
                )
                mapie.fit(X_arr, y_arr)
                self._cp_method_used = "plus"
            except Exception:
                mapie = MAPIERegressor(
                    estimator=self._make_ensemble_estimator(),
                    cv=cv,
                    method="naive",
                    n_jobs=n_jobs,
                )
                mapie.fit(X_arr, y_arr)
                self._cp_method_used = "naive"
            self._mapie = mapie

        # Final fit for point predictor
        reg = self._make_ensemble_estimator()
        reg.fit(X_arr, y_arr)
        self._reg = reg

        self._is_fitted = True
        return self

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def mapie_model_(self) -> MAPIERegressor:
        """Underlying MAPIE regressor."""
        self._check_is_fitted()
        if self._mapie is None:
            raise RuntimeError("MAPIE is not available or was not fitted.")
        return self._mapie

    @property
    def cp_method_used_(self) -> Optional[str]:
        """Conformal prediction method used by MAPIE (e.g. ``'plus'`` or ``'naive'``)."""
        return self._cp_method_used

    @property
    def base_estimators_(self) -> List[Tuple[str, RegressorMixin]]:
        """Base estimators used in the ensemble (templates)."""
        return list(self._base_estimators)

    @property
    def feature_importances_(self) -> pd.Series:
        """
        Aggregate feature importances across tree-based base learners.

        :returns: Mean importance per feature.
        :raises RuntimeError: If no base estimator exposes `feature_importances_`.
        """
        self._check_is_fitted()
        if self._reg is None:
            raise RuntimeError("Internal regressor is not fitted.")

        def _extract_importances(est: Any) -> Optional[np.ndarray]:
            if hasattr(est, "feature_importances_"):
                return np.asarray(est.feature_importances_)
            if isinstance(est, Pipeline):
                last = est.steps[-1][1]
                if hasattr(last, "feature_importances_"):
                    return np.asarray(last.feature_importances_)
            return None

        importances: List[np.ndarray] = []

        if hasattr(self._reg, "estimators_"):
            for est in self._reg.estimators_:
                imp = _extract_importances(est)
                if imp is not None:
                    importances.append(imp)

        if not importances:
            raise RuntimeError(
                "No base estimator exposes `feature_importances_`. "
                "Enable tree-based models (GB/RF/XGB) to use this property."
            )

        imp_arr = np.stack(importances, axis=0)
        mean_imp = imp_arr.mean(axis=0)
        return pd.Series(mean_imp, index=self._feature_names)

    @property
    def last_evaluation_(self) -> Optional[Dict[str, Any]]:
        """Last evaluation results recorded by :meth:`evaluate`."""
        return self._last_evaluation

    # ------------------------------------------------------------------
    # Prediction helpers
    # ------------------------------------------------------------------
    def predict(self, X: ArrayLike) -> np.ndarray:
        """Predict continuous scores for new samples."""
        self._check_is_fitted()
        if self._reg is None:
            raise RuntimeError("Internal regressor is not fitted.")
        X_arr = self._ensure_feature_array(X)
        return self._reg.predict(X_arr)

    def fit_predict(
        self,
        X: ArrayLike,
        y: Optional[Sequence] = None,
        target_col: str = "target",
    ) -> np.ndarray:
        """Fit the model and immediately return predictions on the same data."""
        self.fit(X, y=y, target_col=target_col)
        return self.predict(X)

    def predict_with_interval(
        self,
        X: ArrayLike,
        alpha: Optional[float] = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Predict values and conformal prediction intervals via MAPIE."""
        self._check_is_fitted()
        if self._mapie is None:
            raise RuntimeError("MAPIE is not available or was not fitted.")

        if alpha is None:
            alpha = self.default_alpha

        X_arr = self._ensure_feature_array(X)
        y_pred, y_interval = self._mapie.predict(X_arr, alpha=[alpha])
        y_lower = y_interval[:, 0, 0]
        y_upper = y_interval[:, 1, 0]
        return y_pred, y_lower, y_upper

    # ------------------------------------------------------------------
    # Evaluation helpers
    # ------------------------------------------------------------------
    def evaluate(
        self,
        X: ArrayLike,
        y: Optional[Sequence] = None,
        *,
        df_mode_target_col: str = "target",
        alpha: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Evaluate regression metrics and interval coverage."""
        self._check_is_fitted()
        if alpha is None:
            alpha = self.default_alpha

        if isinstance(X, pd.DataFrame) and y is None:
            if df_mode_target_col not in X.columns:
                raise ValueError(
                    f"Target column '{df_mode_target_col}' not found in dataframe."
                )
            y_true = X[df_mode_target_col].astype(float).values
            X_feat = X[self._feature_names]
        else:
            if y is None:
                raise ValueError("y must be provided in array mode.")
            X_feat = X
            y_true = np.asarray(y).astype(float).ravel()

        y_pred = self.predict(X_feat)
        mae = float(mean_absolute_error(y_true, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        r2 = float(r2_score(y_true, y_pred))

        results: Dict[str, Any] = {
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
            "n_samples": int(len(y_true)),
        }

        if self._mapie is not None:
            _, y_lo, y_hi = self.predict_with_interval(X_feat, alpha=alpha)
            within = (y_true >= y_lo) & (y_true <= y_hi)
            results["interval_coverage"] = float(np.mean(within))
            results["interval_width_mean"] = float(np.mean(y_hi - y_lo))
        else:
            results["interval_coverage"] = float("nan")
            results["interval_width_mean"] = float("nan")

        self._last_evaluation = results
        return results
