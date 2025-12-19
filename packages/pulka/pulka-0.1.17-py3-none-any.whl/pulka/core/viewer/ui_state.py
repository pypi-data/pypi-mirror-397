"""Helpers for persisting per-viewer UI flags."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

INSIGHT_ENABLED_FLAG = "insight_enabled"
INSIGHT_USER_ENABLED_FLAG = "insight_user_enabled"


@dataclass(frozen=True)
class InsightToggleDecision:
    """Resolved insight toggle state for a viewer."""

    enabled: bool
    user_enabled: bool
    allowed: bool

    @property
    def effective(self) -> bool:
        """Return the effective enabled state after applying capability gating."""

        return self.enabled and self.allowed


def inherit_ui_state(parent: Any, child: Any) -> None:
    """Copy known UI flags from ``parent`` to ``child`` without overwriting existing keys."""

    parent_state = get_ui_state(parent)
    if not parent_state:
        return
    combined = get_ui_state(child)
    for key, value in parent_state.items():
        combined.setdefault(key, value)
    child._ui_state = combined


def resolve_insight_state(
    viewer: Any, *, fallback_enabled: bool, user_enabled: bool | None = None
) -> InsightToggleDecision:
    """
    Resolve the persisted insight toggle for ``viewer``.

    ``fallback_enabled`` is used when the viewer does not already have a stored preference.
    """

    stored_enabled, stored_user_enabled = _read_insight_preferences(viewer)
    if _is_soft_disabled(viewer):
        stored_enabled = False
        stored_user_enabled = False
    target_enabled = fallback_enabled if stored_enabled is None else stored_enabled
    target_user_enabled = stored_user_enabled if user_enabled is None else user_enabled
    return _persist_insight_state(viewer, target_enabled, target_user_enabled)


def set_insight_state(
    viewer: Any, *, enabled: bool, user_enabled: bool | None = None
) -> InsightToggleDecision:
    """Persist an explicit insight toggle preference for ``viewer``."""

    _, stored_user_enabled = _read_insight_preferences(viewer)
    target_user_enabled = stored_user_enabled if user_enabled is None else user_enabled
    return _persist_insight_state(viewer, enabled, target_user_enabled)


def get_ui_state(viewer: Any) -> dict[str, object]:
    """Return a copy of the viewer's persisted UI flag mapping."""

    state = getattr(viewer, "_ui_state", None)
    if isinstance(state, dict):
        return dict(state)
    return {}


def _persist_insight_state(viewer: Any, enabled: bool, user_enabled: bool) -> InsightToggleDecision:
    allowed = _insight_allowed(viewer)
    soft_disabled = _is_soft_disabled(viewer)
    effective_enabled = False if (soft_disabled and not user_enabled) else bool(enabled)
    state = getattr(viewer, "_ui_state", None)
    if not isinstance(state, dict):
        state = {}
        viewer._ui_state = state
    state[INSIGHT_ENABLED_FLAG] = effective_enabled
    state[INSIGHT_USER_ENABLED_FLAG] = user_enabled
    return InsightToggleDecision(
        enabled=effective_enabled,
        user_enabled=user_enabled,
        allowed=allowed,
    )


def _read_insight_preferences(viewer: Any) -> tuple[bool | None, bool]:
    state = get_ui_state(viewer)
    raw_enabled = state.get(INSIGHT_ENABLED_FLAG)
    enabled: bool | None = raw_enabled if isinstance(raw_enabled, bool) else None
    raw_user_enabled = state.get(INSIGHT_USER_ENABLED_FLAG)
    user_enabled = bool(raw_user_enabled) if isinstance(raw_user_enabled, bool) else False
    return enabled, user_enabled


def _insight_allowed(viewer: Any) -> bool:
    sheet = getattr(viewer, "sheet", None)
    return not (sheet is not None and getattr(sheet, "is_file_browser", False))


def _is_soft_disabled(viewer: Any) -> bool:
    sheet = getattr(viewer, "sheet", None)
    if sheet is None:
        return False
    return bool(
        getattr(sheet, "is_summary_view", False) or getattr(sheet, "is_transpose_view", False)
    )


__all__ = [
    "INSIGHT_ENABLED_FLAG",
    "INSIGHT_USER_ENABLED_FLAG",
    "InsightToggleDecision",
    "get_ui_state",
    "inherit_ui_state",
    "resolve_insight_state",
    "set_insight_state",
]
