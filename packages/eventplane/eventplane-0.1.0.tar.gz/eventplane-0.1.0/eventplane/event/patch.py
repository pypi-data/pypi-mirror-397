from __future__ import annotations

from typing import Any, Dict, Optional


class EventPatch:
    """
    Partial mutation of an Event.

    Rules:
    - Patch MUST be idempotent
    - Patch MUST NOT delete fields (only add / update)
    - Patch MUST be mergeable
    """

    def __init__(
        self,
        *,
        spec: Optional[Dict[str, Any]] = None,
        status: Optional[Dict[str, Any]] = None,
        finalizers: Optional[Dict[str, Any]] = None,
    ):
        self.spec = spec
        self.status = status
        self.finalizers = finalizers

    # ---------- Factories ----------

    @staticmethod
    def spec(values: Dict[str, Any]) -> "EventPatch":
        """
        Patch spec fields.
        """
        return EventPatch(spec=values)

    @staticmethod
    def status(values: Dict[str, Any]) -> "EventPatch":
        """
        Patch status fields.
        """
        return EventPatch(status=values)

    @staticmethod
    def finalizers(values: Dict[str, Any]) -> "EventPatch":
        """
        Patch finalizers fields.
        """
        return EventPatch(finalizers=values)

    # ---------- Utilities ----------

    def is_empty(self) -> bool:
        return not any([self.spec, self.status, self.finalizers])

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to serializable dict.
        """
        data: Dict[str, Any] = {}

        if self.spec:
            data["spec"] = self.spec

        if self.status:
            data["status"] = self.status

        if self.finalizers:
            data["finalizers"] = self.finalizers

        return data

    def merge(self, other: "EventPatch") -> "EventPatch":
        """
        Merge another patch into this one.
        Later patch wins.
        """
        return EventPatch(
            spec=_deep_merge(self.spec, other.spec),
            status=_deep_merge(self.status, other.status),
            finalizers=_deep_merge(self.finalizers, other.finalizers),
        )


# ---------- Internal helpers ----------

def _deep_merge(
    base: Optional[Dict[str, Any]],
    incoming: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    """
    Deep merge dictionaries.
    incoming values override base.
    """
    if base is None:
        return incoming
    if incoming is None:
        return base

    merged = dict(base)

    for key, value in incoming.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value

    return merged
