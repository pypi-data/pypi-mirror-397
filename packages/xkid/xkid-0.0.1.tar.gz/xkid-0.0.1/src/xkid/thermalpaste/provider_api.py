from __future__ import annotations

from typing import Optional, Protocol

from xkid.thermalpaste.types import (
    Attestation,
    EnvironmentSnapshot,
    KeySpec,
    PublicKeyInfo,
    ThermalpasteClaimV1,
)


class ThermalpasteProvider(Protocol):
    provider_id: str

    def ensure_key(self, name: str, spec: KeySpec) -> str:
        """Ensure a named key exists; return provider KID/handle."""

    def get_public_key(self, kid: str) -> Optional[PublicKeyInfo]:
        """Return public key info if available."""

    def attest_key(self, kid: str, nonce_b64: str) -> Optional[Attestation]:
        """Return attestation evidence if supported, else None."""

    def snapshot_environment(self) -> EnvironmentSnapshot:
        """Return an environment snapshot (no secrets)."""

    def export_claim(self, kid: str, nonce_b64: str) -> ThermalpasteClaimV1:
        """Return a canonical ThermalpasteClaim.v1."""
