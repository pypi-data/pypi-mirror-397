from __future__ import annotations

from typing import Any, Dict

from .hashutil import prefixed_sha256


def ia_hash_material(ia: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(ia)
    out.pop("ia_id", None)
    out.pop("integrity", None)
    return out


def outcome_hash_material(outcome: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(outcome)
    out.pop("outcome_id", None)
    out.pop("integrity", None)
    return out


def compute_ia_canonical_hash(ia: Dict[str, Any]) -> str:
    return prefixed_sha256(ia_hash_material(ia))


def compute_outcome_canonical_hash(outcome: Dict[str, Any]) -> str:
    return prefixed_sha256(outcome_hash_material(outcome))
