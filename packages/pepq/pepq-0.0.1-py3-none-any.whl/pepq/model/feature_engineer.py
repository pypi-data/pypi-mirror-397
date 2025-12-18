from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RepeatedKFold
from sklearn.metrics import (
    r2_score,
    mean_squared_error,
    mean_absolute_error,
)

try:
    from tqdm.auto import tqdm
except Exception:  # pragma: no cover

    def tqdm(x, **kwargs):
        return x  # fallback: no progress bar


ArrayLike = Union[np.ndarray, pd.DataFrame]


@dataclass
class FeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Feature engineering and selection using an embedded estimator.

    This transformer runs a repeated K-fold cross-validation loop with a
    user-provided estimator (default: :class:`RandomForestRegressor`),
    ranks features by importance, and optionally generates non-linear
    features (squares and pairwise products). It follows a scikit-learn
    style API with :meth:`fit`, :meth:`transform` and
    :meth:`fit_transform`.

    The estimator must expose a ``feature_importances_`` attribute after
    fitting (e.g. tree-based methods). During fitting:

    * For each CV split, the estimator is cloned and fitted.
    * A score is computed on the validation fold using the selected
      ``scoring`` metric.
    * Feature importances are collected across folds.
    * The best model (highest validation score) is stored as
      :pyattr:`best_model_`.

    After fitting, feature importances are averaged and a subset of
    features is chosen according to ``top_k`` or
    ``importance_threshold``. The transformer then:

    * Selects these features on :meth:`transform`.
    * Optionally adds quadratic features (x**2).
    * Optionally adds pairwise interaction features (x_i * x_j).

    Parameters
    ----------
    estimator : BaseEstimator or None
        Base estimator with a ``fit`` and ``predict`` method and a
        ``feature_importances_`` attribute. If ``None``, a
        :class:`RandomForestRegressor` with ``n_estimators`` and
        ``max_depth`` from the current instance is used.
    scoring : str
        Scoring metric used to evaluate validation folds. Supported
        values are:

        * ``'r2'`` – R² score (higher is better).
        * ``'neg_mean_squared_error'`` – negative MSE (higher is better).
        * ``'neg_mean_absolute_error'`` – negative MAE (higher is better).

    n_splits : int
        Number of splits for K-fold cross-validation. Default is 5.
    n_repeats : int
        Number of repeats for repeated K-fold cross-validation.
        Default is 5.
    n_jobs : int or None
        Number of parallel jobs for the default RandomForestRegressor.
        Passed directly to :class:`~sklearn.ensemble.RandomForestRegressor`.
        Ignored if a custom estimator is supplied. If ``None``, sklearn's
        default is used.
    random_state : int or None
        Random seed for cross-validation splitting and the default
        random forest. If ``None``, randomness is not fixed.
    n_estimators : int
        Number of trees in the default random forest.
    max_depth : int or None
        Maximum depth of each tree in the default random forest.
    top_k : int or None
        If not ``None``, keep only the top-k features ranked by mean
        feature importance. If ``None``, all features that pass
        ``importance_threshold`` are kept.
    importance_threshold : float
        Relative threshold for feature selection, interpreted as a
        fraction of the maximum importance (e.g. 0.1 keeps all features
        with importance >= 0.1 * max_importance). Ignored if ``top_k``
        is not ``None``.
    generate_quadratic : bool
        Whether to add squared features (x**2) for the selected features.
    generate_interactions : bool
        Whether to add pairwise product features (x_i * x_j) between
        the most important selected features.
    max_interaction_features : int
        Upper bound on the number of base features used to construct
        interaction terms. The transformer will choose the minimum of
        (number of selected features, max_interaction_features) and
        generate all pairwise products between them.
    show_progress : bool
        If ``True``, show a progress bar over CV folds using tqdm.

    Attributes
    ----------
    best_model_ : BaseEstimator
        Estimator fitted on the best validation fold (highest score).
    feature_importances_ : np.ndarray of shape (n_features_,)
        Mean feature importances across all cross-validation fits.
    selected_indices_ : np.ndarray of shape (n_selected_features_,)
        Indices of the original features that are kept.
    selected_feature_names_ : list of str
        Names of the selected original features.
    generated_feature_names_ : list of str
        Names of the additional generated features (quadratic and
        interaction terms).
    input_feature_names_ : list of str
        Names of the input features inferred during fitting.
    cv_scores_ : list of float
        List of scores on each validation fold.
    is_fitted_ : bool
        Flag indicating whether :meth:`fit` has been called.

    Examples
    --------
    Basic DockQ regression with PLDDT/PTM features::

        from pepq.model.feature_engineering import FeatureEngineer

        cols = [
            "prot_plddt", "pep_plddt", "PTM", "PAE",
            "iptm", "composite_ptm", "actifptm",
        ]
        X = df[cols]
        y = df["dockq"]

        fe = FeatureEngineer(
            estimator=None,            # use default RandomForestRegressor
            scoring="r2",
            n_splits=5,
            n_repeats=5,
            n_jobs=-1,
            top_k=5,
            generate_quadratic=True,
            generate_interactions=True,
            max_interaction_features=5,
            random_state=42,
            show_progress=True,
        )

        fe.fit(X, y)
        X_fe = fe.transform(X)

        best_model = fe.best_model
        mean_score, std_score = fe.cv_score
        print("CV R2: %.3f ± %.3f" % (mean_score, std_score))

    Passing a custom estimator (e.g. GradientBoostingRegressor)::

        from sklearn.ensemble import GradientBoostingRegressor

        gbr = GradientBoostingRegressor(random_state=0)
        fe = FeatureEngineer(
            estimator=gbr,
            scoring="neg_mean_squared_error",
            top_k=3,
        )
        X_fe = fe.fit_transform(X, y)
    """

    estimator: Optional[BaseEstimator] = None
    scoring: str = "r2"

    n_splits: int = 5
    n_repeats: int = 5
    n_jobs: Optional[int] = None
    random_state: Optional[int] = None

    # Only used when estimator is None (default RF baseline)
    n_estimators: int = 300
    max_depth: Optional[int] = None

    top_k: Optional[int] = None
    importance_threshold: float = 0.0
    generate_quadratic: bool = True
    generate_interactions: bool = True
    max_interaction_features: int = 8
    show_progress: bool = True

    # Internal state (set in fit)
    best_model_: Optional[BaseEstimator] = field(init=False, default=None)
    feature_importances_: Optional[np.ndarray] = field(init=False, default=None)
    selected_indices_: Optional[np.ndarray] = field(init=False, default=None)
    selected_feature_names_: List[str] = field(init=False, default_factory=list)
    generated_feature_names_: List[str] = field(init=False, default_factory=list)
    input_feature_names_: List[str] = field(init=False, default_factory=list)
    cv_scores_: List[float] = field(init=False, default_factory=list)
    is_fitted_: bool = field(init=False, default=False)

    # ------------------------------------------------------------------
    # Representation helpers
    # ------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"estimator={self.estimator.__class__.__name__}, "
            f"scoring='{self.scoring}', "
            f"n_splits={self.n_splits}, "
            f"n_repeats={self.n_repeats}, "
            f"top_k={self.top_k}, "
            f"importance_threshold={self.importance_threshold}, "
            f"generate_quadratic={self.generate_quadratic}, "
            f"generate_interactions={self.generate_interactions}, "
            f"max_interaction_features={self.max_interaction_features}"
            ")"
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def best_model(self) -> BaseEstimator:
        """
        Best estimator found during cross-validation.

        :returns: Fitted estimator with highest validation score.
        :rtype: BaseEstimator
        :raises RuntimeError: If the transformer has not been fitted yet.
        """
        if not self.is_fitted_ or self.best_model_ is None:
            raise RuntimeError("FeatureEngineer has not been fitted yet.")
        return self.best_model_

    @property
    def selected_features(self) -> List[str]:
        """
        Names of the selected original features.

        :returns: List of selected feature names.
        :rtype: list[str]
        :raises RuntimeError: If the transformer has not been fitted yet.
        """
        if not self.is_fitted_:
            raise RuntimeError("FeatureEngineer has not been fitted yet.")
        return list(self.selected_feature_names_)

    @property
    def all_output_feature_names(self) -> List[str]:
        """
        Names of all output features after :meth:`transform`.

        This includes both selected original features and generated
        quadratic / interaction features.

        :returns: List of output feature names.
        :rtype: list[str]
        :raises RuntimeError: If the transformer has not been fitted yet.
        """
        if not self.is_fitted_:
            raise RuntimeError("FeatureEngineer has not been fitted yet.")
        return self.selected_feature_names_ + self.generated_feature_names_

    @property
    def cv_score(self) -> Tuple[float, float]:
        """
        Cross-validation score summary (mean ± std).

        The scores are computed on validation folds using the selected
        ``scoring`` metric (e.g. R², negative MSE).

        :returns: Tuple of (mean_score, std_score).
        :rtype: tuple[float, float]
        :raises RuntimeError: If the transformer has not been fitted yet.
        """
        if not self.is_fitted_ or not self.cv_scores_:
            raise RuntimeError("FeatureEngineer has not been fitted yet.")
        scores = np.asarray(self.cv_scores_, dtype=float)
        return float(scores.mean()), float(scores.std(ddof=1))

    # ------------------------------------------------------------------
    # Core sklearn-like API
    # ------------------------------------------------------------------
    def fit(self, X: ArrayLike, y: ArrayLike) -> FeatureEngineer:
        """
        Fit the feature engineer on the provided data.

        This runs repeated K-fold cross-validation with the internal
        estimator, aggregates feature importances, selects features, and
        prepares the rules for feature generation.

        :param X: Input features, either a pandas DataFrame or a NumPy array.
        :type X: ArrayLike
        :param y: Target values (e.g. DockQ scores).
        :type y: ArrayLike
        :returns: Self instance with fitted internal state.
        :rtype: FeatureEngineer
        :raises ValueError: If the shapes of ``X`` and ``y`` are incompatible.
        :raises ValueError: If the estimator does not expose
            ``feature_importances_`` after fitting.
        """
        X_arr, feature_names = self._to_array_and_names(X)
        y_arr = np.asarray(y)

        if X_arr.shape[0] != y_arr.shape[0]:
            raise ValueError(
                f"Inconsistent shapes: X has {X_arr.shape[0]} rows, "
                f"y has {y_arr.shape[0]} entries."
            )

        self.input_feature_names_ = feature_names

        rkf = RepeatedKFold(
            n_splits=self.n_splits,
            n_repeats=self.n_repeats,
            random_state=self.random_state,
        )

        splits = list(rkf.split(X_arr))
        n_folds = len(splits)

        all_importances: List[np.ndarray] = []
        self.cv_scores_ = []
        best_score: float = -np.inf
        best_model: Optional[BaseEstimator] = None

        scorer = self._get_scorer()

        iterator = (
            tqdm(
                splits,
                total=n_folds,
                desc="FeatureEngineer CV",
            )
            if self.show_progress
            else splits
        )

        for fold_idx, (train_idx, val_idx) in enumerate(iterator, start=1):
            X_tr, X_val = X_arr[train_idx], X_arr[val_idx]
            y_tr, y_val = y_arr[train_idx], y_arr[val_idx]

            # Clone estimator for each fold
            est = self._make_estimator()
            est.fit(X_tr, y_tr)

            if not hasattr(est, "feature_importances_"):
                raise ValueError(
                    "Estimator does not expose `feature_importances_`. "
                    "Please supply a tree-based model or compatible estimator."
                )

            y_pred = est.predict(X_val)
            score = scorer(y_val, y_pred)

            self.cv_scores_.append(float(score))
            all_importances.append(np.asarray(est.feature_importances_, dtype=float))

            if score > best_score:
                best_score = float(score)
                best_model = est

        self.best_model_ = best_model
        self.feature_importances_ = np.mean(np.vstack(all_importances), axis=0)

        # Feature selection + generation bookkeeping
        self._select_features()
        self._prepare_generated_feature_names()

        self.is_fitted_ = True
        return self

    def transform(self, X: ArrayLike) -> ArrayLike:
        """
        Transform new data using the fitted rules.

        The transformation performs:

        #. Selection of the subset of original features determined
           during :meth:`fit`.
        #. Optional quadratic features (x**2) for these selected features.
        #. Optional pairwise interaction features (x_i * x_j) for the
           most important selected features.

        The output type matches the input type: if ``X`` is a
        :class:`pandas.DataFrame`, a DataFrame is returned; otherwise
        a :class:`numpy.ndarray` is returned.

        :param X: New input data with the same columns / order as used
            during fitting.
        :type X: ArrayLike
        :returns: Transformed feature matrix.
        :rtype: ArrayLike
        :raises RuntimeError: If the transformer has not been fitted yet.
        """
        if not self.is_fitted_:
            raise RuntimeError(
                "FeatureEngineer has not been fitted yet. Call `fit` first."
            )

        X_arr, _ = self._to_array_and_names(X, expect_names=self.input_feature_names_)

        # 1) select base features
        X_base = X_arr[:, self.selected_indices_]

        # 2) generate quadratic and interaction features
        extra_features = []
        if self.generate_quadratic:
            extra_features.append(X_base**2)

        if self.generate_interactions:
            extra_features.append(self._compute_interactions(X_base))

        if extra_features:
            X_out = np.concatenate([X_base] + extra_features, axis=1)
        else:
            X_out = X_base

        if isinstance(X, pd.DataFrame):
            return pd.DataFrame(
                X_out, index=X.index, columns=self.all_output_feature_names
            )
        return X_out

    def fit_transform(self, X: ArrayLike, y: ArrayLike) -> ArrayLike:
        """
        Fit the transformer and return the transformed data.

        This is equivalent to calling :meth:`fit` followed by
        :meth:`transform`.

        :param X: Input feature matrix.
        :type X: ArrayLike
        :param y: Target values.
        :type y: ArrayLike
        :returns: Transformed feature matrix.
        :rtype: ArrayLike
        """
        return self.fit(X, y).transform(X)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _make_estimator(self) -> BaseEstimator:
        """
        Create a fresh clone of the estimator for a single CV fold.

        :returns: Cloned estimator.
        :rtype: BaseEstimator
        """
        if self.estimator is not None:
            return clone(self.estimator)

        # Default: RandomForestRegressor baseline
        base = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            n_jobs=self.n_jobs,
            random_state=self.random_state,
        )
        return clone(base)

    def _get_scorer(self):
        """
        Return a callable scorer(y_true, y_pred) based on self.scoring.

        :returns: Scoring function.
        :rtype: callable
        :raises ValueError: If an unsupported scoring name is given.
        """
        if self.scoring == "r2":
            return r2_score
        if self.scoring == "neg_mean_squared_error":
            return lambda yt, yp: -mean_squared_error(yt, yp)
        if self.scoring == "neg_mean_absolute_error":
            return lambda yt, yp: -mean_absolute_error(yt, yp)

        raise ValueError(
            f"Unsupported scoring='{self.scoring}'. "
            "Supported: 'r2', 'neg_mean_squared_error', 'neg_mean_absolute_error'."
        )

    def _to_array_and_names(
        self,
        X: ArrayLike,
        expect_names: Optional[Sequence[str]] = None,
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Convert input to NumPy array and extract feature names.

        :param X: Input data (DataFrame or ndarray).
        :type X: ArrayLike
        :param expect_names: Optional expected feature names. If given
            and ``X`` is a DataFrame, a consistency check is performed.
        :type expect_names: Sequence[str] or None
        :returns: Tuple of (array representation, feature names).
        :rtype: tuple[np.ndarray, list[str]]
        :raises ValueError: If feature names are incompatible.
        """
        if isinstance(X, pd.DataFrame):
            names = list(X.columns)
            if expect_names is not None and list(expect_names) != names:
                raise ValueError(
                    "Input DataFrame columns differ from those seen during fit.\n"
                    f"Expected: {list(expect_names)}\nGot: {names}"
                )
            return X.to_numpy(dtype=float), names

        X_arr = np.asarray(X, dtype=float)
        if X_arr.ndim != 2:
            raise ValueError("Input array must be 2D.")
        n_features = X_arr.shape[1]

        if expect_names is not None:
            if len(expect_names) != n_features:
                raise ValueError(
                    "Number of features in input does not match the "
                    "fitted feature dimension."
                )
            return X_arr, list(expect_names)

        names = [f"f{i}" for i in range(n_features)]
        return X_arr, names

    def _select_features(self) -> None:
        """
        Select features based on averaged importances.

        Populates :pyattr:`selected_indices_` and
        :pyattr:`selected_feature_names_`.
        """
        assert self.feature_importances_ is not None

        importances = self.feature_importances_
        n_features = importances.shape[0]

        if self.top_k is not None:
            k = min(self.top_k, n_features)
            indices = np.argsort(importances)[::-1][:k]
        else:
            if self.importance_threshold <= 0.0:
                indices = np.arange(n_features)
            else:
                max_imp = float(importances.max())
                if max_imp <= 0.0:
                    indices = np.arange(n_features)
                else:
                    thresh = self.importance_threshold * max_imp
                    indices = np.where(importances >= thresh)[0]
                    if indices.size == 0:
                        indices = np.array([int(np.argmax(importances))])

        indices = np.sort(indices)
        self.selected_indices_ = indices
        self.selected_feature_names_ = [self.input_feature_names_[i] for i in indices]

    def _prepare_generated_feature_names(self) -> None:
        """
        Pre-compute names for generated features
        (quadratic + interactions).
        """
        self.generated_feature_names_ = []

        base_names = self.selected_feature_names_
        if self.generate_quadratic:
            self.generated_feature_names_.extend([f"{name}^2" for name in base_names])

        if self.generate_interactions:
            selected_importances = self.feature_importances_[self.selected_indices_]
            order = np.argsort(selected_importances)[::-1]

            max_bases = min(
                self.max_interaction_features,
                len(self.selected_indices_),
            )
            top_indices = order[:max_bases]
            top_names = [base_names[i] for i in top_indices]

            for i in range(len(top_names)):
                for j in range(i + 1, len(top_names)):
                    n1 = top_names[i]
                    n2 = top_names[j]
                    self.generated_feature_names_.append(f"{n1}*{n2}")

    def _compute_interactions(self, X_base: np.ndarray) -> np.ndarray:
        """
        Compute pairwise interaction terms for the most important
        selected features.

        :param X_base: Base selected feature matrix of shape
            ``(n_samples, n_selected_features)``.
        :type X_base: np.ndarray
        :returns: Interaction feature matrix of shape
            ``(n_samples, n_interactions)``.
        :rtype: np.ndarray
        """
        if X_base.shape[1] == 0:
            return np.zeros((X_base.shape[0], 0), dtype=float)

        selected_importances = self.feature_importances_[self.selected_indices_]
        order = np.argsort(selected_importances)[::-1]
        max_bases = min(self.max_interaction_features, X_base.shape[1])
        top_indices = order[:max_bases]

        interactions = []
        for idx_i in range(len(top_indices)):
            i = top_indices[idx_i]
            for idx_j in range(idx_i + 1, len(top_indices)):
                j = top_indices[idx_j]
                interactions.append(X_base[:, i] * X_base[:, j])

        if not interactions:
            return np.zeros((X_base.shape[0], 0), dtype=float)

        return np.column_stack(interactions)
