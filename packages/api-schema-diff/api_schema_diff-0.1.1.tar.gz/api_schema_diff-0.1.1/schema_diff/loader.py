import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping


class SchemaKind(str, Enum):
    OPENAPI = "openapi"
    JSON_SCHEMA = "json_schema"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class LoadedSchema:
    kind: SchemaKind
    raw: dict[str, Any]
    source: Path


def load_schema(path: Path) -> LoadedSchema:
    """
    Load a schema file from disk (JSON always, YAML optionally) and detect its kind.

    Supported inputs:
      - JSON (.json)
      - YAML (.yml/.yaml) if PyYAML is installed

    Returns:
      LoadedSchema(kind=..., raw=..., source=path)
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")

    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")

    if suffix in {".yml", ".yaml"}:
        raw = _load_yaml(text, path)
    else:
        # default to JSON (even if no extension, JSON is a reasonable default)
        raw = _load_json(text, path)

    if not isinstance(raw, dict):
        raise ValueError(f"Top-level schema must be an object/dict in {path}")

    kind = detect_schema_kind(raw)
    return LoadedSchema(kind=kind, raw=raw, source=path)


def _load_json(text: str, path: Path) -> dict[str, Any]:
    try:
        obj = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e

    if not isinstance(obj, dict):
        raise ValueError(f"Top-level JSON must be an object/dict in {path}")

    return obj


def _load_yaml(text: str, path: Path) -> dict[str, Any]:
    """
    YAML support is optional to keep MVP lightweight.
    Install with: pip install pyyaml
    """
    try:
        import yaml  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "YAML schema detected but PyYAML is not installed. "
            "Install it with: pip install pyyaml"
        ) from e

    try:
        obj = yaml.safe_load(text)
    except Exception as e:
        raise ValueError(f"Invalid YAML in {path}: {e}") from e

    if not isinstance(obj, dict):
        raise ValueError(f"Top-level YAML must be an object/dict in {path}")

    return obj


def detect_schema_kind(raw: Mapping[str, Any]) -> SchemaKind:
    """
    Detect whether `raw` looks like:
      - OpenAPI 3.x document
      - JSON Schema document
    """
    # OpenAPI 3.x typically has keys: "openapi" and "paths"
    if "openapi" in raw and "paths" in raw:
        return SchemaKind.OPENAPI

    # JSON Schema typically has $schema and/or type/properties
    if "$schema" in raw:
        return SchemaKind.JSON_SCHEMA

    # Heuristic: JSON Schema often has these keys at top-level
    json_schema_markers = {
        "type",
        "properties",
        "required",
        "allOf",
        "oneOf",
        "anyOf",
        "$defs",
        "definitions",
    }
    if any(k in raw for k in json_schema_markers):
        return SchemaKind.JSON_SCHEMA

    return SchemaKind.UNKNOWN
