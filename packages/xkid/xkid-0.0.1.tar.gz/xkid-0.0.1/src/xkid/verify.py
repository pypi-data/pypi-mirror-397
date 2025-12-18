from __future__ import annotations
from typing import Any, Dict

from .claim import verify_claim_signature
from .cert import verify_cert_signature, is_expired
from .trust import is_trusted_issuer
from .revocation import is_revoked


def verify_bundle(
    *,
    xkid: Dict[str, Any],
    trust_store: Dict[str, Any],
    revocations: Dict[str, Any],
    agent_pub_b64u: str,
) -> Dict[str, Any]:
    """
    Verify a full XKID bundle.
    Returns a structured verification report.
    """

    # --- certificate signature ---
    if not verify_cert_signature(xkid):
        return {"status": "invalid", "reason": "bad_certificate_signature"}

    issuer = xkid.get("issuer", {})
    issuer_id = issuer.get("issuer_id", "")
    issuer_pub = issuer.get("pub", "")

    # --- trust ---
    if not is_trusted_issuer(trust_store, issuer_id, issuer_pub):
        return {"status": "invalid", "reason": "untrusted_issuer"}

    # --- expiration ---
    if is_expired(xkid):
        return {"status": "invalid", "reason": "certificate_expired"}

    claim = xkid.get("claim", {})

    # --- claim signature ---
    if not verify_claim_signature(claim, agent_pub_b64u):
        return {"status": "invalid", "reason": "bad_claim_signature"}

    # --- revocation ---
    if is_revoked(
        revocations,
        claim_hash=claim.get("claim_hash"),
        cert_hash=xkid.get("certificate_hash"),
    ):
        return {"status": "invalid", "reason": "revoked"}

    return {
        "status": "valid",
        "issuer": issuer_id,
        "agent": claim.get("agent"),
    }
