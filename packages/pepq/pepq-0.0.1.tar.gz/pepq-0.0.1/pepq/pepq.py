"""
pepq.py — Unified PepQ training + calibration + tradeoff selection
===============================================================

This module provides a single high-level class (:class:`PepQ`) that wraps:

- feature selection from a DataFrame
- preprocessing (variance filter + scaler)
- DockQ regression model training
- AD-conformal calibration
- width-threshold tradeoff scanning and operating-point selection

Key update for model size
-------------------------
Instead of caching full calibration arrays (X_cal, y_cal, X_cal_proc),
you can now store only a selected default width-threshold (float) and
(optionally) a small tradeoff DataFrame. This makes serialization small.

.. note::
   Methods that mutate internal state return ``self``. Values are retrieved via
   properties (e.g. :pyattr:`tradeoff_df`, :pyattr:`default_threshold`) or via
   methods that naturally return data (e.g. :meth:`pick_operating_point`).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import numpy as np
import pandas as pd

from pepq.data import (
    DataPreprocessor,
    PreprocessorConfig,
    ScalerConfig,
    VarianceConfig,
    build_data,
)
from pepq.calibration.ad_conformal import ADConformal

HERE = Path(__file__).resolve().parent

ArrayLikeDF = Union[pd.DataFrame, Iterable[Mapping[str, Any]]]
TradeoffAdapter = Callable[[Any], Optional[pd.DataFrame]]
CompressArg = Union[int, Tuple[str, int]]  # e.g. 9 or ("xz", 9)


# ---------------------------- selection utils ----------------------------


def _knee_point(df: pd.DataFrame, x_col: str, y_col: str) -> int:
    """Internal: knee index by max distance to chord in normalized space."""
    x = pd.to_numeric(df[x_col], errors="coerce").to_numpy(dtype=float)
    y = pd.to_numeric(df[y_col], errors="coerce").to_numpy(dtype=float)

    x = np.where(np.isfinite(x), x, np.nan)
    y = np.where(np.isfinite(y), y, np.nan)

    if np.all(np.isnan(x)) or np.all(np.isnan(y)):
        return 0

    # fill nan with column medians for stability
    x_med = float(np.nanmedian(x))
    y_med = float(np.nanmedian(y))
    x = np.where(np.isnan(x), x_med, x)
    y = np.where(np.isnan(y), y_med, y)

    x = (x - x.min()) / (x.max() - x.min() + 1e-12)
    y = (y - y.min()) / (y.max() - y.min() + 1e-12)

    p1 = np.array([x[0], y[0]])
    p2 = np.array([x[-1], y[-1]])
    denom = float(np.linalg.norm(p2 - p1) + 1e-12)

    d: list[float] = []
    for xi, yi in zip(x, y):
        p = np.array([xi, yi])
        dist = float(np.linalg.norm(np.cross(p2 - p1, p1 - p)) / denom)
        d.append(dist)

    return int(np.argmax(d))


def pick_threshold(
    df: pd.DataFrame,
    metric_col: str,
    mode: str = "elbow",
    target_coverage: float = 0.80,
    min_coverage: Optional[float] = None,
    lambda_penalty: float = 0.2,
) -> pd.Series:
    """
    Pick a width-threshold operating point from a normalized tradeoff table.

    :param df:
        Tradeoff DataFrame normalized so ``coverage`` is empirical coverage.
    :param metric_col:
        Column to optimize (e.g. ``pearson_r_in_domain``).
    :param mode:
        - ``"elbow"``: knee on (coverage, metric)
        - ``"max"``: argmax(metric)
        - ``"target"``: nearest coverage to ``target_coverage``
        - ``"mincov_max"``: max metric among rows with coverage >= min_coverage
        - ``"utility"``: maximize metric - lambda*(1-coverage)
    :param target_coverage:
        Target empirical coverage for ``mode="target"``.
    :param min_coverage:
        Minimum empirical coverage for ``mode="mincov_max"``.
    :param lambda_penalty:
        Penalty weight for ``mode="utility"``.
    :returns:
        Selected row.

    .. code-block:: python

        row = pick_threshold(tradeoff_df, "pearson_r_in_domain",
                             mode="target", target_coverage=0.70)
        thr = float(row["threshold"])
    """
    required = {"coverage", "threshold", metric_col}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)} | available={list(df.columns)}"
        )

    d = df.sort_values("coverage", ascending=True).reset_index(drop=True)

    if mode == "max":
        idx = int(d[metric_col].idxmax())
        return d.loc[idx]

    if mode == "elbow":
        idx = _knee_point(d, "coverage", metric_col)
        return d.iloc[idx]

    if mode == "target":
        idx = int((d["coverage"] - float(target_coverage)).abs().idxmin())
        return d.loc[idx]

    if mode == "mincov_max":
        mc = float(target_coverage if min_coverage is None else min_coverage)
        sub = d[d["coverage"] >= mc]
        if len(sub) == 0:
            return pick_threshold(d, metric_col, mode="target", target_coverage=mc)
        idx = int(sub[metric_col].idxmax())
        return d.loc[idx]

    if mode == "utility":
        util = d[metric_col] - float(lambda_penalty) * (1.0 - d["coverage"])
        idx = int(util.idxmax())
        return d.loc[idx]

    raise ValueError(f"Unknown mode='{mode}'")


# ---------------------------- artifacts ----------------------------


@dataclass
class PepQArtifacts:
    """Holds fitted components and small optional cached artifacts."""

    preprocessor: Optional[DataPreprocessor] = None
    model: Any = None
    ad_conf: Optional[ADConformal] = None

    # optional caches (can be stripped before save)
    X_cal: Optional[pd.DataFrame] = None
    y_cal: Optional[pd.Series] = None
    X_cal_proc: Optional[pd.DataFrame] = None

    tradeoff_df: Optional[pd.DataFrame] = None
    tradeoff_raw: Any = None

    # NEW: store only default threshold / operating point for lightweight deployment
    default_threshold: Optional[float] = None
    default_op: Optional[Dict[str, Any]] = None


# ---------------------------- tradeoff helpers ----------------------------


class TradeoffCoercer:
    """
    Small helper to convert arbitrary "tradeoff results" into a DataFrame.

    The logic is intentionally split into small methods to keep cyclomatic
    complexity low.
    """

    _ATTR_CANDIDATES: Tuple[str, ...] = (
        "tradeoff_table",
        "tradeoff_df",
        "df",
        "table",
        "results",
        "scan_table",
        "scan_df",
        "results_df",
    )

    @staticmethod
    def _try_df(obj: Any) -> Optional[pd.DataFrame]:
        if obj is None:
            return None
        if isinstance(obj, pd.DataFrame):
            return obj.copy()
        try:
            return pd.DataFrame(obj)
        except Exception:
            return None

    def from_attr(self, raw: Any) -> Optional[pd.DataFrame]:
        for attr in self._ATTR_CANDIDATES:
            if hasattr(raw, attr):
                df = self._try_df(getattr(raw, attr))
                if df is not None:
                    return df
        return None

    def from_mapping(self, raw: Any) -> Optional[pd.DataFrame]:
        if isinstance(raw, Mapping):
            return self._try_df(raw)
        return None

    def from_numpy(self, raw: Any) -> Optional[pd.DataFrame]:
        if isinstance(raw, np.ndarray):
            return self._try_df(raw)
        return None

    def from_sequence(self, raw: Any) -> Optional[pd.DataFrame]:
        if not isinstance(raw, (list, tuple)):
            return None

        # If it's a list of candidates, try each element first.
        for item in raw:
            df = self.coerce(item)
            if df is not None:
                return df

        # Otherwise try direct DataFrame construction.
        return self._try_df(raw)

    def coerce(self, raw: Any) -> Optional[pd.DataFrame]:
        """
        Attempt to coerce a raw object to a DataFrame.

        :param raw: Any scan output / results object.
        :returns: DataFrame or None.
        """
        df = self._try_df(raw)
        if df is not None:
            return df

        df = self.from_attr(raw)
        if df is not None:
            return df

        df = self.from_mapping(raw)
        if df is not None:
            return df

        df = self.from_numpy(raw)
        if df is not None:
            return df

        df = self.from_sequence(raw)
        if df is not None:
            return df

        return None


class TradeoffNormalizer:
    """
    Normalize tradeoff tables to a single convention.

    Output columns (as available):
    - threshold (float)
    - coverage_quantile (0..1 scan quantile)
    - coverage (empirical coverage)
    - pearson_r_in_domain, spearman_rho_in_domain, n_in_domain
    """

    @staticmethod
    def _lower_map(cols: Sequence[Any]) -> Dict[str, Any]:
        return {str(c).lower(): c for c in cols}

    @staticmethod
    def _first(cols_map: Dict[str, Any], candidates: Sequence[str]) -> Optional[Any]:
        for c in candidates:
            key = str(c).lower()
            if key in cols_map:
                return cols_map[key]
        return None

    @staticmethod
    def _numstats(x: pd.Series) -> Dict[str, float]:
        v = pd.to_numeric(x, errors="coerce").to_numpy(dtype=float)
        v = v[np.isfinite(v)]
        if v.size == 0:
            return {"min": np.nan, "max": np.nan, "mean": np.nan}
        return {"min": float(v.min()), "max": float(v.max()), "mean": float(v.mean())}

    @classmethod
    def _rename_known(cls, d: pd.DataFrame) -> pd.DataFrame:
        cols = cls._lower_map(list(d.columns))
        rename: Dict[Any, str] = {}

        def add(cands: Sequence[str], target: str) -> None:
            src = cls._first(cols, cands)
            if src is not None and src != target and target not in d.columns:
                rename[src] = target

        add(
            ["threshold", "thr", "width_threshold", "width_thr", "w_threshold"],
            "threshold",
        )
        add(
            ["pearson_r_in_domain", "pearson_r", "pearson", "pearsonr"],
            "pearson_r_in_domain",
        )
        add(
            ["spearman_rho_in_domain", "spearman_rho", "spearman"],
            "spearman_rho_in_domain",
        )
        add(["n_in_domain", "n_domain", "n_eval", "n_points", "n"], "n_in_domain")
        add(
            ["coverage_interval", "interval_coverage", "coverage_ci"],
            "coverage_interval",
        )
        add(["coverage_quantile", "quantile", "q"], "coverage_quantile")
        add(["coverage", "cov", "coverage_in_domain", "in_domain_coverage"], "coverage")

        if rename:
            d = d.rename(columns=rename)
        return d

    @classmethod
    def _resolve_coverage_ambiguity(cls, d: pd.DataFrame) -> pd.DataFrame:
        if "coverage" not in d.columns or "coverage_interval" not in d.columns:
            return d

        s_cov = cls._numstats(d["coverage"])
        s_covi = cls._numstats(d["coverage_interval"])

        cov_scanlike = (
            np.isfinite(s_cov["min"])
            and np.isfinite(s_cov["max"])
            and abs(s_cov["min"] - 0.0) < 0.05
            and abs(s_cov["max"] - 1.0) < 0.05
            and 0.35 <= s_cov["mean"] <= 0.65
        )
        covi_coveragelike = (
            np.isfinite(s_covi["min"])
            and np.isfinite(s_covi["max"])
            and 0.50 <= s_covi["mean"] <= 1.00
        )

        if cov_scanlike and covi_coveragelike:
            # treat "coverage" as scan quantile, "coverage_interval" as empirical
            d = d.rename(columns={"coverage": "coverage"})
            d = d.rename(columns={"coverage_interval": "coverage_interval"})
        return d

    @classmethod
    def _ensure_quantile_alias(cls, d: pd.DataFrame) -> pd.DataFrame:
        if "coverage" not in d.columns or "coverage_quantile" in d.columns:
            return d

        s_cov = cls._numstats(d["coverage"])
        looks_scanlike = (
            np.isfinite(s_cov["min"])
            and np.isfinite(s_cov["max"])
            and abs(s_cov["min"] - 0.0) < 0.05
            and abs(s_cov["max"] - 1.0) < 0.05
            and 0.35 <= s_cov["mean"] <= 0.65
        )
        if looks_scanlike:
            d = d.rename(columns={"coverage": "coverage_quantile"})
        return d

    @staticmethod
    def _coerce_numeric(d: pd.DataFrame) -> pd.DataFrame:
        if "threshold" in d.columns:
            d["threshold"] = pd.to_numeric(d["threshold"], errors="coerce")
        return d

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize a tradeoff DataFrame.

        :param df: Raw tradeoff table.
        :returns: Normalized copy.
        """
        d = df.copy()
        d = self._rename_known(d)
        d = self._resolve_coverage_ambiguity(d)
        d = self._ensure_quantile_alias(d)
        d = self._coerce_numeric(d)
        return d


