from __future__ import annotations

import os
from typing import Optional

from xkid.device.provider_api import DeviceProvider
from xkid.device.providers.default import DefaultDeviceProvider


# Singleton cache (provider selection should be stable per process)
_PROVIDER: Optional[DeviceProvider] = None


def get_device_provider() -> DeviceProvider:
    """
    Resolve the active DeviceProvider.

    Resolution order (B with fallback to A):
      B) Explicit provider via env: XKID_DEVICE_PROVIDER
      A) Default OSS-safe provider

    This function MUST NEVER raise.
    """
    global _PROVIDER
    if _PROVIDER is not None:
        return _PROVIDER

    name = os.environ.get("XKID_DEVICE_PROVIDER", "").strip().lower()

    # --- B: explicit provider selection ---
    if name in ("default", ""):
        _PROVIDER = DefaultDeviceProvider()
        return _PROVIDER

    # --- A: fallback (absolute safety) ---
    # Future providers (hardware, sealed, TPM, enclave) plug in here
    _PROVIDER = DefaultDeviceProvider()
    return _PROVIDER
