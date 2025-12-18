from typing import Any, Mapping


def resolve_schema(
    schema: Mapping[str, Any], doc: Mapping[str, Any], *, max_depth: int = 20
) -> dict[str, Any]:
    """
    Resolve local OpenAPI $ref for schema-like dicts (best-effort).

    Supported refs:
      - #/components/schemas/Name
      - #/components/parameters/Name   (useful when parsing operation/path parameters)

    Notes:
      - This returns a dict and does NOT preserve the original $ref.
      - It is intentionally conservative: local refs only.
    """
    return _resolve(schema, doc, depth=0, max_depth=max_depth)


def _resolve(
    schema: Any, doc: Mapping[str, Any], *, depth: int, max_depth: int
) -> dict[str, Any]:
    if depth > max_depth:
        return dict(schema) if isinstance(schema, dict) else {}

    if not isinstance(schema, dict):
        return {}

    ref = schema.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/components/"):
        target = _resolve_components_ref(ref, doc)
        if isinstance(target, dict):
            return _resolve(target, doc, depth=depth + 1, max_depth=max_depth)
        return {}

    # resolve nested structures we care about
    out = dict(schema)

    props = out.get("properties")
    if isinstance(props, dict):
        out["properties"] = {
            k: (
                _resolve(v, doc, depth=depth + 1, max_depth=max_depth)
                if isinstance(v, dict)
                else v
            )
            for k, v in props.items()
        }

    items = out.get("items")
    if isinstance(items, dict):
        out["items"] = _resolve(items, doc, depth=depth + 1, max_depth=max_depth)

    # composition (best-effort)
    for key in ("allOf", "oneOf", "anyOf"):
        val = out.get(key)
        if isinstance(val, list):
            out[key] = [
                (
                    _resolve(x, doc, depth=depth + 1, max_depth=max_depth)
                    if isinstance(x, dict)
                    else x
                )
                for x in val
            ]

    return out


def _resolve_components_ref(ref: str, doc: Mapping[str, Any]) -> Any:
    """
    Resolve a ref under #/components/*.

    Supported:
      - #/components/schemas/<Name>
      - #/components/parameters/<Name>
    """
    # Example: "#/components/parameters/XApiVersion"
    parts = ref.split("/")
    # ["#", "components", "<bucket>", "<Name>"]
    if len(parts) < 4:
        return None

    bucket = parts[2]
    name = parts[3]

    components = doc.get("components", {})
    if not isinstance(components, dict):
        return None

    if bucket == "schemas":
        schemas = components.get("schemas", {})
        if isinstance(schemas, dict):
            return schemas.get(name)
        return None

    if bucket == "parameters":
        params = components.get("parameters", {})
        if isinstance(params, dict):
            return params.get(name)
        return None

    return None
