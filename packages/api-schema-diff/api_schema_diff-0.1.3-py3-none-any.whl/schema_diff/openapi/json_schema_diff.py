from typing import Any, Mapping

from ..models import Change, ChangeSeverity, ChangeType, DiffResult


def _get_type(schema: Mapping[str, Any]) -> str | None:
    t = schema.get("type")
    if isinstance(t, str):
        return t
    return None


def diff_json_schema(
    old: Mapping[str, Any],
    new: Mapping[str, Any],
    *,
    path: str,
    result: DiffResult,
) -> None:
    """
    Minimal JSON Schema diff used inside OpenAPI request/response checks.

    Breaking:
      - type change
      - removed property
      - optional -> required (required added)

    Non-breaking:
      - added property
      - required -> optional (required removed)

    Supports:
      - object/properties/required
      - array/items
      - primitive type comparison
    """
    old_type = _get_type(old)
    new_type = _get_type(new)

    # Type change: if both specified and different -> breaking
    if old_type and new_type and old_type != new_type:
        result.breaking.append(
            Change(
                change_type=ChangeType.TYPE_CHANGE,
                severity=ChangeSeverity.BREAKING,
                path=path,
                old_type=old_type,
                new_type=new_type,
                message="Schema type changed",
            )
        )
        return

    # Object properties
    if (
        (old_type == "object")
        or ("properties" in old)
        or ("required" in old)
        or (new_type == "object")
        or ("properties" in new)
    ):
        old_props = old.get("properties") or {}
        new_props = new.get("properties") or {}

        if not isinstance(old_props, dict):
            old_props = {}
        if not isinstance(new_props, dict):
            new_props = {}

        old_keys = set(k for k in old_props.keys() if isinstance(k, str))
        new_keys = set(k for k in new_props.keys() if isinstance(k, str))

        # removed properties -> breaking
        for k in sorted(old_keys - new_keys):
            result.breaking.append(
                Change(
                    change_type=ChangeType.REMOVED_FIELD,
                    severity=ChangeSeverity.BREAKING,
                    path=f"{path}.properties.{k}",
                    message="Property removed",
                )
            )

        # added properties -> non-breaking
        for k in sorted(new_keys - old_keys):
            result.non_breaking.append(
                Change(
                    change_type=ChangeType.ADDED_FIELD,
                    severity=ChangeSeverity.NON_BREAKING,
                    path=f"{path}.properties.{k}",
                    message="Property added",
                )
            )

        # required changes
        old_req = old.get("required") or []
        new_req = new.get("required") or []
        if not isinstance(old_req, list):
            old_req = []
        if not isinstance(new_req, list):
            new_req = []

        old_req_set = set(x for x in old_req if isinstance(x, str))
        new_req_set = set(x for x in new_req if isinstance(x, str))

        # optional -> required (required added) => breaking
        for k in sorted(new_req_set - old_req_set):
            result.breaking.append(
                Change(
                    change_type=ChangeType.REQUIRED_CHANGE,
                    severity=ChangeSeverity.BREAKING,
                    path=f"{path}.required.{k}",
                    message="Field became required",
                )
            )

        # required -> optional (required removed) => non-breaking
        for k in sorted(old_req_set - new_req_set):
            result.non_breaking.append(
                Change(
                    change_type=ChangeType.REQUIRED_CHANGE,
                    severity=ChangeSeverity.NON_BREAKING,
                    path=f"{path}.required.{k}",
                    message="Field is no longer required",
                )
            )

        # recurse into common properties
        for k in sorted(old_keys & new_keys):
            o = old_props.get(k)
            n = new_props.get(k)
            if isinstance(o, dict) and isinstance(n, dict):
                diff_json_schema(o, n, path=f"{path}.properties.{k}", result=result)

        return

    # Array items
    if (
        (old_type == "array")
        or (new_type == "array")
        or ("items" in old)
        or ("items" in new)
    ):
        old_items = old.get("items")
        new_items = new.get("items")

        if isinstance(old_items, dict) and isinstance(new_items, dict):
            diff_json_schema(old_items, new_items, path=f"{path}.items", result=result)
        return
