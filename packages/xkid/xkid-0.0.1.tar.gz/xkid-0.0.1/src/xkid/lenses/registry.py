from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List


# ---------------------------------------------------------------------
# Contract hashing
# ---------------------------------------------------------------------

def _contract_hash(d: Dict[str, Any]) -> str:
    """
    Stable hash of the lens contract (excluding runtime fields).
    Used by versioning tests.
    """
    frozen = {
        "name": d["name"],
        "version": d["version"],
        "supports": d["supports"],
        "schema": d["schema"],
    }
    raw = json.dumps(
        frozen,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------------
# Param schema application
# ---------------------------------------------------------------------

def _apply_param_schema(
    schema: Dict[str, Any],
    params: Dict[str, Any],
) -> Dict[str, Any]:
    props = schema.get("properties", {})
    out: Dict[str, Any] = {}

    # Reject unknown params
    for k in params:
        if k not in props:
            raise ValueError(f"Unknown parameter: {k}")

    # Apply defaults + cast
    for name, spec in props.items():
        if name in params:
            val = params[name]
        elif "default" in spec:
            val = spec["default"]
        else:
            continue

        t = spec.get("type")
        try:
            if t == "integer":
                val = int(val)
            elif t == "number":
                val = float(val)
            elif t == "string":
                val = str(val)
        except Exception as e:
            raise ValueError(
                f"Invalid type for parameter '{name}'"
            ) from e

        out[name] = val

    return out


# ---------------------------------------------------------------------
# Lens runners
# ---------------------------------------------------------------------

def _real_oscillation(params: Dict[str, Any]) -> Dict[str, Any]:
    from xkid.id.v1 import id_v1_oscillation

    out = id_v1_oscillation(dict(params))
    return {
        "schema": "xkid.LensOutput.v1",
        "lens": "oscillation",
        "xid": out["xid"],
        "params": out["params"],
        "trace_len": out.get("trace_len"),
        "xid_struct": out.get("xid_struct"),
    }


def _digest(params: Dict[str, Any]) -> Dict[str, Any]:
    text = params.get("text")
    hexval = params.get("hex")

    if (text is None) == (hexval is None):
        raise ValueError(
            "digest lens requires exactly one of: text, hex"
        )

    if text is not None:
        payload = text.encode("utf-8")
    else:
        payload = bytes.fromhex(hexval)

    h = hashlib.sha256(payload).hexdigest()

    return {
        "schema": "xkid.LensOutput.v1",
        "lens": "digest",
        "xid": f"sha256:{h}",
        "params": params,
    }


def _spirelica(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Spirelica lens (v1): currently backed by the entrogravity ID_V1 generator.
    """
    from xkid.id.v1 import id_v1_entrogravity_spherical

    out = id_v1_entrogravity_spherical(dict(params))
    return {
        "schema": "xkid.LensOutput.v1",
        "lens": "spirelica",
        "xid": out["xid"],
        "params": out["params"],
        "trace_len": out.get("trace_len"),
        "xid_struct": out.get("xid_struct"),
    }


# ---------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------

_LENSES: Dict[str, Dict[str, Any]] = {
    "oscillation": {
        "name": "oscillation",
        "version": "0.1.0",
        "supports": {"struct": True, "trace": True},
        "schema": {
            "schema": "xkid.LensSchema.v1/oscillation",
            "type": "object",
            "properties": {
                "dim": {"type": "integer", "default": 6},
                "eta": {"type": "number", "default": 0.1},
                "steps": {"type": "integer", "default": 8},
                "index": {"type": "integer", "default": 3},
                "component": {"type": "integer", "default": 0},
                "amplitude": {"type": "number", "default": 1.0},
            },
        },
        "run": _real_oscillation,
    },
    "digest": {
        "name": "digest",
        "version": "0.6.0",
        "supports": {"struct": True, "trace": False},
        "schema": {
            "schema": "xkid.LensSchema.v1/digest",
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "hex": {"type": "string"},
            },
            "oneOf": [
                {"required": ["text"]},
                {"required": ["hex"]},
            ],
        },
        "run": _digest,
    },
    "spirelica": {
        "name": "spirelica",
        "version": "0.1.0",
        "supports": {"struct": True, "trace": True},
        "schema": {
            "schema": "xkid.LensSchema.v1/spirelica",
            "type": "object",
            "properties": {
                "q": {"type": "number", "default": 1e-6},
                "D0": {"type": "number", "default": 1.0},
                "xmin": {"type": "number", "default": 10.0},
                "xmax": {"type": "number", "default": 1e5},
                "steps": {"type": "integer", "default": 200},
            },
        },
        "run": _spirelica,
    },
}


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------

def lens_list() -> List[Dict[str, Any]]:
    return [
        {
            "name": d["name"],
            "version": d["version"],
            "supports": d["supports"],
        }
        for d in sorted(_LENSES.values(), key=lambda x: x["name"])
    ]


def lens_describe(name: str) -> Dict[str, Any]:
    if name not in _LENSES:
        raise KeyError(f"Unknown lens: {name}")

    d = _LENSES[name]
    return {
        "schema": "xkid.LensDescribe.v1",
        "name": d["name"],
        "version": d["version"],
        "supports": d["supports"],
        "param_schema": d["schema"],
        "compat": {
            "deprecated": False,
            "replaced_by": None,
            "sunset_ts": None,
            "contract_sha256": _contract_hash(d),
        },
    }


def lens_run(
    name: str,
    params: Dict[str, Any],
    *,
    want: Dict[str, bool] | None = None,
    need_trace: bool = False,
    need_struct: bool = False,
) -> Dict[str, Any]:
    if want is not None:
        need_struct = bool(want.get("struct", need_struct))
        need_trace = bool(want.get("trace", need_trace))

    if name not in _LENSES:
        raise KeyError(f"Unknown lens: {name}")

    d = _LENSES[name]
    supports = d["supports"]

    if need_trace and not supports.get("trace", False):
        raise ValueError(
            f"Lens '{name}' does not support required capability: trace"
        )

    if need_struct and not supports.get("struct", False):
        raise ValueError(
            f"Lens '{name}' does not support required capability: struct"
        )

    clean_params = _apply_param_schema(d["schema"], params)
    return d["run"](clean_params)
