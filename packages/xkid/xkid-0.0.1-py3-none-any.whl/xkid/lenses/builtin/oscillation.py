from __future__ import annotations

from typing import Any, Dict, Callable

from xkid.lenses.plugin_api import LensSpec


def _stub_oscillation(params: Dict[str, Any]) -> Dict[str, Any]:
    steps = int(params.get("steps", 8))
    dim = int(params.get("dim", 6))
    index = int(params.get("index", 0))
    component = int(params.get("component", 0))
    amplitude = float(params.get("amplitude", 1.0))
    eta = float(params.get("eta", 0.1))

    xid = (
        f"XID:oscillation:"
        f"dim={dim}:steps={steps}:index={index}:"
        f"component={component}:amplitude={amplitude}:eta={eta}"
    )

    return {
        "schema": "xkid.LensOutput.v1",
        "xid": xid,
        "lens": "oscillation",
        "params": dict(params),
        "warnings": ["stub lens (not wired to xkid.id.v1)"],
    }


def _real_oscillation(params: Dict[str, Any]) -> Dict[str, Any]:
    from xkid.id.v1 import id_v1_oscillation

    out = id_v1_oscillation(dict(params))
    if not isinstance(out, dict) or "xid" not in out:
        raise RuntimeError("id_v1_oscillation did not return dict with 'xid'")

    normalized: Dict[str, Any] = {
        "schema": "xkid.LensOutput.v1",
        "xid": out["xid"],
        "lens": out.get("lens", "oscillation"),
        "params": out.get("params", dict(params)),
    }

    for k in ("trace_len", "xid_json", "xid_struct", "trace"):
        if k in out:
            normalized[k] = out[k]

    return normalized


def _pick_runner() -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    try:
        from xkid.id.v1 import id_v1_oscillation  # noqa: F401
        return _real_oscillation
    except Exception:
        return _stub_oscillation


SPEC = LensSpec(
    name="oscillation",
    version="0.1.0",
    supports={"struct": True, "trace": True},
    compat={
        "deprecated": False,
        "replaced_by": None,
        "sunset_ts": None,
    },
    schema={
        "schema": "xkid.LensSchema.v1/oscillation",
        "type": "object",
        "properties": {
            "dim": {"type": "integer", "default": 6, "minimum": 1},
            "eta": {"type": "number", "default": 0.1},
            "steps": {"type": "integer", "default": 8, "minimum": 1},
            "index": {"type": "integer", "default": 0, "minimum": 0},
            "component": {"type": "integer", "default": 0, "minimum": 0},
            "amplitude": {"type": "number", "default": 1.0},
        },
    },
    run=_pick_runner(),
)
