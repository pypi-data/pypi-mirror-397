from __future__ import annotations

import base64
import os
import platform
import time
from typing import Optional

from xkid.thermalpaste.types import (
    Attestation,
    EnvironmentSnapshot,
    KeySpec,
    PublicKeyInfo,
    ThermalpasteClaimV1,
)


class NullThermalpasteProvider:
    """
    Software-only provider.

    This is intentionally NOT hardware-backed. It exists to validate wiring and
    JSON outputs, and to act as a fallback where no platform binding exists.
    """

    provider_id = "null"

    def ensure_key(self, name: str, spec: KeySpec) -> str:
        # No real keystore; we just mint a handle. Private key mgmt is out of scope here.
        return f"null:{name}"

    def get_public_key(self, kid: str) -> Optional[PublicKeyInfo]:
        # Not available.
        return None

    def attest_key(self, kid: str, nonce_b64: str) -> Optional[Attestation]:
        return None

    def snapshot_environment(self) -> EnvironmentSnapshot:
        ts = int(time.time())
        boot = {"verified": False, "state": "unknown"}
        os_info = {"name": platform.system() or "unknown", "version": platform.version() or "unknown"}

        device = {
            "manufacturer": "unknown",
            "model": os.environ.get("TERMUX_DEVICE_MODEL", "unknown"),
            "hardware": platform.machine() or "unknown",
        }

        key_security = {
            "hardware_backed": False,
            "strongbox": False,
            "non_exportable": False,
            "user_auth": "none",
        }

        return EnvironmentSnapshot(ts_unix=ts, boot=boot, os=os_info, device=device, key_security=key_security)

    def export_claim(self, kid: str, nonce_b64: str) -> ThermalpasteClaimV1:
        env = self.snapshot_environment()
        # With null provider we must not claim hardware binding.
        binding = "external"

        return ThermalpasteClaimV1(
            version="thermalpaste.v1",
            provider=self.provider_id,
            present=True,
            binding=binding,
            kid=kid,
            environment=env,
            public_key=None,
            attestation=None,
        )
