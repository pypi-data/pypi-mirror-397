from __future__ import annotations
from typing import Any, Dict
import json
from pathlib import Path


def load_trust_store(path: Path) -> Dict[str, Any]:
    """
    Load a local XKID trust store.
    This is a pure O0 input: no network, no mutation.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def is_trusted_issuer(
    trust: Dict[str, Any],
    issuer_id: str,
    issuer_pub_b64u: str,
) -> bool:
    """
    Check whether an issuer (id + public key) is pinned in the trust store.
    """
    for entry in trust.get("trusted_issuers", []):
        if (
            entry.get("issuer_id") == issuer_id
            and entry.get("pub") == issuer_pub_b64u
        ):
            return True
    return False
