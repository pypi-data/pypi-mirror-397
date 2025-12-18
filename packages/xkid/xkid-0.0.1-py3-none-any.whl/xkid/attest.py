from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    from importlib.metadata import PackageNotFoundError, version as pkg_version
except Exception:  # pragma: no cover
    PackageNotFoundError = Exception  # type: ignore
    pkg_version = None  # type: ignore

# We intentionally keep schemas simple and stable for sysop tooling.
SCHEMA_SYSOP_CHALLENGE_V1 = "xkid.SysopChallenge.v1"
SCHEMA_ATTESTATION_V1 = "xkid.Attestation.v1"
SCHEMA_SYSOP_VERIFY_V1 = "xkid.SysopVerify.v1"


def _b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    s2 = s.strip()
    pad = "=" * ((4 - (len(s2) % 4)) % 4)
    return base64.urlsafe_b64decode(s2 + pad)


def _canonical_json(obj: Any) -> bytes:
    # Stable serialization for signatures.
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _hmac_sha256(key: bytes, msg: bytes) -> bytes:
    return hmac.new(key, msg, hashlib.sha256).digest()


def _require_key() -> bytes:
    k = os.environ.get("XKID_ATTEST_KEY", "")
    if not k:
        raise ValueError(
            "Missing XKID_ATTEST_KEY. Set a shared secret for HMAC attestation "
            "(e.g. export XKID_ATTEST_KEY='...')."
        )
    return k.encode("utf-8")


def make_challenge(n_bytes: int = 32) -> Dict[str, Any]:
    nonce = secrets.token_bytes(n_bytes)
    return {
        "schema": SCHEMA_SYSOP_CHALLENGE_V1,
        "challenge": _b64url(nonce),
        "n_bytes": n_bytes,
    }


def _xkid_version() -> str:
    if pkg_version is None:
        return "unknown"
    try:
        return pkg_version("xkid")
    except PackageNotFoundError:
        return "unknown"
    except Exception:
        return "unknown"


@dataclass(frozen=True)
class AttestInputs:
    challenge: str
    packet_sha256_hex: str
    packet_codec: str
    packet_b32k: str
    device: Dict[str, Any]


def sign_attestation(inputs: AttestInputs, *, now: Optional[int] = None) -> Dict[str, Any]:
    """
    Sign an attestation over:
      - challenge (nonce)
      - packet commitment (sha256_hex)
      - codec + transport b32k
      - device binding object (policy-driven)
      - xkid version + epoch seconds

    This is NOT PKI. It's HMAC v1 (shared secret).
    """
    now_i = int(time.time()) if now is None else int(now)

    payload: Dict[str, Any] = {
        "schema": SCHEMA_ATTESTATION_V1,
        "challenge": inputs.challenge,
        "ts": now_i,
        "xkid_version": _xkid_version(),
        "packet": {
            "sha256_hex": inputs.packet_sha256_hex,
            "codec": inputs.packet_codec,
            "b32k": inputs.packet_b32k,
        },
        "device": inputs.device,
        "sig_alg": "hmac-sha256",
    }

    key = _require_key()
    sig = _hmac_sha256(key, _canonical_json(payload))
    payload["sig"] = _b64url(sig)
    return payload


def verify_attestation(att: Dict[str, Any], *, challenge: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify signature and (optionally) challenge binding.
    Returns a SysopVerify.v1 report, not a boolean.
    """
    if att.get("schema") != SCHEMA_ATTESTATION_V1:
        raise ValueError(f"Expected schema {SCHEMA_ATTESTATION_V1} (got {att.get('schema')!r})")

    sig_s = att.get("sig")
    if not isinstance(sig_s, str) or not sig_s:
        raise ValueError("Attestation missing 'sig'")

    if challenge is not None:
        if att.get("challenge") != challenge:
            return {
                "schema": SCHEMA_SYSOP_VERIFY_V1,
                "ok": False,
                "reason": "challenge_mismatch",
                "expected": challenge,
                "got": att.get("challenge"),
            }

    # Recompute signature over payload without 'sig'
    att2 = dict(att)
    att2.pop("sig", None)

    key = _require_key()
    expect = _hmac_sha256(key, _canonical_json(att2))
    got = _b64url_decode(sig_s)

    ok = hmac.compare_digest(expect, got)
    return {
        "schema": SCHEMA_SYSOP_VERIFY_V1,
        "ok": bool(ok),
        "reason": "ok" if ok else "bad_signature",
    }
