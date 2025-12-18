from __future__ import annotations

import hashlib
import os
import platform
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, Tuple


def _read_text(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def _sha256_hex(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def _normalize_mac(s: str) -> Optional[str]:
    s = (s or "").strip().lower()
    if len(s) < 17 or ":" not in s:
        return None
    parts = s.split(":")
    if len(parts) != 6:
        return None
    try:
        _ = [int(p, 16) for p in parts]
    except Exception:
        return None
    return ":".join(f"{int(p,16):02x}" for p in parts)


def best_effort_mac() -> Tuple[Optional[str], Optional[str]]:
    """
    Best-effort MAC lookup for Linux/Android.

    Notes:
    - On modern Android, real MAC may be unavailable or randomized.
    - This function must never be relied on for security.
    """
    candidates = ["wlan0", "eth0", "wifi0", "rmnet0"]
    for ifname in candidates:
        mac = _read_text(f"/sys/class/net/{ifname}/address")
        mac_n = _normalize_mac(mac or "")
        if mac_n:
            return mac_n, ifname
    return None, None


def device_hints() -> Dict[str, Any]:
    """
    Non-authoritative hardware/runtime hints safe to include in packets.

    Default behavior:
      - Emits mac_sha256 (salted if XKID_DEVICE_SALT is set) when readable
      - Does NOT emit raw mac unless XKID_EMIT_RAW_MAC=1
      - Adds platform string as a weak environment hint

    Env:
      - XKID_DEVICE_SALT: optional salt used for hashing stable identifiers
      - XKID_EMIT_RAW_MAC: set to "1" to include raw MAC (not recommended)
    """
    salt = os.environ.get("XKID_DEVICE_SALT", "")
    raw_allowed = os.environ.get("XKID_EMIT_RAW_MAC", "") == "1"

    mac, ifname = best_effort_mac()
    hints: Dict[str, Any] = {
        "present": False,
        "platform": platform.platform(),
    }

    if mac:
        hints["present"] = True
        hints["ifname"] = ifname

        # Prefer hashed MAC (salted) to avoid turning packets into tracking beacons.
        hints["mac_sha256"] = _sha256_hex((salt + mac).encode("utf-8"))

        if raw_allowed:
            hints["mac"] = mac

    return hints


# -----------------------------------------------------------------------------
# Provider contract + selection
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class DevicePolicy:
    """
    Policy is the caller's intent; providers may ignore fields they don't support.

    binding:
      - "advisory": safe default for CI/Termux; do not claim strong identity
      - "external": expect external system to provide a device KID (explicit env)
      - "metal": reserved for future "full metal" / hardware-rooted binding
    """

    binding: str = "advisory"


class DeviceProvider(Protocol):
    def get_claim(self, policy: DevicePolicy) -> Dict[str, Any]:
        """
        Return a device claim dict (not yet bound into a packet).

        Expected minimal shape (binder will enforce final schema):
          - present: bool
          - binding: str
        Optional:
          - kid: str (stable identifier; e.g. "sha256:deadbeef")
          - hints: dict (non-authoritative environment hints)
        """
        ...


class DevDeviceProvider:
    """
    Safe default provider.

    - Never asserts a strong identity.
    - May provide weak hints (hashed MAC) but does not treat them as binding.
    """

    def get_claim(self, policy: DevicePolicy) -> Dict[str, Any]:
        # In advisory mode, do not claim presence as an identity binding.
        # Hints are still useful for debugging / observability.
        hints = device_hints()
        return {
            "binding": "none",
            "present": False,
            "hints": hints,
        }


class ExternalDeviceProvider:
    """
    External provider passthrough.

    Enabled explicitly via env:
      - XKID_DEVICE_EXTERNAL=1

    Data:
      - XKID_DEVICE_KID (required for present=True)
        Example: "sha256:deadbeef"
    """

    def get_claim(self, policy: DevicePolicy) -> Dict[str, Any]:
        kid = (os.environ.get("XKID_DEVICE_KID") or "").strip()
        if not kid:
            # External requested but no KID provided -> treat as not present.
            return {
                "binding": "none",
                "present": False,
            }
        return {
            "binding": "external",
            "present": True,
            "kid": kid,
        }


def get_device_provider() -> DeviceProvider:
    """
    Select device provider.

    Priority:
      1) External provider (explicitly requested)
      2) Dev provider (safe fallback)
    """
    if os.environ.get("XKID_DEVICE_EXTERNAL") == "1":
        return ExternalDeviceProvider()
    return DevDeviceProvider()
