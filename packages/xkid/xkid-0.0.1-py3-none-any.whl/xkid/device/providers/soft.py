from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass

from xkid.device.provider_api import DeviceClaim, DevicePolicy, DeviceProvider


def _stable_kid_for_device_id(device_id: str) -> str:
    # Stable, deterministic (A-mode). No secrets required.
    h = hashlib.sha256(device_id.encode("utf-8")).hexdigest()
    return f"soft-inst-{h[:32]}"


@dataclass(frozen=True)
class SoftDeviceProvider(DeviceProvider):
    name: str = "soft"

    def get_claim(self, policy: DevicePolicy) -> DeviceClaim:
        # If caller disables device binding entirely
        if policy.binding_policy == "none":
            return DeviceClaim(
                present=False,
                binding="none",
                device_id=None,
                kid=None,
                metadata={"provider": self.name},
            )

        device_id = os.getenv("XKID_DEVICE_ID") or ""
        device_id = device_id.strip()

        if not device_id:
            # No env-provided device id => no claim
            return DeviceClaim(
                present=False,
                binding="none",
                device_id=None,
                kid=None,
                metadata={"provider": self.name, "reason": "missing_XKID_DEVICE_ID"},
            )

        # If external bindings are disallowed, we must refuse (policy)
        if not policy.allow_external:
            return DeviceClaim(
                present=False,
                binding="none",
                device_id=None,
                kid=None,
                metadata={"provider": self.name, "reason": "external_disallowed"},
            )

        kid = _stable_kid_for_device_id(device_id)

        return DeviceClaim(
            present=True,
            binding="external",
            device_id=device_id,
            kid=kid,
            metadata={"provider": self.name, "mode": "A"},
        )
