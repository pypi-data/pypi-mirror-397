from __future__ import annotations

import os

from xkid.device.provider_api import DevicePolicy


def _env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    v2 = v.strip().lower()
    if v2 in ("1", "true", "yes", "y", "on"):
        return True
    if v2 in ("0", "false", "no", "n", "off"):
        return False
    return default


def policy_from_env() -> DevicePolicy:
    """
    Build DevicePolicy from environment variables.

    Supported:
      - XKID_DEVICE_BINDING: none|advisory|required|sealed
      - XKID_DEVICE_GRADE: dev|commercial|high_assurance
      - XKID_DEVICE_ALLOW_EXTERNAL: bool
      - XKID_DEVICE_REQUIRE_HW_ROOT: bool

    Default behavior (critical):
      - If XKID_DEVICE_BINDING is NOT set, binding_policy defaults to "none"
        so goldens remain device-neutral unless explicitly enabled.
    """
    raw = os.environ.get("XKID_DEVICE_BINDING")
    if raw is None:
        binding_policy = "none"
    else:
        binding_policy = raw.strip().lower()
        if binding_policy not in ("none", "advisory", "required", "sealed"):
            binding_policy = "advisory"

    min_grade = os.environ.get("XKID_DEVICE_GRADE", "dev").strip().lower()
    if min_grade not in ("dev", "commercial", "high_assurance"):
        min_grade = "dev"

    allow_external = _env_bool("XKID_DEVICE_ALLOW_EXTERNAL", True)
    require_hardware_root = _env_bool("XKID_DEVICE_REQUIRE_HW_ROOT", False)

    return DevicePolicy(
        binding_policy=binding_policy,
        min_grade=min_grade,
        allow_external=allow_external,
        require_hardware_root=require_hardware_root,
    )
