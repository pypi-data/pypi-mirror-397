from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Set

from .resolver import resolve_schema

_HTTP_METHODS = {"get", "put", "post", "delete", "patch", "head", "options", "trace"}
_PARAM_IN_ALLOWED = {"query", "path", "header"}


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    location: str  # "query" | "path"
    required: bool
    schema: dict[str, Any] | None  # resolved (best-effort)


@dataclass(frozen=True)
class OperationSchemas:
    request_required: bool
    request_schema: dict[str, Any] | None
    responses: dict[str, dict[str, Any] | None]  # status -> schema
    parameters: dict[str, ParameterSpec]  # key -> spec (key is "in:name")


@dataclass(frozen=True)
class NormalizedOpenAPI:
    paths: Dict[str, Set[str]]
    operations: Dict[str, OperationSchemas]


def normalize_openapi(raw: Mapping[str, Any]) -> NormalizedOpenAPI:
    paths_raw = raw.get("paths") or {}
    if not isinstance(paths_raw, dict):
        raise ValueError("OpenAPI 'paths' must be an object")

    paths: Dict[str, Set[str]] = {}
    operations: Dict[str, OperationSchemas] = {}

    for path, path_item in paths_raw.items():
        if not isinstance(path, str) or not isinstance(path_item, dict):
            continue

        # parameters can exist at PATH ITEM level and apply to all ops under that path
        base_params = _parse_parameters(path_item.get("parameters"), raw)

        methods: Set[str] = set()

        for k, op in path_item.items():
            method = str(k).lower()
            if method not in _HTTP_METHODS or not isinstance(op, dict):
                continue

            methods.add(method)
            op_key = f"{method.upper()} {path}"

            # merge: path-item params + op params (op overrides same (in,name))
            op_params = dict(base_params)
            op_params.update(_parse_parameters(op.get("parameters"), raw))

            # requestBody: application/json only (MVP)
            req_required = False
            req_schema = None
            request_body = op.get("requestBody")
            if isinstance(request_body, dict):
                req_required = bool(request_body.get("required", False))
                content = request_body.get("content", {})
                if isinstance(content, dict):
                    app_json = content.get("application/json")
                    if isinstance(app_json, dict):
                        schema = app_json.get("schema")
                        if isinstance(schema, dict):
                            req_schema = resolve_schema(schema, raw)

            # responses: collect application/json schemas per status code
            responses_out: dict[str, dict[str, Any] | None] = {}
            responses = op.get("responses", {})
            if isinstance(responses, dict):
                for status, resp in responses.items():
                    if not isinstance(status, str) or not isinstance(resp, dict):
                        continue
                    schema_dict = None
                    content = resp.get("content", {})
                    if isinstance(content, dict):
                        app_json = content.get("application/json")
                        if isinstance(app_json, dict):
                            schema = app_json.get("schema")
                            if isinstance(schema, dict):
                                schema_dict = resolve_schema(schema, raw)
                    responses_out[status] = schema_dict

            operations[op_key] = OperationSchemas(
                request_required=req_required,
                request_schema=req_schema,
                responses=responses_out,
                parameters=op_params,
            )

        paths[path] = set(sorted(methods))

    return NormalizedOpenAPI(paths=paths, operations=operations)


def _parse_parameters(
    params_obj: Any, doc: Mapping[str, Any]
) -> dict[str, ParameterSpec]:
    """
    Parse a list of OpenAPI parameters (best-effort).
    Supports local $ref and in: query/path/header (MVP).
    Header names are treated as case-insensitive for identity (keying).
    Returns dict keyed by "in:name" where for headers name is lowercased.
    """
    out: dict[str, ParameterSpec] = {}
    if not isinstance(params_obj, list):
        return out

    for item in params_obj:
        param = item
        if isinstance(item, dict) and "$ref" in item:
            param = resolve_schema(item, doc)  # resolve local ref (best-effort)

        if not isinstance(param, dict):
            continue

        name = param.get("name")
        location = param.get("in")
        if not isinstance(name, str) or not isinstance(location, str):
            continue

        location = location.lower()
        if location not in _PARAM_IN_ALLOWED:
            continue

        required = bool(param.get("required", False))

        schema_dict = None
        schema = param.get("schema")
        if isinstance(schema, dict):
            schema_dict = resolve_schema(schema, doc)

        # IMPORTANT: header names are case-insensitive
        key_name = name.lower() if location == "header" else name
        key = f"{location}:{key_name}"

        # Preserve original 'name' for display in output paths/messages
        out[key] = ParameterSpec(
            name=name,
            location=location,
            required=required,
            schema=schema_dict,
        )

    return out
