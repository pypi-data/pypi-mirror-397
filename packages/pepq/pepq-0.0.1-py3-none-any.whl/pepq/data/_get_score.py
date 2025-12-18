"""
pepq._get_score
===============

PLDDT/PTM/PAE helper utilities and :func:`get_data`.

This module provides robust readers for compact summary arrays produced by
``MetricsCalculator.summarize_plddt`` / ``summarize_pae`` /
``calculate_ptm_values`` and a helper :func:`get_data` that flattens
per-complex rank entries and attaches derived numeric summaries.

Semantic map
------------
**pLDDT summary array** (from ``summarize_plddt``):

- ``plddt[0]`` -> mean pLDDT over all residues
- ``plddt[1]`` -> median pLDDT over all residues
- ``plddt[2]`` -> peptide mean pLDDT (peptide-specific)
- ``plddt[3]`` -> interface overall average pLDDT (prot+pep interface)

**pTM array** (from ``calculate_ptm_values``):

- ``ptm[0]`` -> global pTM (float or None)
- ``ptm[1:]`` -> per-chain pTM values sorted by chain ID (lexicographic)

**PAE summary array** (from ``summarize_pae``):

- ``pae[0]`` -> max PAE (numeric or None)
- ``pae[1]`` -> mean of flattened PAE matrix
- ``pae[2]`` -> median of flattened PAE matrix
- ``pae[3]`` -> coverage in [0, 1] (longest-run metric)

Interface map
-------------
Typical interface structure:

- ``interface["prot_interface"]`` -> list of protein residue indices
- ``interface["pep_interface"]``  -> list of peptide residue indices

From these lists we derive compact scalar descriptors such as:

- ``prot_if_n``, ``pep_if_n``, ``if_n_total``
- ``prot_if_span``, ``pep_if_span``
- ``prot_if_coverage``, ``pep_if_coverage``
- ``prot_if_n_segments``, ``pep_if_n_segments``
"""

from __future__ import annotations

from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Mapping,
    MutableMapping,
    Optional,
    Set,
    Tuple,
)

import numpy as np


# --------------------------------------------------------------------------- #
# Core helpers
# --------------------------------------------------------------------------- #
def _is_number(obj: Any) -> bool:
    """
    Check if *obj* is a numeric scalar.

    :param obj: Any python object.
    :returns: True for int/float/numpy scalar (excluding bool), else False.
    """
    if isinstance(obj, bool):
        return False
    return isinstance(obj, (int, float, np.integer, np.floating))


def _safe_float(obj: Any) -> Optional[float]:
    """
    Convert a value to float and require finiteness.

    :param obj: Any value.
    :returns: float if finite, otherwise None.
    """
    try:
        val = float(obj)
    except Exception:
        return None
    if np.isnan(val) or np.isinf(val):
        return None
    return val


def _as_list(obj: Any) -> Optional[List[Any]]:
    """
    Convert iterable-like objects to a list.

    :param obj: Any value.
    :returns: list(obj) if possible, otherwise None.
    """
    try:
        return list(obj)
    except Exception:
        return None


def _finite_floats(values: Iterable[Any]) -> List[float]:
    """
    Filter an iterable to finite floats.

    :param values: Iterable of mixed values.
    :returns: List of finite floats.
    """
    out: List[float] = []
    for v in values:
        fv = _safe_float(v)
        if fv is not None:
            out.append(fv)
    return out


def _summary_select(
    values: Optional[Iterable[Any]], select: str = "mean"
) -> Optional[float]:
    """
    Safely summarize an iterable of numbers.

    :param values: Iterable of numeric-like values (or None).
    :param select: One of ``mean``, ``median``, ``min``, ``max``, ``first``, ``last``.
    :returns: Summary float or None.
    """
    if values is None:
        return None

    arr = _finite_floats(values)
    if not arr:
        return None

    s = select.lower()
    a = np.asarray(arr, dtype=float)

    if s == "mean":
        return float(np.nanmean(a))
    if s == "median":
        return float(np.nanmedian(a))
    if s == "min":
        return float(np.nanmin(a))
    if s == "max":
        return float(np.nanmax(a))
    if s == "first":
        return float(a[0])
    if s == "last":
        return float(a[-1])

    return float(np.nanmean(a))


def _pick_index(seq: List[Any], idx: int) -> Optional[float]:
    """
    Safely pick and coerce a sequence element.

    :param seq: Sequence converted to a list.
    :param idx: Index to pick.
    :returns: Float value if present and finite, else None.
    """
    if idx < 0 or idx >= len(seq):
        return None
    return _safe_float(seq[idx])


