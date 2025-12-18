from __future__ import annotations
from typing import Any, Dict
import time

from .canon import canon_json_bytes
from .hashing import hash_obj
from .keys import sign_detached, verify_detached


def now_utc() -> int:
    return int(time.time())


def build_claim(
    *,
    agent_id: str,
    trace_hash: str,
    features_hash: str,
    token_envelope: Dict[str, Any],
    verdict: bool,
    issued_at_utc: int | None = None,
) -> Dict[str, Any]:
    """
    Construct an unsigned XKID claim deterministically.
    """
    claim = {
        "version": 1,
        "agent": agent_id,
        "issued_at_utc": now_utc() if issued_at_utc is None else int(issued_at_utc),
        "trace_hash": trace_hash,
        "features_hash": features_hash,
        "token_envelope": token_envelope,
        "token_hash": hash_obj(token_envelope),
        "verdict": bool(verdict),
    }
    claim["claim_hash"] = hash_obj(claim)
    return claim


def sign_claim(claim: Dict[str, Any], agent_secret_b64u: str) -> Dict[str, Any]:
    """
    Sign a claim with the agent's Ed25519 key.
    Signature covers the canonical JSON of the claim without the signature field.
    """
    unsigned = dict(claim)
    unsigned.pop("signature", None)

    msg = canon_json_bytes(unsigned)
    sig = sign_detached(agent_secret_b64u, msg)

    signed = dict(unsigned)
    signed["signature"] = {"algo": "ed25519", "value": sig}
    return signed


def verify_claim_signature(claim: Dict[str, Any], agent_public_b64u: str) -> bool:
    sig = claim.get("signature", {}).get("value", "")
    if not sig:
        return False

    unsigned = dict(claim)
    unsigned.pop("signature", None)

    msg = canon_json_bytes(unsigned)
    return verify_detached(agent_public_b64u, msg, sig)
