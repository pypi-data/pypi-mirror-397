from __future__ import annotations

from typing import Dict, Any, List, Optional, Sequence, Mapping
from copy import deepcopy
import os

import numpy as np
import pandas as pd
from sklearn.base import clone, RegressorMixin
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.utils import check_random_state

from pepq.metrics.metrics import MetricsCalculator


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------


class MultiModelRepeatedRegressor:
    """
    Repeated hold-out evaluation for a pool of regression models.

    This class runs multiple random train/test splits and evaluates a
    **fixed pool of regressors** (by default::

        ['Ridge', 'KNN', 'SVM', 'RF', 'GB']

    For each ``repeat × model`` combination it stores:

    * scalar metrics (Pearson, Spearman, R², MAE, RMSE),
    * the test indices (original DataFrame index),
    * ``y_test`` / ``y_pred``,
    * the processed ``X_test`` features.

    Results are exposed via :attr:`metrics_df` and
    :meth:`raw_predictions_df`.

    The API follows a fluent style: :meth:`fit` returns ``self``.

    :param model_pool:
        Mapping from model names to regressor instances. If ``None``,
        a default pool (Ridge, KNN, SVR, RF, GB) is used.
    :type model_pool: Optional[Mapping[str, RegressorMixin]]
    :param n_repeats:
        Number of random train/test splits to run.
    :type n_repeats: int
    :param test_size:
        Fraction of samples used as test set in each split.
    :type test_size: float
    :param random_state:
        Seed or :class:`numpy.random.RandomState` seed for reproducibility.
    :type random_state: Optional[int]
    """

    DEFAULT_MODEL_POOL: Dict[str, RegressorMixin] = {
        "Ridge": Ridge(),
        "KNN": KNeighborsRegressor(),
        "SVM": SVR(),
        "RF": RandomForestRegressor(n_estimators=100),
        "GB": GradientBoostingRegressor(n_estimators=100),
    }

    def __init__(
        self,
        model_pool: Optional[Mapping[str, RegressorMixin]] = None,
        n_repeats: int = 5,
        test_size: float = 0.2,
        random_state: Optional[int] = None,
    ) -> None:
        self.model_pool: Dict[str, RegressorMixin] = (
            deepcopy(dict(model_pool))
            if model_pool is not None
            else deepcopy(self.DEFAULT_MODEL_POOL)
        )
        self.n_repeats = int(n_repeats)
        self.test_size = float(test_size)
        self.random_state = random_state

        # Internal storage
        self._runs: List[Dict[str, Any]] = []
        self._fitted: bool = False

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def fit(
        self,
        df: pd.DataFrame,
        target_key: str,
        feature_cols: Optional[Sequence[str]] = None,
    ) -> "MultiModelRepeatedRegressor":
        """
        Run the repeated train/test evaluation on a DataFrame.

        :param df:
            Input DataFrame containing features and target column.
        :type df: pandas.DataFrame
        :param target_key:
            Name of the target column in ``df``.
        :type target_key: str
        :param feature_cols:
            Optional subset of columns to use as features. If ``None``,
            all columns except ``target_key`` are used.
        :type feature_cols: Optional[Sequence[str]]
        :returns: Self.
        :rtype: MultiModelRepeatedRegressor
        :raises KeyError:
            If ``target_key`` is not a column in ``df``.
        :raises ValueError:
            If no features remain after preprocessing.
        """
        if target_key not in df.columns:
            raise KeyError(
                f"target_key {target_key!r} not present in DataFrame columns."
            )

        X_df = (
            df.drop(columns=[target_key])
            if feature_cols is None
            else df.loc[:, feature_cols]
        )
        y = df[target_key].values

        # One-hot encode categoricals while preserving original index
        X_proc = pd.get_dummies(X_df, drop_first=True)
        if X_proc.shape[1] == 0:
            raise ValueError(
                "No features after preprocessing. Check input DataFrame / feature_cols."
            )

        # Series indexed by X_proc.index for clean index-based selection
        y_indexed = pd.Series(y, index=X_proc.index)

        rng = check_random_state(self.random_state)
        self._runs = []

        for repeat in range(self.n_repeats):
            seed = int(rng.randint(0, 2**31 - 1))

            idx = X_proc.index.to_numpy()
            train_idx, test_idx = train_test_split(
                idx,
                test_size=self.test_size,
                random_state=seed,
                shuffle=True,
            )

            X_train = X_proc.loc[train_idx]
            X_test = X_proc.loc[test_idx]
            y_train = y_indexed.loc[train_idx].to_numpy()
            y_test = y_indexed.loc[test_idx].to_numpy()

            for model_name, base_model in self.model_pool.items():
                run_entry = self._run_single_model(
                    model_name=model_name,
                    base_model=base_model,
                    repeat=repeat,
                    seed=seed,
                    X_train=X_train,
                    y_train=y_train,
                    X_test=X_test,
                    y_test=y_test,
                    test_idx=test_idx,
                )
                self._runs.append(run_entry)

        self._fitted = True
        return self

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _run_single_model(
        self,
        *,
        model_name: str,
        base_model: RegressorMixin,
        repeat: int,
        seed: int,
        X_train: pd.DataFrame,
        y_train: np.ndarray,
        X_test: pd.DataFrame,
        y_test: np.ndarray,
        test_idx: np.ndarray,
    ) -> Dict[str, Any]:
        """
        Fit a single model on one split and collect metrics/raw data.
        """
        model: RegressorMixin = clone(base_model)

        # Set random_state if available for reproducibility
        if hasattr(model, "random_state"):
            try:
                setattr(model, "random_state", int(seed))
            except Exception:
                pass

        model.fit(X_train, y_train)
        y_pred = np.asarray(model.predict(X_test), dtype=float)

        mc = MetricsCalculator().fit(y_test, y_pred)
        meta: Dict[str, Any] = {
            "repeat": int(repeat),
            "seed": int(seed),
            "model": model_name,
            "n_train": int(X_train.shape[0]),
            "n_test": int(X_test.shape[0]),
            **mc.metrics,
        }

        run_entry: Dict[str, Any] = {
            "meta": meta,
            "test_index": np.asarray(test_idx).copy(),
            "y_test": np.asarray(y_test).copy(),
            "y_pred": y_pred.copy(),
            "X_test": X_test.copy(),
        }
        return run_entry

    # ------------------------------------------------------------------
    # Properties and outputs
    # ------------------------------------------------------------------

    @property
    def fitted(self) -> bool:
        """
        Whether :meth:`fit` has been called successfully.

        :rtype: bool
        """
        return self._fitted

    @property
    def n_models(self) -> int:
        """
        Number of models in the pool.

        :rtype: int
        """
        return len(self.model_pool)

    @property
    def model_names(self) -> List[str]:
        """
        Names of models in the pool in arbitrary order.

        :rtype: List[str]
        """
        return list(self.model_pool.keys())

    @property
    def metrics_df(self) -> pd.DataFrame:
        """
        Aggregated metrics per ``repeat × model``.

        The resulting DataFrame contains at least the columns:

        ``['repeat', 'seed', 'model', 'n_train', 'n_test',
        'pearson', 'spearman', 'r2', 'mae', 'rmse']``.

        :rtype: pandas.DataFrame
        """
        if not self._fitted:
            return pd.DataFrame()
        rows = [r["meta"] for r in self._runs]
        return (
            pd.DataFrame(rows).sort_values(["repeat", "model"]).reset_index(drop=True)
        )

    def raw_predictions_df(self, include_features: bool = True) -> pd.DataFrame:
        """
        Long-form table with per-sample predictions across all runs.

        Columns:

        * ``repeat``, ``seed``, ``model``, ``row_index``
        * ``y_true``, ``y_pred``
        * plus feature columns prefixed with ``'feat__'`` when
          ``include_features=True``.

        :param include_features:
            If ``True``, include processed feature columns with
            ``'feat__'`` prefix.
        :type include_features: bool
        :returns: Long-form DataFrame with one row per test sample per run.
        :rtype: pandas.DataFrame
        """
        if not self._fitted:
            return pd.DataFrame()

        rows: List[Dict[str, Any]] = []

        for r in self._runs:
            meta = r["meta"]
            model_name = meta["model"]
            repeat = meta["repeat"]
            seed = meta["seed"]
            X_test = r["X_test"]
            y_test = r["y_test"]
            y_pred = r["y_pred"]
            test_idx = r["test_index"]

            # rely on positional alignment: j-th row ↔ j-th test_idx
            for j, row_id in enumerate(test_idx):
                base: Dict[str, Any] = {
                    "repeat": int(repeat),
                    "seed": int(seed),
                    "model": model_name,
                    "row_index": int(row_id),
                    "y_true": float(y_test[j]),
                    "y_pred": float(y_pred[j]),
                }
                if include_features:
                    feat_row = X_test.iloc[j].to_dict()
                    prefixed = {f"feat__{k}": v for k, v in feat_row.items()}
                    base.update(prefixed)
                rows.append(base)

        return pd.DataFrame(rows)

    def save_raw_predictions_csv(
        self,
        path: str = "/mnt/data/raw_predictions.csv",
        include_features: bool = True,
    ) -> str:
        """
        Save raw per-sample predictions to CSV and return the sandbox path.

        :param path:
            Output CSV path. Parent directories are created if needed.
        :type path: str
        :param include_features:
            Whether to include feature columns in the saved file.
        :type include_features: bool
        :returns:
            Sandbox path (``'sandbox:...'``) to the created CSV file.
        :rtype: str
        """
        df = self.raw_predictions_df(include_features=include_features)
        dirname = os.path.dirname(path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)
        df.to_csv(path, index=False)
        return f"sandbox:{path}"

    # ------------------------------------------------------------------
    # Dunder methods
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """
        Number of run entries stored (``n_repeats × n_models``).

        :rtype: int
        """
        return len(self._runs)

    def __repr__(self) -> str:
        status = "fitted" if self._fitted else "unfitted"
        return (
            f"{self.__class__.__name__}("
            f"n_models={len(self.model_pool)}, "
            f"n_repeats={self.n_repeats}, "
            f"test_size={self.test_size}, "
            f"state={status})"
        )