# --------------------------------------------------------------------------- #
# pLDDT helpers
# --------------------------------------------------------------------------- #
_PLDDT_INDEX = {
    "mean": 0,
    "median": 1,
    "peptide": 2,
    "pep": 2,
    "interface": 3,
    "interface_avg": 3,
}

_PLDDT_DICT_KEYS = ("prot_plddt", "prot", "protein")


def _get_plddt_from_mapping(scores: Mapping[str, Any], select: str) -> Optional[float]:
    """
    pLDDT getter for mapping-like inputs.

    :param scores: Mapping input.
    :param select: Selection string.
    :returns: pLDDT value or None.
    """
    sel = select.lower()

    for key in _PLDDT_DICT_KEYS:
        if key in scores:
            base_sel = "mean" if sel in ("peptide", "interface") else sel
            return _summary_select(scores.get(key), select=base_sel)

    if "plddt" in scores:
        base_sel = "min" if sel in ("peptide", "interface") else sel
        return _summary_select(scores.get("plddt"), select=base_sel)

    return None


def _get_plddt_from_sequence(seq: List[Any], select: str) -> Optional[float]:
    """
    pLDDT getter for sequence-like inputs.

    :param seq: pLDDT list-like.
    :param select: Selection string.
    :returns: pLDDT value or None.
    """
    sel = select.lower()
    if sel in _PLDDT_INDEX:
        val = _pick_index(seq, _PLDDT_INDEX[sel])
        if val is not None:
            return val
        fallback_sel = "mean" if sel in ("peptide", "interface") else sel
        return _summary_select(seq, select=fallback_sel)

    if sel in ("min", "max", "first", "last", "median"):
        return _summary_select(seq, select=sel)

    return _summary_select(seq, select="mean")


def _get_plddt(scores: Any, select: str = "mean") -> Optional[float]:
    """
    Robustly extract a protein pLDDT summary.

    :param scores: Source (list/dict/number/None).
    :param select: Selection (``mean``, ``median``, ``peptide``, ``interface``, etc.).
    :returns: Optional float.
    """
    if scores is None:
        return None

    if isinstance(scores, Mapping):
        return _get_plddt_from_mapping(scores, select)

    if _is_number(scores):
        return _safe_float(scores)

    seq = _as_list(scores)
    if seq is None:
        return None

    return _get_plddt_from_sequence(seq, select)


def _get_pep_plddt(scores: Any) -> Optional[float]:
    """
    Extract peptide pLDDT.

    :param scores: Source (list/dict/number/None).
    :returns: Optional float.
    """
    if scores is None:
        return None

    if isinstance(scores, Mapping):
        for key in ("pep_plddt", "pep", "peptide"):
            if key in scores:
                return _summary_select(scores.get(key), select="mean")
        if "plddt" in scores:
            return _summary_select(scores.get("plddt"), select="min")
        return None

    if _is_number(scores):
        return _safe_float(scores)

    seq = _as_list(scores)
    if seq is None:
        return None

    val = _pick_index(seq, 2)
    if val is not None:
        return val
    return _summary_select(seq, select="min")


# --------------------------------------------------------------------------- #
# pTM helpers
# --------------------------------------------------------------------------- #
def _get_ptml(scores: Any, select: str = "mean") -> Optional[float]:
    """
    Read pTM values.

    :param scores: Source (list/dict/number/None).
    :param select: Selection string.
    :returns: Optional float.
    """
    if scores is None:
        return None

    if isinstance(scores, Mapping):
        if "ptm" in scores:
            return _summary_select(scores.get("ptm"), select=select)
        return _summary_select(scores.values(), select=select)

    if _is_number(scores):
        return _safe_float(scores)

    seq = _as_list(scores)
    if seq is None:
        return None

    sel = select.lower()
    if sel == "mean":
        return _pick_index(seq, 0) or _summary_select(seq, select="mean")
    if sel == "median":
        return _pick_index(seq, 1) or _summary_select(seq, select="median")

    return _summary_select(seq, select=sel)


# --------------------------------------------------------------------------- #
# PAE helpers
# --------------------------------------------------------------------------- #
_PAE_INDEX = {"max": 0, "mean": 1, "median": 2, "coverage": 3, "converage": 3}


