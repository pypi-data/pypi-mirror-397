import pandas as pd
from typing import Dict, Optional
from ._get_score import get_data


DOCKQ_THRESHOLD = 0.23


def build_data(
    data: Dict,
    dockq: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """
    Build a modeling-ready dataframe from AlphaFold-Multimer summaries,
    optionally merged with DockQ results.

    The function always:
      1) Flattens summary objects returned by :func:`get_data`
      2) Normalizes identifiers and ranks
      3) Returns a clean feature table

    If ``dockq`` is provided, it additionally:
      4) Merges DockQ scores via a stable (complex_id, rank) key
      5) Adds regression target ``dockq`` and binary ``label``

    If ``dockq`` is None, the function **skips merging** and returns
    summary features only.

    Parameters
    ----------
    data : dict
        Raw input object consumed by :func:`get_data`.
        Expected to describe per-complex confidence and interface summaries.

    dockq : pandas.DataFrame, optional
        DockQ results table containing at least:
          - ``id``   : complex identifier
          - ``Rank`` : integer rank (0, 1, 2, …)
          - ``GlobalDockQ``

        If None, DockQ-dependent columns are not added.

    Returns
    -------
    pandas.DataFrame
        Feature dataframe suitable for:
          - DockQ regression (if dockq is provided)
          - DockQ classification (binary label)
          - Feature analysis / visualization (if dockq is None)

    Raises
    ------
    KeyError
        If required identifier columns are missing.
    """

    # ------------------------------------------------------------
    # 1) Flatten & normalize summary data
    # ------------------------------------------------------------
    df = pd.DataFrame(get_data(data))

    required_summary_cols = {"complex_id", "rank"}
    missing = required_summary_cols - set(df.columns)
    if missing:
        raise KeyError(f"Summary data missing required columns: {missing}")

    df = df.copy()
    df["merge"] = df["complex_id"].astype(str) + "_" + df["rank"].astype(str)

    # ------------------------------------------------------------
    # 2) Define feature columns (robust selection)
    # ------------------------------------------------------------
    feature_cols = [
        # global confidence
        "prot_plddt",
        "pep_plddt",
        "PTM",
        "PAE",
        "iptm",
        "composite_ptm",
        "actifptm",
        # interface summaries (optional / expandable)
        # "prot_if_n",
        # "pep_if_n",
        # "if_n_total",
        # "prot_if_span",
        # "pep_if_span",
        # "prot_if_coverage",
        # "pep_if_coverage",
        # "prot_if_n_segments",
        # "pep_if_n_segments",
    ]

    feature_cols = [c for c in feature_cols if c in df.columns]

    # ------------------------------------------------------------
    # 3) Early return if DockQ is not provided
    # ------------------------------------------------------------
    if dockq is None:
        return df[feature_cols + ["complex_id", "rank"]]

    # ------------------------------------------------------------
    # 4) Prepare DockQ table
    # ------------------------------------------------------------
    required_dockq_cols = {"id", "Rank", "GlobalDockQ"}
    missing = required_dockq_cols - set(dockq.columns)
    if missing:
        raise KeyError(f"DockQ table missing required columns: {missing}")

    dockq = dockq.copy()
    dockq["rank"] = "rank00" + dockq["Rank"].astype(str)
    dockq["merge"] = dockq["id"].astype(str) + "_" + dockq["rank"].astype(str)

    # ------------------------------------------------------------
    # 5) Merge summary with DockQ
    # ------------------------------------------------------------
    merged = df.merge(
        dockq,
        on="merge",
        how="inner",
        suffixes=("", "_dockq"),
    )

    merged = merged.rename(columns={"GlobalDockQ": "dockq"})

    # Binary classification label
    merged["label"] = (merged["dockq"] >= DOCKQ_THRESHOLD).astype(int)

    return merged[feature_cols + ["dockq", "label"]]
