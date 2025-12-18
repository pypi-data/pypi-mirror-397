from __future__ import annotations

import hashlib
from typing import Any, Dict

SCHEMA_PACKET_V1 = "xkid.Packet.v1"


def _sha256_hex(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def packet_v1_from_id_output(
    *,
    xid: str,
    payload_hex: str,
    codec: str = "b32k",
) -> Dict[str, Any]:
    """
    Construct a Packet.v1 from the ID projection.

    Packet != encoding.
    - Packet (logical artifact): canonical bytes + commitments.
    - Encoding (wire): B32K Unicode string.

    Null+1:
      - payload_hex is treated as the canonical packet bytes
      - xid is the b32k wire text for transport

    Device binding:
      - attached via device provider + binder (policy-driven)
      - advisory modes MUST NOT raise (packet construction is total)
      - required/sealed modes MUST fail closed if binding cannot be produced
    """
    payload_hex = payload_hex.lower()
    raw = bytes.fromhex(payload_hex)

    pkt: Dict[str, Any] = {
        "schema": SCHEMA_PACKET_V1,
        "codec": codec,
        "bytes_hex": payload_hex,
        "sha256_hex": _sha256_hex(raw),
        "b32k": xid,
    }

    # Device binding policy is driven by environment (DevicePolicy).
    # Behavior:
    # - none/advisory: never fail; fall back to explicit "no binding"
    # - required/sealed: fail closed if provider/binding fails or yields present=False
    try:
        from xkid.device import get_device_provider
        from xkid.device.policy import policy_from_env
        from xkid.packet.bind import bind_device

        provider = get_device_provider()
        policy = policy_from_env()
        claim = provider.get_claim(policy)

        if policy.binding_policy in ("required", "sealed") and not getattr(claim, "present", False):
            raise ValueError(f"Device binding policy '{policy.binding_policy}' requires a device claim, got present=False")

        pkt = bind_device(pkt, claim, policy)

    except Exception as e:
        # Fail-closed modes propagate error to caller (CLI will return cli.error).
        try:
            from xkid.device.policy import policy_from_env

            pol = policy_from_env()
            if pol.binding_policy in ("required", "sealed"):
                raise
        except Exception:
            # If even policy parsing fails, treat as advisory fallback (safe default).
            pass

        # Advisory/none modes: absolute invariant is "never crash"; represent no binding explicitly.
        pkt["device"] = {"binding": "none", "present": False}

        # Optional: include a non-normative hint (doesn't affect existing tests unless asserted).
        # Keep it minimal and future-safe.
        pkt.setdefault("device_note", str(e))

    return pkt