def _get_pae(scores: Any, select: str = "mean") -> Optional[float]:
    """
    Extract a PAE summary value from the compact PAE summary array.

    :param scores: Source (list/dict/number/None).
    :param select: Selection (``max``, ``mean``, ``median``, ``coverage``).
    :returns: Optional float.
    """
    if scores is None:
        return None

    if isinstance(scores, Mapping):
        if "pae" in scores:
            return _summary_select(scores.get("pae"), select=select)
        return _summary_select(scores.values(), select=select)

    if _is_number(scores):
        return _safe_float(scores)

    seq = _as_list(scores)
    if seq is None:
        return None

    sel = select.lower()
    if sel in _PAE_INDEX:
        return _pick_index(seq, _PAE_INDEX[sel]) or _summary_select(seq, select=sel)

    return _summary_select(seq, select=sel)


# --------------------------------------------------------------------------- #
# Interface helpers
# --------------------------------------------------------------------------- #
def _summarise_index_list(idxs: Any) -> Dict[str, float]:
    """
    Summarise a list/array of residue indices into compact scalar features.

    :param idxs: Iterable of residue indices (int-like) or None/empty.
    :returns: Dictionary with keys:
        ``n``, ``span``, ``coverage``, ``n_segments``, ``center``, ``std_idx``,
        ``max_gap``, ``mean_gap``.
    """
    seq = _as_list(idxs)
    if not seq:
        return {
            "n": 0.0,
            "span": 0.0,
            "coverage": 0.0,
            "n_segments": 0.0,
            "center": np.nan,
            "std_idx": np.nan,
            "max_gap": np.nan,
            "mean_gap": np.nan,
        }

    try:
        arr = np.asarray(seq, dtype=int)
    except Exception:
        arr = np.asarray([], dtype=int)

    if arr.size == 0:
        return {
            "n": 0.0,
            "span": 0.0,
            "coverage": 0.0,
            "n_segments": 0.0,
            "center": np.nan,
            "std_idx": np.nan,
            "max_gap": np.nan,
            "mean_gap": np.nan,
        }

    arr = np.sort(arr)
    n = float(arr.size)
    span = float(int(arr[-1]) - int(arr[0]) + 1)
    span = max(span, 0.0)

    if arr.size == 1:
        diffs = np.asarray([], dtype=float)
        n_segments = 1.0
    else:
        diffs = np.diff(arr).astype(float)
        n_segments = float(1 + np.sum(diffs != 1))

    coverage = float(n / span) if span > 0 else 0.0
    center = float(np.mean(arr))
    std_idx = float(np.std(arr)) if arr.size > 1 else 0.0

    max_gap = float(np.max(diffs)) if diffs.size else np.nan
    mean_gap = float(np.mean(diffs)) if diffs.size else np.nan

    return {
        "n": n,
        "span": span,
        "coverage": coverage,
        "n_segments": n_segments,
        "center": center,
        "std_idx": std_idx,
        "max_gap": max_gap,
        "mean_gap": mean_gap,
    }


def _interface_features(prot_idxs: Any, pep_idxs: Any) -> Dict[str, float]:
    """
    Build flat interface summary features from protein/peptide index lists.

    :param prot_idxs: Protein interface residue indices (or None/empty).
    :param pep_idxs: Peptide interface residue indices (or None/empty).
    :returns: Flat dict with keys:
        - ``prot_if_*`` and ``pep_if_*`` summaries
        - ``if_n_total``
        - ``if_n_ratio_pep_over_prot``
    """
    prot_feats = _summarise_index_list(prot_idxs)
    pep_feats = _summarise_index_list(pep_idxs)

    out: Dict[str, float] = {}
    for key, val in prot_feats.items():
        out[f"prot_if_{key}"] = float(val) if val is not None else np.nan
    for key, val in pep_feats.items():
        out[f"pep_if_{key}"] = float(val) if val is not None else np.nan

    out["if_n_total"] = out["prot_if_n"] + out["pep_if_n"]
    out["if_n_ratio_pep_over_prot"] = (
        out["pep_if_n"] / out["prot_if_n"] if out["prot_if_n"] > 0 else np.nan
    )
    return out


def _extract_interface_indices(record: Mapping[str, Any]) -> Tuple[Any, Any]:
    """
    Extract (prot_idxs, pep_idxs) from a record.

    :param record: Record mapping.
    :returns: Tuple (prot_idxs, pep_idxs), each can be None or list-like.
    """
    interface = record.get("interface")
    prot_idxs: Any = None
    pep_idxs: Any = None

    if isinstance(interface, Mapping):
        prot_idxs = (
            interface.get("prot_interface")
            or interface.get("prot")
            or interface.get("protein")
        )
        pep_idxs = (
            interface.get("pep_interface")
            or interface.get("pep")
            or interface.get("peptide")
        )

    if prot_idxs is None and "prot_interface" in record:
        prot_idxs = record.get("prot_interface")
    if pep_idxs is None and "pep_interface" in record:
        pep_idxs = record.get("pep_interface")

    return prot_idxs, pep_idxs


