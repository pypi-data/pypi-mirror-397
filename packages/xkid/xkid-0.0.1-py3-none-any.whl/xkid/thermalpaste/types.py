from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional


Binding = Literal["none", "external", "hardware", "sealed"]
UserAuth = Literal["none", "device", "biometric", "biometric_or_device"]
AttestationFormat = Literal["x509-chain", "cose", "jwt", "opaque"]


@dataclass(frozen=True)
class KeySpec:
    kty: str                      # "EC" | "RSA" | "OKP"
    alg: str                      # "ES256" | "RS256" | "Ed25519" | ...
    purpose: List[str]            # ["sign", "verify"]
    user_auth: UserAuth = "none"
    require_hardware: bool = True
    require_non_exportable: bool = True
    require_sealed: bool = False


@dataclass(frozen=True)
class PublicKeyInfo:
    kty: str
    alg: str
    der_b64: str                  # SPKI DER (base64)


@dataclass(frozen=True)
class Attestation:
    format: AttestationFormat
    evidence_b64: Optional[str] = None
    cert_chain_b64: Optional[List[str]] = None
    claims: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class EnvironmentSnapshot:
    ts_unix: int
    boot: Dict[str, Any]
    os: Dict[str, Any]
    device: Optional[Dict[str, Any]] = None
    key_security: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class ThermalpasteClaimV1:
    version: str                  # must be "thermalpaste.v1"
    provider: str
    present: bool
    binding: Binding
    kid: str
    environment: EnvironmentSnapshot
    public_key: Optional[PublicKeyInfo] = None
    attestation: Optional[Attestation] = None

    def to_json(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "version": self.version,
            "provider": self.provider,
            "present": self.present,
            "binding": self.binding,
            "kid": self.kid,
            "environment": {
                "ts_unix": self.environment.ts_unix,
                "boot": self.environment.boot,
                "os": self.environment.os,
            },
        }
        if self.environment.device is not None:
            out["environment"]["device"] = self.environment.device
        if self.environment.key_security is not None:
            out["environment"]["key_security"] = self.environment.key_security

        if self.public_key is not None:
            out["public_key"] = {
                "kty": self.public_key.kty,
                "alg": self.public_key.alg,
                "der_b64": self.public_key.der_b64,
            }
        if self.attestation is not None:
            a: Dict[str, Any] = {"format": self.attestation.format}
            if self.attestation.evidence_b64 is not None:
                a["evidence_b64"] = self.attestation.evidence_b64
            if self.attestation.cert_chain_b64 is not None:
                a["cert_chain_b64"] = self.attestation.cert_chain_b64
            if self.attestation.claims is not None:
                a["claims"] = self.attestation.claims
            out["attestation"] = a
        return out
