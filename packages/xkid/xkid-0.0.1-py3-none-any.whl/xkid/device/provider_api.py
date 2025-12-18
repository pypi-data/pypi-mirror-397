from __future__ import annotations

"""
Device provider contract (v1)

Key idea:
- `binding_policy` is *what the caller wants* (policy).
- `binding` is *what the provider actually delivered* (claim).

Important semantics:
- binding="external" may be a software-derived identifier (A-mode). It is NOT
  hardware-backed and NOT sealed unless explicitly stated by the provider.
- binding="hardware" implies a hardware root-of-trust was used to derive or
  attest the identity (future provider).
- binding="sealed" implies the identity is cryptographically sealed to hardware
  (e.g. TPM/TEE/SE) and is not forgeable by software alone (future provider).
"""

from dataclasses import dataclass
from typing import Dict, Optional, Protocol


@dataclass(frozen=True)
class DevicePolicy:
    # Caller intent:
    # - none: disable device binding entirely
    # - advisory: include device binding if available (best-effort)
    # - required: device binding must be present (caller may reject "none")
    # - sealed: device binding must be sealed (caller may reject non-sealed)
    binding_policy: str = "advisory"  # none|advisory|required|sealed

    # Minimum assurance / deployment tier requested by caller.
    min_grade: str = "dev"  # dev|commercial|high_assurance

    # Whether non-hardware ("external") bindings are allowed (e.g. A-mode).
    allow_external: bool = True

    # If True, provider should only return identities rooted in hardware.
    # (i.e., binding should be "hardware" or "sealed" when present=True)
    require_hardware_root: bool = False


@dataclass(frozen=True)
class DeviceClaim:
    # Whether a device identity is present.
    present: bool

    # What was actually delivered:
    # - none: no device identity included
    # - external: non-sealed identity (may be software-derived; A-mode)
    # - hardware: identity derived/attested via hardware root-of-trust
    # - sealed: identity cryptographically sealed to hardware (strongest)
    binding: str  # none|external|hardware|sealed

    # Provider-specific stable identifier for the device (if present).
    device_id: Optional[str]

    # Stable key identifier for the device identity.
    # Contract: REQUIRED when present=True; MUST be stable across runs for the
    # same device identity.
    kid: Optional[str]

    # Future-safe provider metadata (strings only).
    metadata: Dict[str, str]


class DeviceProvider(Protocol):
    name: str

    def get_claim(self, policy: DevicePolicy) -> DeviceClaim:
        ...
