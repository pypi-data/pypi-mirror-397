from __future__ import annotations

import os

from xkid.device.provider_api import DeviceProvider
from xkid.device.providers.default import DefaultDeviceProvider
from xkid.device.providers.soft import SoftDeviceProvider


def get_device_provider() -> DeviceProvider:
    """
    Select a device provider.

    Semantics:
    - "self" is the canonical fallback: I think therefore I am.
      (Software-derived identity / A-mode by default.)
    - "default" is retained as a backward-compatible alias for "self".
    - Additional providers may be added over time (termux, hardware, sealed, ...).
    """
    name = os.environ.get("XKID_DEVICE_PROVIDER", "self").strip().lower()

    # Back-compat alias
    if name == "default":
        name = "self"

    if name == "self":
        return DefaultDeviceProvider()

    if name == "soft":
        return SoftDeviceProvider()

    raise RuntimeError(f"Unknown device provider: {name}")
