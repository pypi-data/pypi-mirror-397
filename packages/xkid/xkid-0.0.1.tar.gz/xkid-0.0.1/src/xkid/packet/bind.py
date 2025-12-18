from __future__ import annotations

from typing import Any, Dict


def bind_device(
    pkt: Dict[str, Any],
    claim: Any,
    policy: Any,
) -> Dict[str, Any]:
    """
    Bind a device claim into a packet.

    Contract:
    - If claim.present is False:
        device = { "binding": "none", "present": False }
    - If claim.present is True:
        device MUST include:
          - binding
          - present
          - kid   (derived from claim.device_id)
    """

    present = bool(getattr(claim, "present", False))

    if not present:
        pkt["device"] = {
            "binding": "none",
            "present": False,
        }
        return pkt

    binding = getattr(claim, "binding", None)
    device_id = getattr(claim, "device_id", None)

    if not binding:
        raise ValueError("Device claim present=True but missing binding")

    if not device_id:
        raise ValueError("Device claim present=True but missing device_id")

    # 🔑 Canonical mapping: device_id → kid
    pkt["device"] = {
        "binding": binding,
        "present": True,
        "kid": device_id,
    }

    # Optional passthrough metadata (future-safe)
    metadata = getattr(claim, "metadata", None)
    if isinstance(metadata, dict):
        pkt["device"]["metadata"] = metadata

    return pkt