# ---------------------------- main class ----------------------------


class PepQ:
    """
    End-to-end PepQ trainer + AD-conformal calibrator + width-threshold selector.

    :param feature_keys:
        Feature columns to use. The input DataFrame can contain more columns,
        but only these are passed to preprocessing/model.
    :param target_key:
        Target column name when using the "data includes y" API.
    :param preprocessor_cfg:
        Preprocessor configuration.
    :param model_cls:
        Regression model class. Defaults to ``DockQRegressor``.
    :param model_kwargs:
        kwargs passed to the model constructor.
    :param adconf_kwargs:
        kwargs passed to :class:`pepq.calibration.ad_conformal.ADConformal`.
    :param ensure_return_dataframe:
        If True, forces the preprocessor to return DataFrames where supported.
    :param cache_calibration:
        If True, stores calibration X/y (and processed X) for later scanning.
        If False, you can still scan by passing ``X_eval/y_eval`` to
        :meth:`scan_width_tradeoff` or :meth:`calibrate_threshold`.
    :param tradeoff_adapter:
        Optional hook to convert custom scan results into a DataFrame.

    .. code-block:: python

        cfg = PepQ.make_default_preprocessor_cfg(
            variance_threshold=0.0,
            scaler="minmax",
            return_dataframe=True,
        )

        pepq = PepQ(preprocessor_cfg=cfg, target_key="dockq",
                    cache_calibration=False)

        pepq.fit((X_train, y_train), (X_val, y_val))

        # Compute & store ONLY a default threshold (no X_cal cached)
        pepq.calibrate_threshold(
            X_eval=X_val,
            y_eval=y_val,
            scan_kwargs={"score_type": "fbeta", "beta": 4},
            pick_kwargs={"metric_col": "pearson_r_in_domain",
                        "mode": "target", "target_coverage": 0.70},
            store_tradeoff_df=True,
        )

        pepq.save("pepq_small.joblib", compress=("xz", 9), compact=True)
    """

    def __init__(
        self,
        *,
        feature_keys: Sequence[str] = (
            "prot_plddt",
            "pep_plddt",
            "PTM",
            "PAE",
            "iptm",
            "composite_ptm",
            "actifptm",
        ),
        target_key: Optional[str] = None,
        preprocessor_cfg: Optional[PreprocessorConfig] = None,
        model_cls: Optional[type] = None,
        model_kwargs: Optional[Mapping[str, Any]] = None,
        adconf_kwargs: Optional[Mapping[str, Any]] = None,
        ensure_return_dataframe: bool = True,
        cache_calibration: bool = False,
        tradeoff_adapter: Optional[TradeoffAdapter] = None,
    ) -> None:
        self._feature_keys: Tuple[str, ...] = tuple(feature_keys)
        self._target_key = target_key
        self._preprocessor_cfg = preprocessor_cfg
        self._ensure_return_dataframe = bool(ensure_return_dataframe)

        self._model_cls = model_cls
        self._model_kwargs: Dict[str, Any] = dict(model_kwargs or {})
        self._adconf_kwargs: Dict[str, Any] = dict(adconf_kwargs or {})

        self._cache_calibration = bool(cache_calibration)
        self._tradeoff_adapter = tradeoff_adapter

        self._coercer = TradeoffCoercer()
        self._normalizer = TradeoffNormalizer()

        self._art = PepQArtifacts()
        self._fitted = False

    # -------------------- basic helpers / properties --------------------

    def __repr__(self) -> str:
        has_cal = self._art.X_cal is not None and self._art.y_cal is not None
        has_tbl = self._art.tradeoff_df is not None
        has_thr = self._art.default_threshold is not None
        return (
            f"{self.__class__.__name__}("
            f"fitted={self._fitted}, "
            f"n_features={len(self._feature_keys)}, "
            f"has_cal={has_cal}, "
            f"has_tradeoff_df={has_tbl}, "
            f"has_default_thr={has_thr}"
            f")"
        )

    def help(self) -> str:
        """
        Human-readable overview of current state.

        :returns: Multi-line string.
        """
        return (
            f"{repr(self)}\n"
            f"feature_keys={self._feature_keys}\n"
            f"preprocessor={'yes' if self._art.preprocessor is not None else 'no'}\n"
            f"model={'yes' if self._art.model is not None else 'no'}\n"
            f"ad_conf={'yes' if self._art.ad_conf is not None else 'no'}\n"
            f"default_threshold={self._art.default_threshold}\n"
        )

    @property
    def fitted(self) -> bool:
        """:returns: True if fit has been called successfully."""
        return bool(self._fitted)

    @property
    def feature_keys(self) -> Tuple[str, ...]:
        """:returns: Feature keys used by this PepQ instance."""
        return self._feature_keys

    @property
    def preprocessor(self) -> Optional[DataPreprocessor]:
        """:returns: Fitted preprocessor (or None)."""
        return self._art.preprocessor

    @property
    def model(self) -> Any:
        """:returns: Fitted model (or None)."""
        return self._art.model

    @property
    def ad_conformal(self) -> Optional[ADConformal]:
        """:returns: Fitted ADConformal object (or None)."""
        return self._art.ad_conf

    @property
    def tradeoff_df(self) -> Optional[pd.DataFrame]:
        """
        :returns:
            Normalized tradeoff DataFrame (or None). Normalization guarantees:
            - ``coverage_quantile`` is scan quantile (0..1)
            - ``coverage`` is empirical coverage
        """
        return self._art.tradeoff_df

    @property
    def default_threshold(self) -> Optional[float]:
        """
        :returns:
            Stored default width-threshold (float) used by :meth:`predict_confident`
            when ``threshold=None``.
        """
        return self._art.default_threshold

    @staticmethod
    def _require(cond: bool, msg: str) -> None:
        if not cond:
            raise RuntimeError(msg)

    @staticmethod
    def _as_series(y: Union[pd.Series, Sequence[Any]]) -> pd.Series:
        return y if isinstance(y, pd.Series) else pd.Series(y)

    @staticmethod
    def _is_xy_pair(obj: Any) -> bool:
        return (
            isinstance(obj, (tuple, list))
            and len(obj) == 2
            and isinstance(obj[0], pd.DataFrame)
        )

    # -------------------- factory --------------------

    @staticmethod
    def make_default_preprocessor_cfg(
        *,
        variance_threshold: float = 0.00,
        scaler: str = "minmax",
        return_dataframe: bool = True,
    ) -> PreprocessorConfig:
        """
        Convenience factory for a standard preprocessor config.

        :param variance_threshold: Variance filter threshold.
        :param scaler: Scaler name (e.g., ``"minmax"``, ``"standard"``).
        :param return_dataframe: If supported, force DataFrame outputs.
        :returns: :class:`pepq.data.PreprocessorConfig`
        """
        cfg = PreprocessorConfig(
            variance=VarianceConfig(threshold=float(variance_threshold)),
            scaler=ScalerConfig(scaler=str(scaler)),
        )
        if hasattr(cfg, "set_return_dataframe"):
            cfg = cfg.set_return_dataframe(bool(return_dataframe))
        return cfg

    # -------------------- data helpers --------------------

    def build_dataframe(self, data: Any, dockq: pd.DataFrame) -> pd.DataFrame:
        """
        Build a merged feature table from raw inputs and DockQ table.

        :param data: Raw object consumed by :func:`pepq.data.build_data`.
        :param dockq: DockQ results table.
        :returns: Merged DataFrame.
        """
        return build_data(data=data, dockq=dockq)

    def get_X(self, data: ArrayLikeDF) -> pd.DataFrame:
        """
        Extract the feature matrix (X) with strict column checking.

        :param data: DataFrame or iterable of dict-like rows.
        :returns: DataFrame with columns == ``feature_keys`` (copy).
        :raises KeyError: If required columns are missing.
        """
        df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
        missing = [k for k in self._feature_keys if k not in df.columns]
        if missing:
            raise KeyError(f"Missing required feature columns: {missing}")
        return df.loc[:, list(self._feature_keys)].copy()

    def get_xy(
        self,
        data: ArrayLikeDF,
        *,
        target_key: Optional[str] = None,
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Extract (X, y) from a DataFrame-like.

        :param data: DataFrame-like that includes the target column.
        :param target_key: Overrides instance ``target_key`` if provided.
        :returns: (X, y)
        :raises RuntimeError: If no target_key is available.
        :raises KeyError: If target column not found in data.
        """
        df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
        X = self.get_X(df)
        tkey = self._target_key if target_key is None else target_key
        self._require(tkey is not None, "target_key is None; cannot extract y.")
        if tkey not in df.columns:
            raise KeyError(f"Target column '{tkey}' not found in data")
        return X, df[tkey].copy()

    def _extract_pair_or_df(
        self,
        obj: Union[ArrayLikeDF, Tuple[pd.DataFrame, Union[pd.Series, Sequence[Any]]]],
        *,
        target_key: Optional[str],
    ) -> Tuple[pd.DataFrame, pd.Series]:
        if self._is_xy_pair(obj):
            X, y = obj  # type: ignore[misc]
            return self.get_X(X), self._as_series(y)  # type: ignore[arg-type]
        return self.get_xy(obj, target_key=target_key)  # type: ignore[arg-type]

    # -------------------- builders (return self) --------------------

    def build_preprocessor(self) -> "PepQ":
        """
        Instantiate the preprocessor from ``preprocessor_cfg``.

        :returns: self
        :raises RuntimeError: If preprocessor_cfg is None.
        """
        self._require(self._preprocessor_cfg is not None, "preprocessor_cfg is None.")
        cfg = self._preprocessor_cfg
        if self._ensure_return_dataframe and hasattr(cfg, "set_return_dataframe"):
            cfg = cfg.set_return_dataframe(True)
        self._art.preprocessor = DataPreprocessor.from_config(cfg)
        return self

    def build_model(self) -> "PepQ":
        """
        Instantiate the regression model.

        :returns: self
        """
        if self._model_cls is None:
            from pepq.model.regression import DockQRegressor  # default backend

            self._model_cls = DockQRegressor
        self._art.model = self._model_cls(**self._model_kwargs)
        return self

    def build_adconformal(self) -> "PepQ":
        """
        Instantiate the ADConformal calibrator.

        :returns: self
        """
        self._art.ad_conf = ADConformal(**self._adconf_kwargs)
        return self

    # -------------------- fit / transform --------------------

    def fit(
        self,
        train: Optional[
            Union[ArrayLikeDF, Tuple[pd.DataFrame, Union[pd.Series, Sequence[Any]]]]
        ] = None,
        cal: Optional[
            Union[ArrayLikeDF, Tuple[pd.DataFrame, Union[pd.Series, Sequence[Any]]]]
        ] = None,
        *,
        X_train: Optional[pd.DataFrame] = None,
        y_train: Optional[Union[pd.Series, Sequence[Any]]] = None,
        X_cal: Optional[pd.DataFrame] = None,
        y_cal: Optional[Union[pd.Series, Sequence[Any]]] = None,
        target_key: Optional[str] = None,
    ) -> "PepQ":
        """
        Fit preprocessor + model + ADConformal calibration.

        You can provide either:
        - ``fit((X_train, y_train), (X_cal, y_cal))``, or
        - ``fit(X_train=..., y_train=..., X_cal=..., y_cal=...)``, or
        - ``fit(train_df_with_target, cal_df_with_target, target_key="dockq")``

        :param train: Training data or (X, y) pair.
        :param cal: Calibration data or (X, y) pair.
        :param X_train: Training X.
        :param y_train: Training y.
        :param X_cal: Calibration X.
        :param y_cal: Calibration y.
        :param target_key: Target column name if passing full DataFrames.
        :returns: self
        """
        if self._art.preprocessor is None:
            self.build_preprocessor()
        if self._art.model is None:
            self.build_model()
        if self._art.ad_conf is None:
            self.build_adconformal()

        explicit = any(v is not None for v in (X_train, y_train, X_cal, y_cal))
        if explicit:
            self._require(
                X_train is not None and y_train is not None,
                "Provide X_train and y_train.",
            )
            self._require(
                X_cal is not None and y_cal is not None,
                "Provide X_cal and y_cal.",
            )
            Xtr = self.get_X(X_train)
            ytr = self._as_series(y_train)
            Xca = self.get_X(X_cal)
            yca = self._as_series(y_cal)
        else:
            self._require(
                train is not None and cal is not None,
                "Provide both train and cal.",
            )
            Xtr, ytr = self._extract_pair_or_df(train, target_key=target_key)
            Xca, yca = self._extract_pair_or_df(cal, target_key=target_key)

        self._art.preprocessor.fit(Xtr)
        Xtr_p = self._art.preprocessor.transform(Xtr)
        Xca_p = self._art.preprocessor.transform(Xca)

        self._art.model.fit(Xtr_p, ytr)
        self._art.ad_conf.fit(self._art.model, Xca_p, yca)

        if self._cache_calibration:
            self._art.X_cal = Xca.copy()
            self._art.y_cal = yca.copy()
            self._art.X_cal_proc = (
                Xca_p.copy() if isinstance(Xca_p, pd.DataFrame) else None
            )

        self._fitted = True
        return self

    def transform(self, X: pd.DataFrame) -> Any:
        """
        Transform features through the fitted preprocessor.

        :param X: Raw feature DataFrame (must include feature_keys).
        :returns: Processed feature matrix (DataFrame/ndarray depending on config).
        """
        self._require(self._art.preprocessor is not None, "Preprocessor is not fitted.")
        return self._art.preprocessor.transform(self.get_X(X))

    # -------------------- tradeoff: scan + normalize --------------------

    def normalize_tradeoff_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize/standardize tradeoff tables to the PepQ convention.

        :param df: Raw tradeoff table.
        :returns: Normalized copy.
        """
        return self._normalizer.normalize(df)

    def _get_tradeoff_from_adconf(self) -> Optional[pd.DataFrame]:
        ad = self._art.ad_conf
        if ad is None:
            return None
        for attr in (
            "tradeoff_table",
            "tradeoff_df",
            "scan_table",
            "scan_df",
            "results_df",
        ):
            if hasattr(ad, attr):
                df = self._coercer._try_df(getattr(ad, attr))
                if df is not None:
                    return df
        return None

    def scan_width_tradeoff(
        self,
        *,
        X_eval: Optional[pd.DataFrame] = None,
        y_eval: Optional[Union[pd.Series, Sequence[Any]]] = None,
        require_dataframe: bool = True,
        store_raw: bool = False,
        store_df: bool = True,
        **kwargs: Any,
    ) -> "PepQ":
        """
        Scan width thresholds and store normalized results.

        You have two modes:

        1) Cached mode (legacy): if you fitted with ``cache_calibration=True``,
           omit ``X_eval/y_eval`` and it will use cached calibration.
        2) Stateless mode (recommended for small serialization):
           pass ``X_eval`` and ``y_eval`` explicitly; nothing large is stored.

        :param X_eval: Evaluation features for scanning (recommended).
        :param y_eval: Evaluation target for scanning.
        :param require_dataframe: If True, raises if a DataFrame cannot be obtained.
        :param store_raw: If True, store raw scan output (can be large).
        :param store_df: If True, store normalized tradeoff_df (usually small).
        :param kwargs: Passed to ``ADConformal.scan_width_tradeoff``.
        :returns: self
        """
        self._require(self._art.ad_conf is not None, "ADConformal is not fitted.")

        if X_eval is None or y_eval is None:
            # fallback to cached calibration
            self._require(
                self._art.y_cal is not None,
                "No cached calibration. Either fit with cache_calibration=True "
                "or pass X_eval/y_eval to scan_width_tradeoff.",
            )
            Xp = self._art.X_cal_proc
            if Xp is None:
                self._require(
                    self._art.X_cal is not None,
                    "No cached X_cal. Fit with cache_calibration=True or pass X_eval.",
                )
                Xp = self.transform(self._art.X_cal)
            ye = self._art.y_cal
        else:
            X = self.get_X(X_eval)
            Xp = self._art.preprocessor.transform(X)  # type: ignore[union-attr]
            ye = self._as_series(y_eval)

        raw = self._art.ad_conf.scan_width_tradeoff(X_eval=Xp, y_eval=ye, **kwargs)
        if store_raw:
            self._art.tradeoff_raw = raw

        df = self._get_tradeoff_from_adconf()
        if df is None:
            df = self._coercer.coerce(raw)

        if df is not None:
            df = self.normalize_tradeoff_df(df)

        if store_df:
            self._art.tradeoff_df = df

        if df is None and require_dataframe:
            raw_repr = repr(raw)
            if len(raw_repr) > 300:
                raw_repr = raw_repr[:300] + "..."
            raise TypeError(
                "scan_width_tradeoff: could not produce DataFrame. "
                f"type(raw)={type(raw)} | raw_repr={raw_repr}"
            )
        return self

    def ensure_tradeoff(
        self,
        *,
        scan_kwargs: Optional[Dict[str, Any]] = None,
        require_dataframe: bool = True,
    ) -> "PepQ":
        """
        Ensure a normalized tradeoff table exists.

        :param scan_kwargs: kwargs passed to :meth:`scan_width_tradeoff` if needed.
        :param require_dataframe: If True, scanning must yield a DataFrame.
        :returns: self
        """
        if self._art.tradeoff_df is not None:
            return self
        scan_kwargs = {} if scan_kwargs is None else dict(scan_kwargs)
        return self.scan_width_tradeoff(
            require_dataframe=require_dataframe, **scan_kwargs
        )

    def pick_operating_point(
        self,
        *,
        metric_col: str,
        mode: str = "elbow",
        target_coverage: float = 0.70,
        min_coverage: Optional[float] = None,
        lambda_penalty: float = 0.2,
        tradeoff_df: Optional[pd.DataFrame] = None,
        auto_scan: bool = True,
        scan_kwargs: Optional[Dict[str, Any]] = None,
        require_dataframe: bool = True,
    ) -> pd.Series:
        """
        Pick an operating point (row) from the tradeoff table.

        :param metric_col: Metric column to optimize.
        :param mode: Selection mode (see :func:`pick_threshold`).
        :param target_coverage: Target empirical coverage for ``mode="target"``.
        :param min_coverage: Minimum empirical coverage for ``mode="mincov_max"``.
        :param lambda_penalty: Coverage penalty for ``mode="utility"``.
        :param tradeoff_df: If provided, use this table instead of cached one.
        :param auto_scan: If True and no cached table exists, scan first.
        :param scan_kwargs: kwargs used if auto_scan triggers scanning.
        :param require_dataframe: If True, scanning must yield a DataFrame.
        :returns: Operating point as a row Series.
        """
        d = tradeoff_df if tradeoff_df is not None else self._art.tradeoff_df
        if d is None and auto_scan:
            self.ensure_tradeoff(
                scan_kwargs=scan_kwargs, require_dataframe=require_dataframe
            )
            d = self._art.tradeoff_df

        self._require(d is not None, "No tradeoff_df available.")
        d = self.normalize_tradeoff_df(d)

        if metric_col not in d.columns:
            metric_col = self._resolve_metric_alias(metric_col, d.columns)

        return pick_threshold(
            d,
            metric_col=metric_col,
            mode=mode,
            target_coverage=target_coverage,
            min_coverage=min_coverage,
            lambda_penalty=lambda_penalty,
        )

    @staticmethod
    def _resolve_metric_alias(metric_col: str, columns: Sequence[str]) -> str:
        aliases: Dict[str, Sequence[str]] = {
            "pearson_r_in_domain": ("pearson_r", "pearson", "pearsonr"),
            "spearman_rho_in_domain": ("spearman_rho", "spearman"),
        }
        for alt in aliases.get(metric_col, ()):
            if alt in columns:
                return alt
        return metric_col

    # -------------------- default threshold utilities --------------------

    def set_default_threshold(
        self,
        threshold: float,
        *,
        operating_point: Optional[Mapping[str, Any]] = None,
    ) -> "PepQ":
        """
        Store a default width threshold for later inference.

        :param threshold: Width threshold (float).
        :param operating_point: Optional metadata dict (picked row, params, etc.).
        :returns: self
        """
        thr = float(threshold)
        if not np.isfinite(thr):
            raise ValueError(f"default threshold is not finite: {threshold!r}")
        self._art.default_threshold = thr
        self._art.default_op = (
            None if operating_point is None else dict(operating_point)
        )
        return self

    def calibrate_threshold(
        self,
        *,
        X_eval: pd.DataFrame,
        y_eval: Union[pd.Series, Sequence[Any]],
        scan_kwargs: Optional[Dict[str, Any]] = None,
        pick_kwargs: Optional[Dict[str, Any]] = None,
        store_tradeoff_df: bool = True,
        store_operating_point: bool = True,
    ) -> "PepQ":
        """
        One-shot helper: scan -> pick operating point -> store ONLY threshold.

        :param X_eval: Evaluation feature table for scanning.
        :param y_eval: Evaluation target for scanning.
        :param scan_kwargs: Passed to :meth:`scan_width_tradeoff`.
        :param pick_kwargs: Passed to :meth:`pick_operating_point`.
        :param store_tradeoff_df: If False, the tradeoff_df is dropped after threshold is picked.
        :param store_operating_point: If False, do not store the picked row metadata.
        :returns: self
        """
        scan_kwargs = {} if scan_kwargs is None else dict(scan_kwargs)
        pick_kwargs = {} if pick_kwargs is None else dict(pick_kwargs)

        # Always store temporarily so we can pick; drop later if requested.
        self.scan_width_tradeoff(
            X_eval=X_eval,
            y_eval=y_eval,
            store_raw=False,
            store_df=True,
            **scan_kwargs,
        )

        op = self.pick_operating_point(auto_scan=False, **pick_kwargs)

        thr_val = pd.to_numeric(op.get("threshold", np.nan), errors="coerce")
        if not np.isfinite(float(thr_val)):
            raise RuntimeError(
                "Selected operating point has NaN threshold. " f"op={op.to_dict()}"
            )

        self.set_default_threshold(
            float(thr_val),
            operating_point=(op.to_dict() if store_operating_point else None),
        )

        if not store_tradeoff_df:
            self._art.tradeoff_df = None

        return self

    # -------------------- prediction --------------------

    def predict(self, data: ArrayLikeDF) -> Any:
        """
        Predict DockQ for inputs.

        :param data: DataFrame-like containing feature columns.
        :returns: Model predictions.
        """
        self._require(self._art.model is not None, "Model is not fitted.")
        X = self.get_X(data)
        Xp = self._art.preprocessor.transform(X)  # type: ignore[union-attr]
        return self._art.model.predict(Xp)

    def predict_confident(
        self,
        data: ArrayLikeDF,
        *,
        threshold: Optional[float] = None,
        auto_threshold_cfg: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Predict with confidence filtering based on a width threshold.

        Resolution order for threshold:
        1) explicit ``threshold=...``
        2) stored :pyattr:`default_threshold`
        3) auto-select from tradeoff table (may require scanning)

        :param data: DataFrame-like containing feature columns.
        :param threshold: Width threshold. If None, use stored or auto-select.
        :param auto_threshold_cfg:
            Dict with keys:
            - ``scan_kwargs``: passed to :meth:`scan_width_tradeoff`
            - ``pick_kwargs``: passed to :meth:`pick_operating_point`
        :param kwargs:
            Passed through to ``ADConformal.predict_confident_with_threshold``.
        :returns: Output depends on ADConformal implementation.
        """
        self._require(self._art.ad_conf is not None, "ADConformal is not fitted.")
        self._require(
            hasattr(self._art.ad_conf, "predict_confident_with_threshold"),
            "ADConformal missing predict_confident_with_threshold",
        )

        if threshold is None and self._art.default_threshold is not None:
            threshold = float(self._art.default_threshold)

        if threshold is None:
            cfg = dict(auto_threshold_cfg or {})
            scan_kwargs = dict(cfg.get("scan_kwargs") or {})
            if not scan_kwargs:
                scan_kwargs = {
                    "score_type": "fbeta",
                    "beta": 4,
                    "use_abs_pearson": False,
                }

            pick_kwargs = dict(cfg.get("pick_kwargs") or {})
            if not pick_kwargs:
                pick_kwargs = {
                    "metric_col": "pearson_r_in_domain",
                    "mode": "target",
                    "target_coverage": 0.7,
                }

            self.ensure_tradeoff(scan_kwargs=scan_kwargs, require_dataframe=True)
            op = self.pick_operating_point(auto_scan=False, **pick_kwargs)

            thr_val = pd.to_numeric(op.get("threshold", np.nan), errors="coerce")
            if not np.isfinite(float(thr_val)):
                raise RuntimeError(
                    "Selected operating point has NaN threshold. " f"op={op.to_dict()}"
                )
            threshold = float(thr_val)

        X = self.get_X(data)
        Xp = self._art.preprocessor.transform(X)  # type: ignore[union-attr]
        return self._art.ad_conf.predict_confident_with_threshold(
            Xp,
            threshold=float(threshold),
            **kwargs,
        )

    # -------------------- size control / serialization --------------------

    def compact(
        self,
        *,
        drop_calibration: bool = True,
        drop_tradeoff_raw: bool = True,
    ) -> "PepQ":
        """
        Drop large cached artifacts to shrink serialized size.

        :param drop_calibration: Remove cached X_cal/y_cal/X_cal_proc.
        :param drop_tradeoff_raw: Remove raw scan output.
        :returns: self
        """
        if drop_calibration:
            self._art.X_cal = None
            self._art.y_cal = None
            self._art.X_cal_proc = None
        if drop_tradeoff_raw:
            self._art.tradeoff_raw = None
        return self

    def save(
        self,
        path: Union[str, Path],
        *,
        backend: str = "joblib",
        compress: CompressArg = ("xz", 9),
        compact: bool = True,
        drop_calibration: bool = True,
        drop_tradeoff_raw: bool = True,
    ) -> "PepQ":
        """
        Serialize the PepQ object with strong compression.

        Recommended default: ``compress=("xz", 9)`` (smallest files).

        :param path: Output path.
        :param backend: ``"joblib"`` or ``"pickle"``.
        :param compress: joblib compression (e.g. 9 or ("xz", 9)).
        :param compact: If True, call :meth:`compact` before saving.
        :param drop_calibration: If compact=True, remove X_cal/y_cal/X_cal_proc.
        :param drop_tradeoff_raw: If compact=True, remove tradeoff_raw.
        :returns: self
        """
        path = Path(path)
        backend_l = backend.lower()

        if compact:
            self.compact(
                drop_calibration=drop_calibration,
                drop_tradeoff_raw=drop_tradeoff_raw,
            )

        if backend_l == "joblib":
            import joblib

            joblib.dump(self, path, compress=compress)
            return self

        if backend_l == "pickle":
            import pickle

            with path.open("wb") as f:
                pickle.dump(self, f, protocol=pickle.HIGHEST_PROTOCOL)
            return self

        raise ValueError("backend must be one of: 'joblib', 'pickle'")

    @classmethod
    def load(
        cls, path: Union[str, Path] = HERE / "pepq", *, backend: str = "joblib"
    ) -> "PepQ":
        """
        Load a serialized PepQ object.

        :param path: Input path.
        :param backend: ``"joblib"`` or ``"pickle"``.
        :returns: PepQ instance.
        """
        path = Path(path)
        backend_l = backend.lower()

        if backend_l == "joblib":
            import joblib

            obj = joblib.load(path)
        elif backend_l == "pickle":
            import pickle

            with path.open("rb") as f:
                obj = pickle.load(f)
        else:
            raise ValueError("backend must be one of: 'joblib', 'pickle'")

        if not isinstance(obj, cls):
            raise TypeError(f"Loaded object is not a {cls.__name__}: {type(obj)}")
        return obj
