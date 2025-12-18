from __future__ import annotations

import hashlib
import os
import sys

try:
    from importlib.metadata import PackageNotFoundError, version as pkg_version
except Exception:  # pragma: no cover
    PackageNotFoundError = Exception  # type: ignore
    pkg_version = None  # type: ignore

from xkid.device.provider_api import DevicePolicy, DeviceClaim


def _xkid_version() -> str:
    if pkg_version is None:
        return "unknown"
    try:
        return pkg_version("xkid")
    except PackageNotFoundError:
        return "unknown"
    except Exception:
        return "unknown"


def _xkid_instance_id() -> str:
    """
    A: Derive a stable software instance id from the running xkid installation.

    This is NOT sealed / not hardware-backed. It is a deterministic identifier for:
      "this xkid install, in this python, on this platform/user context".
    """
    try:
        import xkid as xkid_pkg  # local package instance
        xkid_path = getattr(xkid_pkg, "__file__", "") or ""
    except Exception:
        xkid_path = ""

    parts = [
        "xkid-inst-v1",
        _xkid_version(),
        sys.executable,
        xkid_path,
        os.name,
        sys.platform,
        os.environ.get("HOME", ""),
        str(os.getuid()) if hasattr(os, "getuid") else "",
        str(os.getgid()) if hasattr(os, "getgid") else "",
    ]
    blob = "|".join(parts).encode("utf-8", errors="ignore")
    h = hashlib.sha256(blob).hexdigest()[:32]
    return f"soft-inst-{h}"


class DefaultDeviceProvider:
    """
    Best-effort, non-sealed provider.
    Safe for OSS, CI, containers, Termux.

    A-mode only: derives device_id from the xkid package instance.
    """

    name = "default"

    def get_claim(self, policy: DevicePolicy) -> DeviceClaim:
        # Explicitly disabled -> no binding.
        if policy.binding_policy == "none":
            return DeviceClaim(
                present=False,
                binding="none",
                kid=None,
                device_id=None,
                metadata={"provider": self.name, "grade": policy.min_grade},
            )

        # External binding only if allowed by policy.
        if not policy.allow_external:
            return DeviceClaim(
                present=False,
                binding="none",
                kid=None,
                device_id=None,
                metadata={"provider": self.name, "grade": policy.min_grade},
            )

        device_id = _xkid_instance_id()
        kid = device_id  # canonical mapping

        return DeviceClaim(
            present=True,
            binding="external",
            kid=kid,
            device_id=device_id,
            metadata={
                "provider": self.name,
                "grade": policy.min_grade,
                "binding_policy": policy.binding_policy,
            },
        )
