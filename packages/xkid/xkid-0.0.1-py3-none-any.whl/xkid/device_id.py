from __future__ import annotations

import base64
import hashlib
import json
import os
from typing import Any, Dict, Optional


def _sha256(data: bytes) -> bytes:
    h = hashlib.sha256()
    h.update(data)
    return h.digest()


def _sha256_hex(data: bytes) -> str:
    return _sha256(data).hex()


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _load_external_json() -> Optional[Dict[str, Any]]:
    """
    External (app/keystore) path: provide a complete device block as JSON.

    Env:
      - XKID_DEVICE_EXTERNAL_JSON: JSON string of the device block
        (must include at least id/kid/binding, and optionally sig_b64/attestation)
    """
    s = os.environ.get("XKID_DEVICE_EXTERNAL_JSON")
    if not s:
        return None
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj
    except Exception:
        return None
    return None


def _load_attestation_json() -> Optional[Dict[str, Any]]:
    s = os.environ.get("XKID_DEVICE_ATTESTATION_JSON")
    if not s:
        return None
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj
    except Exception:
        return None
    return None


def _ed25519_available() -> bool:
    try:
        import cryptography  # noqa: F401
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey  # noqa: F401
        return True
    except Exception:
        return False


def _ed25519_key_from_seed(seed32: bytes):
    """
    Deterministic key from 32-byte seed, used for tests/CI and Termux dev.
    """
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    return Ed25519PrivateKey.from_private_bytes(seed32)


def _seed_from_env() -> Optional[bytes]:
    """
    Env:
      - XKID_DEVICE_KEY_SEED_HEX: 64 hex chars (32 bytes)
    """
    s = os.environ.get("XKID_DEVICE_KEY_SEED_HEX")
    if not s:
        return None
    s = s.strip().lower()
    try:
        b = bytes.fromhex(s)
    except Exception:
        return None
    return b if len(b) == 32 else None


def device_block_for_packet(packet_bytes: bytes) -> Dict[str, Any]:
    """
    Produce the `device` block to embed in Packet.v1.

    Precedence:
      1) External JSON (app/keystore) if provided.
      2) Deterministic Ed25519 signature if cryptography is available and seed is set.
      3) Otherwise, return binding='none' with present=False.

    The signature covers the canonical packet bytes (packet_bytes), NOT the B32K text.
    """
    ext = _load_external_json()
    if ext is not None:
        # Allow external signer to optionally include attestation as well.
        # If attestation is provided separately, merge it in.
        att = _load_attestation_json()
        if att is not None and "attestation" not in ext:
            ext = dict(ext)
            ext["attestation"] = att
        return ext

    # Termux/dev path: deterministic seed-based key (tests/CI should set seed)
    if _ed25519_available():
        seed = _seed_from_env()
        if seed is not None:
            sk = _ed25519_key_from_seed(seed)
            pk = sk.public_key()
            pk_bytes = pk.public_bytes_raw()

            kid_hex = _sha256_hex(pk_bytes)
            kid = f"sha256:{kid_hex}"
            did = f"did:xkid:sha256:{kid_hex}"

            sig = sk.sign(packet_bytes)
            d: Dict[str, Any] = {
                "present": True,
                "binding": "sig",
                "kid": kid,
                "id": did,
                "sig_b64": _b64(sig),
            }

            att = _load_attestation_json()
            if att is not None:
                d["attestation"] = att

            return d

    # Fallback: cannot sign / no key material available
    return {
        "present": False,
        "binding": "none",
    }
