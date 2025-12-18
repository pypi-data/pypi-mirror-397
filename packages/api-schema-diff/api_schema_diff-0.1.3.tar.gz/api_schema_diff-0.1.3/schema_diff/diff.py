from typing import Any

from .models import (
    Change,
    ChangeType,
    ChangeSeverity,
    DiffResult,
)


def _typename(value: Any) -> str:
    if value is None:
        return "null"
    return type(value).__name__


def diff_objects(
    old: Any,
    new: Any,
    path: str = "",
    result: DiffResult | None = None,
) -> DiffResult:
    """
    Deterministic diff of two nested JSON-like objects.

    Rules (v0.1):
    - Removed fields      → breaking
    - Type changes        → breaking
    - Added fields        → non-breaking
    """
    if result is None:
        result = DiffResult()

    # Type change at node level → breaking
    if _typename(old) != _typename(new):
        result.breaking.append(
            Change(
                change_type=ChangeType.TYPE_CHANGE,
                severity=ChangeSeverity.BREAKING,
                path=path or "$",
                old_type=_typename(old),
                new_type=_typename(new),
                message="Type changed",
            )
        )
        return result

    # Dict comparison
    if isinstance(old, dict) and isinstance(new, dict):
        old_keys = set(old.keys())
        new_keys = set(new.keys())

        # Removed fields → breaking
        for key in sorted(old_keys - new_keys):
            p = f"{path}.{key}" if path else key
            result.breaking.append(
                Change(
                    change_type=ChangeType.REMOVED_FIELD,
                    severity=ChangeSeverity.BREAKING,
                    path=p,
                    message="Field removed",
                )
            )

        # Added fields → non-breaking
        for key in sorted(new_keys - old_keys):
            p = f"{path}.{key}" if path else key
            result.non_breaking.append(
                Change(
                    change_type=ChangeType.ADDED_FIELD,
                    severity=ChangeSeverity.NON_BREAKING,
                    path=p,
                    message="Field added",
                )
            )

        # Recurse into common fields
        for key in sorted(old_keys & new_keys):
            p = f"{path}.{key}" if path else key
            diff_objects(old[key], new[key], p, result)

        return result

    # List comparison (MVP rule)
    if isinstance(old, list) and isinstance(new, list):
        if old and new:
            diff_objects(
                old[0],
                new[0],
                f"{path}[]" if path else "[]",
                result,
            )
        return result

    # Primitive types, same type → no change
    return result
