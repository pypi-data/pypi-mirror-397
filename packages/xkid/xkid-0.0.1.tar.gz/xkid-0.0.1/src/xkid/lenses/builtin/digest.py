from __future__ import annotations

from typing import Any, Dict
import json
import hashlib

from b32k.codec import load_b32k_alphabet, encode

from xkid.lenses.plugin_api import LensSpec


def run(params: Dict[str, Any]) -> Dict[str, Any]:
    text = params.get("text")
    hex_ = params.get("hex")

    # registry normalization should enforce exactly-one-of;
    # keep a final guard so plugins stay safe when used directly.
    if (text is None and hex_ is None) or (text is not None and hex_ is not None):
        raise ValueError("digest lens requires exactly one of: text, hex")

    if text is not None:
        payload = str(text).encode("utf-8")
        in_params = {"text": str(text)}
    else:
        payload = bytes.fromhex(str(hex_))
        in_params = {"hex": str(hex_)}

    symbols, index = load_b32k_alphabet()
    xid = encode(payload, symbols)

    out: Dict[str, Any] = {
        "schema": "xkid.LensOutput.v1",
        "lens": "digest",
        "params": in_params,
        "xid": xid,
        "payload_len": len(payload),
        "payload_sha256": hashlib.sha256(payload).hexdigest(),
        "xid_json": json.dumps(xid, ensure_ascii=False),
    }

    # Best-effort structural decode if available
    try:
        from xkid.id.v1 import _xid_struct  # type: ignore
        out["xid_struct"] = _xid_struct(xid, symbols, index)
    except Exception:
        pass

    return out


SPEC = LensSpec(
    name="digest",
    version="0.1.0",
    supports={"struct": True, "trace": False},
    compat={
        "deprecated": False,
        "replaced_by": None,
        "sunset_ts": None,
    },
    schema={
        "schema": "xkid.LensSchema.v1/digest",
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "hex": {"type": "string"},
        },
        "xkid_rules": {"exactly_one_of": ["text", "hex"]},
    },
    run=run,
)
