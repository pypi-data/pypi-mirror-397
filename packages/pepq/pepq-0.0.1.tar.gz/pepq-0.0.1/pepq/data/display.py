"""
pepq.data.display
-----------------

Reusable NiceDisplayMixin to provide rich Jupyter card + compact ASCII repr.

The mixin keeps external dependencies minimal (only pandas) and is intended
for interactive use inside notebooks. Subclasses can override the helpers
to customise parameters, feature sets, diagram lines and the summary table.
"""

from __future__ import annotations

from html import escape
from typing import Any, Dict, Iterable, List, Mapping

import pandas as pd


class NiceDisplayMixin:
    """
    Mixin providing a compact HTML card for Jupyter and a simple ASCII repr.

    Subclasses can override helpers:
      - _repr_params_dict() -> Dict[str, Any]
      - _repr_feature_sets() -> Dict[str, List[str]]
      - _ascii_diagram_lines() -> List[str]
      - summary() -> pandas.DataFrame

    Example
    -------
    >>> class P(NiceDisplayMixin):
    ...     def get_params(self, deep=False):
    ...         return {"a": 1}
    ...     def summary(self):
    ...         return pd.DataFrame([{"x": 1}])
    >>> P()  # doctest: +ELLIPSIS
    P()
    """

    # ---------------------------
    # Public helpers / overrides
    # ---------------------------
    def _repr_params_dict(self) -> Dict[str, Any]:
        """
        Return a mapping of parameters to show in the card.

        Defaults to sklearn-like `get_params(deep=False)` if available.

        :returns: dict of parameter names -> values
        """
        if hasattr(self, "get_params"):
            try:
                return self.get_params(deep=False)
            except Exception:
                # fall through to empty
                pass
        return {}

    def _repr_feature_sets(self) -> Dict[str, List[str]]:
        """
        Return groups of feature names to render as chips.

        :returns: mapping group name -> list of feature names
        """
        return {}

    def _ascii_diagram_lines(self) -> List[str]:
        """
        Return ASCII diagram lines for __repr__.

        :returns: list of short strings (each line)
        """
        return [f"{type(self).__name__}()"]

    # ---------------------------
    # Small utility helpers
    # ---------------------------
    def help(self) -> str:
        """
        Return a short help string describing the mixin usage.

        :returns: help string
        """
        return (
            f"{type(self).__name__}: override _repr_params_dict(), "
            "_repr_feature_sets(), _ascii_diagram_lines(), summary()"
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert public repr pieces to a dict (useful for tests).

        :returns: dict with 'params', 'features' and optionally 'summary'
        """
        out: Dict[str, Any] = {}
        out["params"] = self._repr_params_dict()
        out["features"] = self._repr_feature_sets()
        try:
            if hasattr(self, "summary"):
                out["summary"] = getattr(self, "summary")().to_dict(orient="records")
        except Exception:
            out["summary"] = None
        return out

    # ---------------------------
    # Rendering helpers
    # ---------------------------
    def _safe_param_frame(self, params: Mapping[str, Any]) -> str:
        """
        Try to render a params DataFrame to HTML. On error return fallback.

        :param params: mapping of parameter name -> value
        :returns: HTML string
        """
        try:
            df = pd.DataFrame(list(params.items()), columns=["param", "value"])
            return df.to_html(index=False, escape=True)
        except Exception:
            return "<div><em>Unable to render parameters</em></div>"

    def _safe_summary_html(self) -> str:
        """
        Safely obtain the summary() HTML or a fallback string.

        :returns: HTML string
        """
        if not hasattr(self, "summary"):
            return "<div><em>No summary</em></div>"

        try:
            sdf = getattr(self, "summary")()
            if sdf is None:
                return "<div><em>No summary</em></div>"
            return sdf.to_html(index=False, escape=True)
        except Exception:
            return "<div><em>Summary not available</em></div>"

    def _render_chip(self, name: str, color: str = "#0EA5E9") -> str:
        """
        Render a single chip span for a feature.

        :param name: chip label
        :param color: base hex color
        :returns: HTML span string
        """
        txt = escape(str(name))
        style = (
            "display:inline-block;padding:2px 6px;margin:2px;"
            "border-radius:999px;background:"
            + color
            + "20;color:"
            + color
            + ";font-size:11px;"
        )
        return f"<span style='{style}'>{txt}</span>"

    def _render_feature_group(
        self, title: str, names: Iterable[str], color: str
    ) -> str:
        """
        Render a titled feature group with up to 12 chips.

        :param title: group title
        :param names: iterable of feature names
        :param color: hex color for chips
        :returns: HTML block for the group
        """
        items = list(names)[:12]
        if not items:
            chips_html = "<span style='color:#6B7280;'>None</span>"
        else:
            chips_html = " ".join(self._render_chip(n, color=color) for n in items)

        title_html = f"<div style='font-size:11px;color:#374151'>{escape(title)}</div>"
        return f"<div style='margin-bottom:6px'>{title_html}{chips_html}</div>"

    # ---------------------------
    # Jupyter HTML representation
    # ---------------------------
    def _repr_html_(self) -> str:
        """
        Jupyter rich HTML representation.

        :returns: HTML markup (safe-ish)
        """
        title = escape(type(self).__name__)
        params = dict(self._repr_params_dict())

        param_df = self._safe_param_frame(params)
        summary_html = self._safe_summary_html()

        features = self._repr_feature_sets()
        feature_html = ""
        if features:
            parts: List[str] = []
            parts.append("<div style='margin-top:8px'>")
            parts.append(
                "<div style='font-weight:600;margin-bottom:4px;'>Feature overview</div>"
            )

            colors = ["#0EA5E9", "#EF4444", "#10B981"]
            for i, (k, v) in enumerate(features.items()):
                color = colors[i % len(colors)]
                parts.append(self._render_feature_group(k, v, color))
            parts.append("</div>")
            feature_html = "".join(parts)

        # compose html in small chunks to avoid long lines
        html_parts: List[str] = []
        html_parts.append(
            "<div style='font-family:system-ui, -apple-system, BlinkMacSystemFont, "
            "'Segoe UI', sans-serif; font-size:13px; border:1px solid #E5E7EB; "
            "border-radius:8px; padding:10px;background:#FFF;'>"
        )

        header = (
            "<div style='display:flex;justify-content:space-between;align-items:center;"
            "margin-bottom:6px;'>"
        )
        html_parts.append(header)

        left = (
            "<div><div style='font-weight:600'>" + title + "</div>"
            "<div style='font-size:11px;color:#6B7280'>"
            + escape(repr(self))
            + "</div></div>"
        )
        html_parts.append(left)
        html_parts.append(
            "<div style='font-size:11px;padding:2px 8px;border-radius:999px;"
            "background:#E5E7EB;color:#374151'>object</div>"
        )
        html_parts.append("</div>")  # close header

        html_parts.append("<div style='display:flex;gap:12px'>")
        html_parts.append(
            "<div style='flex:1;min-width:200px'><div style='font-weight:600;"
            "margin-bottom:4px'>Parameters</div>" + param_df + "</div>"
        )
        html_parts.append(
            "<div style='flex:1;min-width:200px'><div style='font-weight:600;"
            "margin-bottom:4px'>Summary</div>" + summary_html + "</div>"
        )
        html_parts.append("</div>")  # close two-column area

        if feature_html:
            html_parts.append(feature_html)

        html_parts.append("</div>")  # close main card

        return "".join(html_parts)

    # ---------------------------
    # ASCII repr for consoles / tests
    # ---------------------------
    def __repr__(self) -> str:
        """
        Short multi-line ASCII representation.

        Falls back to object.__repr__ on error.

        :returns: newline-joined ASCII diagram lines
        """
        try:
            lines = self._ascii_diagram_lines()
            return "\n".join(lines)
        except Exception:
            return super().__repr__()
