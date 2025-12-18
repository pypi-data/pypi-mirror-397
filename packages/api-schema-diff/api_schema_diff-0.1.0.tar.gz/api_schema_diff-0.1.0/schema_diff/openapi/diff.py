from typing import Any, Mapping

from ..models import Change, ChangeSeverity, ChangeType, DiffResult
from .json_schema_diff import diff_json_schema
from .normalizer import normalize_openapi


def diff_openapi(old_raw: Mapping[str, Any], new_raw: Mapping[str, Any]) -> DiffResult:
    old = normalize_openapi(old_raw)
    new = normalize_openapi(new_raw)

    result = DiffResult()

    old_paths = set(old.paths.keys())
    new_paths = set(new.paths.keys())

    # Paths removed/added
    for p in sorted(old_paths - new_paths):
        result.breaking.append(
            Change(
                ChangeType.REMOVED_FIELD,
                ChangeSeverity.BREAKING,
                f"paths.{p}",
                message="Path removed",
            )
        )
    for p in sorted(new_paths - old_paths):
        result.non_breaking.append(
            Change(
                ChangeType.ADDED_FIELD,
                ChangeSeverity.NON_BREAKING,
                f"paths.{p}",
                message="Path added",
            )
        )

    # Operations removed/added
    for p in sorted(old_paths & new_paths):
        old_methods = set(old.paths.get(p, set()))
        new_methods = set(new.paths.get(p, set()))

        for m in sorted(old_methods - new_methods):
            result.breaking.append(
                Change(
                    ChangeType.REMOVED_FIELD,
                    ChangeSeverity.BREAKING,
                    f"paths.{p}.{m}",
                    message="Operation removed",
                )
            )
        for m in sorted(new_methods - old_methods):
            result.non_breaking.append(
                Change(
                    ChangeType.ADDED_FIELD,
                    ChangeSeverity.NON_BREAKING,
                    f"paths.{p}.{m}",
                    message="Operation added",
                )
            )

    # Common operations: params + request + responses
    common_ops = set(old.operations.keys()) & set(new.operations.keys())
    for op_key in sorted(common_ops):
        old_op = old.operations[op_key]
        new_op = new.operations[op_key]

        # ----------------------------
        # PARAMETERS (query/path)
        # ----------------------------
        old_params = old_op.parameters
        new_params = new_op.parameters

        old_keys = set(old_params.keys())
        new_keys = set(new_params.keys())

        # removed params -> breaking
        for k in sorted(old_keys - new_keys):
            spec = old_params[k]
            result.breaking.append(
                Change(
                    change_type=ChangeType.REMOVED_FIELD,
                    severity=ChangeSeverity.BREAKING,
                    path=f"operations.{op_key}.parameters.{spec.location}.{spec.name}",
                    message="Parameter removed",
                )
            )

        # added params -> required? breaking else non-breaking
        for k in sorted(new_keys - old_keys):
            spec = new_params[k]
            if spec.required:
                result.breaking.append(
                    Change(
                        change_type=ChangeType.REQUIRED_CHANGE,
                        severity=ChangeSeverity.BREAKING,
                        path=f"operations.{op_key}.parameters.{spec.location}.{spec.name}",
                        message="Required parameter added",
                    )
                )
            else:
                result.non_breaking.append(
                    Change(
                        change_type=ChangeType.ADDED_FIELD,
                        severity=ChangeSeverity.NON_BREAKING,
                        path=f"operations.{op_key}.parameters.{spec.location}.{spec.name}",
                        message="Optional parameter added",
                    )
                )

        # common params: required flip + schema diff
        for k in sorted(old_keys & new_keys):
            o = old_params[k]
            n = new_params[k]

            if o.required != n.required:
                if n.required:
                    result.breaking.append(
                        Change(
                            change_type=ChangeType.REQUIRED_CHANGE,
                            severity=ChangeSeverity.BREAKING,
                            path=f"operations.{op_key}.parameters.{n.location}.{n.name}.required",
                            message="Parameter became required",
                        )
                    )
                else:
                    result.non_breaking.append(
                        Change(
                            change_type=ChangeType.REQUIRED_CHANGE,
                            severity=ChangeSeverity.NON_BREAKING,
                            path=f"operations.{op_key}.parameters.{n.location}.{n.name}.required",
                            message="Parameter is no longer required",
                        )
                    )

            if isinstance(o.schema, dict) and isinstance(n.schema, dict):
                diff_json_schema(
                    o.schema,
                    n.schema,
                    path=f"operations.{op_key}.parameters.{n.location}.{n.name}.schema",
                    result=result,
                )

        # ----------------------------
        # requestBody presence + schema
        # ----------------------------
        old_has_req = old_op.request_schema is not None
        new_has_req = new_op.request_schema is not None

        if old_has_req and not new_has_req:
            result.breaking.append(
                Change(
                    ChangeType.REMOVED_FIELD,
                    ChangeSeverity.BREAKING,
                    f"operations.{op_key}.requestBody",
                    message="Request body removed",
                )
            )
        elif (not old_has_req) and new_has_req:
            if new_op.request_required:
                result.breaking.append(
                    Change(
                        ChangeType.REQUIRED_CHANGE,
                        ChangeSeverity.BREAKING,
                        f"operations.{op_key}.requestBody",
                        message="Required request body added",
                    )
                )
            else:
                result.non_breaking.append(
                    Change(
                        ChangeType.ADDED_FIELD,
                        ChangeSeverity.NON_BREAKING,
                        f"operations.{op_key}.requestBody",
                        message="Optional request body added",
                    )
                )
        elif old_has_req and new_has_req:
            diff_json_schema(
                old_op.request_schema or {},
                new_op.request_schema or {},
                path=f"operations.{op_key}.requestBody.schema",
                result=result,
            )

            if old_op.request_required != new_op.request_required:
                if new_op.request_required:
                    result.breaking.append(
                        Change(
                            ChangeType.REQUIRED_CHANGE,
                            ChangeSeverity.BREAKING,
                            f"operations.{op_key}.requestBody.required",
                            message="Request body became required",
                        )
                    )
                else:
                    result.non_breaking.append(
                        Change(
                            ChangeType.REQUIRED_CHANGE,
                            ChangeSeverity.NON_BREAKING,
                            f"operations.{op_key}.requestBody.required",
                            message="Request body is no longer required",
                        )
                    )

        # ----------------------------
        # responses: statuses + schema
        # ----------------------------
        old_statuses = set(old_op.responses.keys())
        new_statuses = set(new_op.responses.keys())

        for status in sorted(old_statuses - new_statuses):
            result.breaking.append(
                Change(
                    ChangeType.REMOVED_FIELD,
                    ChangeSeverity.BREAKING,
                    f"operations.{op_key}.responses.{status}",
                    message="Response status removed",
                )
            )
        for status in sorted(new_statuses - old_statuses):
            result.non_breaking.append(
                Change(
                    ChangeType.ADDED_FIELD,
                    ChangeSeverity.NON_BREAKING,
                    f"operations.{op_key}.responses.{status}",
                    message="Response status added",
                )
            )

        for status in sorted(old_statuses & new_statuses):
            old_schema = old_op.responses.get(status)
            new_schema = new_op.responses.get(status)

            if old_schema is not None and new_schema is None:
                result.breaking.append(
                    Change(
                        ChangeType.REMOVED_FIELD,
                        ChangeSeverity.BREAKING,
                        f"operations.{op_key}.responses.{status}.schema",
                        message="Response schema removed",
                    )
                )
                continue
            if old_schema is None and new_schema is not None:
                result.non_breaking.append(
                    Change(
                        ChangeType.ADDED_FIELD,
                        ChangeSeverity.NON_BREAKING,
                        f"operations.{op_key}.responses.{status}.schema",
                        message="Response schema added",
                    )
                )
                continue

            if isinstance(old_schema, dict) and isinstance(new_schema, dict):
                diff_json_schema(
                    old_schema,
                    new_schema,
                    path=f"operations.{op_key}.responses.{status}.schema",
                    result=result,
                )

    return result
