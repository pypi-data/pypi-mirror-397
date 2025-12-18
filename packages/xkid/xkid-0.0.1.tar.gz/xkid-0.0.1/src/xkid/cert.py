from __future__ import annotations
from typing import Any, Dict
import time

from .canon import canon_json_bytes
from .hashing import hash_obj
from .keys import sign_detached, verify_detached


def now_utc() -> int:
    return int(time.time())


def issue_cert(
    *,
    issuer_id: str,
    issuer_public_b64u: str,
    issuer_secret_b64u: str,
    claim: Dict[str, Any],
    expires_at_utc: int = 0,
) -> Dict[str, Any]:
    """
    Issue an XKID certificate (AID) over a signed claim.
    """
    unsigned = {
        "cert_version": 1,
        "issuer": {
            "issuer_id": issuer_id,
            "pub": issuer_public_b64u,
        },
        "claim_hash": claim["claim_hash"],
        "token_hash": claim["token_hash"],
        "issued_at_utc": now_utc(),
        "expires_at_utc": int(expires_at_utc),
        "claim": claim,
    }

    unsigned["certificate_hash"] = hash_obj(unsigned)

    msg = canon_json_bytes(unsigned)
    sig = sign_detached(issuer_secret_b64u, msg)

    cert = dict(unsigned)
    cert["signature"] = {"algo": "ed25519", "value": sig}
    return cert


def verify_cert_signature(cert: Dict[str, Any]) -> bool:
    sig = cert.get("signature", {}).get("value", "")
    issuer_pub = cert.get("issuer", {}).get("pub", "")
    if not sig or not issuer_pub:
        return False

    unsigned = dict(cert)
    unsigned.pop("signature", None)

    msg = canon_json_bytes(unsigned)
    return verify_detached(issuer_pub, msg, sig)


def is_expired(cert: Dict[str, Any], now_utc: int | None = None) -> bool:
    n = int(time.time()) if now_utc is None else int(now_utc)
    exp = int(cert.get("expires_at_utc", 0))
    return exp != 0 and n > exp