# --------------------------------------------------------------------------- #
# get_data: flatten and attach derived scores
# --------------------------------------------------------------------------- #
def _iter_rank_entries(
    ranks: Mapping[str, Any],
    rank: Optional[str],
) -> Iterable[Tuple[str, Mapping[str, Any]]]:
    """
    Yield (rank_key, record) pairs.

    :param ranks: Mapping of rank keys -> record mappings.
    :param rank: Specific rank key or None (auto-detect rank*).
    :yields: Tuples of (rank_key, record_mapping).
    """
    if rank is not None:
        rec = ranks.get(rank)
        if isinstance(rec, Mapping):
            yield rank, rec
        return

    for rk, rv in ranks.items():
        if isinstance(rv, Mapping) and str(rk).lower().startswith("rank"):
            yield str(rk), rv


def _attach_derived_fields(
    record: MutableMapping[str, Any],
    plddt_select: str,
    ptm_select: str,
    pae_select: str,
) -> None:
    """
    Attach derived PLDDT / PTM / PAE fields to a record (in-place).

    :param record: Record dict to update.
    :param plddt_select: Selection passed to :func:`_get_plddt`.
    :param ptm_select: Selection passed to :func:`_get_ptml`.
    :param pae_select: Selection passed to :func:`_get_pae`.
    """
    plddt_val = record.get("plddt")
    record["prot_plddt"] = _get_plddt(plddt_val, select=plddt_select)
    record["pep_plddt"] = _get_pep_plddt(plddt_val)

    record["PTM"] = _get_ptml(record.get("ptm"), select=ptm_select)
    record["PAE"] = _get_pae(record.get("pae"), select=pae_select)


def _filter_record(record: Mapping[str, Any], keep: Set[str]) -> Dict[str, Any]:
    """
    Filter a record to a stable subset of fields.

    Always keeps ``complex_id`` and ``rank``.

    :param record: Record mapping.
    :param keep: Keys to keep.
    :returns: Filtered record dict.
    """
    out: Dict[str, Any] = {
        "complex_id": record.get("complex_id"),
        "rank": record.get("rank"),
    }
    for key in keep:
        if key in record:
            out[key] = record[key]
    return out


def get_data(
    data: Mapping[str, Mapping[str, MutableMapping[str, Any]]],
    rank: Optional[str] = None,
    plddt_select: str = "mean",
    ptm_select: str = "mean",
    pae_select: str = "mean",
    select_score: Optional[Iterable[str]] = (
        "prot_plddt",
        "pep_plddt",
        "PTM",
        "PAE",
        "iptm",
        "actifptm",
        "composite_ptm",
        "prot_if_n",
        "pep_if_n",
        "if_n_total",
        "prot_if_span",
        "pep_if_span",
        "prot_if_coverage",
        "pep_if_coverage",
        "prot_if_n_segments",
        "pep_if_n_segments",
    ),
) -> List[Dict[str, Any]]:
    """
    Flatten *data* and attach derived numeric summaries.

    :param data: Mapping ``complex_id -> mapping(rank_key -> record mapping)``.
    :param rank: Optional specific rank key to select (e.g. ``"rank001"``).
    :param plddt_select: Selection passed to :func:`_get_plddt`.
    :param ptm_select: Selection passed to :func:`_get_ptml`.
    :param pae_select: Selection passed to :func:`_get_pae`.
    :param select_score: Iterable of keys to keep; if None keep everything.
    :returns: List of flattened record dicts.
    """
    keep_scores: Optional[Set[str]] = (
        set(select_score) if select_score is not None else None
    )
    records: List[Dict[str, Any]] = []

    for complex_id, ranks in data.items():
        for rank_key, rec in _iter_rank_entries(ranks, rank):
            record: Dict[str, Any] = dict(rec) if rec is not None else {}
            record["complex_id"] = complex_id
            record["rank"] = rank_key

            _attach_derived_fields(record, plddt_select, ptm_select, pae_select)

            prot_idxs, pep_idxs = _extract_interface_indices(record)
            record.update(_interface_features(prot_idxs, pep_idxs))

            if keep_scores is not None:
                records.append(_filter_record(record, keep_scores))
            else:
                records.append(record)

    return records
