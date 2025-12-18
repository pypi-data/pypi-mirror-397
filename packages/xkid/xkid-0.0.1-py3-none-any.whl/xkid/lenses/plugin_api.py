from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional


LensRunner = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass(frozen=True)
class LensSpec:
    """
    Minimal stable interface between registry and lens modules.

    - name/version/supports/compat/schema are metadata frozen by goldens + contract hash
    - run is the callable
    """
    name: str
    version: str
    supports: Mapping[str, Any]
    schema: Mapping[str, Any]
    run: LensRunner
    compat: Optional[Mapping[str, Any]] = None


def as_dict(spec: LensSpec) -> Dict[str, Any]:
    return {
        "name": spec.name,
        "version": spec.version,
        "supports": dict(spec.supports),
        "schema": dict(spec.schema),
        "compat": dict(spec.compat or {}),
        "run": spec.run,
    }


def validate_spec(spec: LensSpec) -> None:
    if not spec.name or not isinstance(spec.name, str):
        raise ValueError("LensSpec.name must be non-empty string")
    if not spec.version or not isinstance(spec.version, str):
        raise ValueError("LensSpec.version must be non-empty string")

    if not isinstance(spec.supports, Mapping):
        raise ValueError(f"{spec.name}: supports must be a mapping")
    if not isinstance(spec.schema, Mapping):
        raise ValueError(f"{spec.name}: schema must be a mapping")

    # Required schema identity string
    schema_id = spec.schema.get("schema")
    if not isinstance(schema_id, str) or not schema_id:
        raise ValueError(f"{spec.name}: schema must contain non-empty 'schema' string")

    # run must be callable
    if not callable(spec.run):
        raise ValueError(f"{spec.name}: run must be callable")

    # compat is optional but if present must be a mapping
    if spec.compat is not None and not isinstance(spec.compat, Mapping):
        raise ValueError(f"{spec.name}: compat must be a mapping if provided")
