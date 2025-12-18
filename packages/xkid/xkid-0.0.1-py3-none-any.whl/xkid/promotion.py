from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .hashutil import prefixed_sha256
from .world_ledger import append_entry, load_json, scan_ledger


class PromotionError(ValueError):
    pass


# -----------------------------
# WEP
# -----------------------------
def wep_hash_material(wep: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(wep)
    out.pop("wep_id", None)
    out.pop("integrity", None)
    return out


def compute_wep_canonical_hash(wep: Dict[str, Any]) -> str:
    return prefixed_sha256(wep_hash_material(wep))


def make_wep(
    *,
    world_id: str,
    ruleset_id: str,
    entry_type: str,
    payload: Dict[str, Any],
    basis_type: str,
    basis_refs: List[Dict[str, Any]],
    proposer_id: str,
    proposer_version: str,
    hash_alg: str = "SHA-256",
) -> Dict[str, Any]:
    wep: Dict[str, Any] = {
        "wep_version": "WEP_V1",
        "target_world": {"world_id": world_id, "ledger_ruleset_id": ruleset_id},
        "proposed_entry": {"entry_type": entry_type, "payload": payload},
        "proposer": {"proposer_id": proposer_id, "proposer_version": proposer_version},
        "basis": {"basis_type": basis_type, "refs": basis_refs},
    }
    canon_hash = compute_wep_canonical_hash(wep)
    wep["integrity"] = {"canonical_hash": canon_hash, "hash_alg": hash_alg}
    wep["wep_id"] = canon_hash
    return wep


def verify_wep(wep: Dict[str, Any]) -> Dict[str, Any]:
    got = wep.get("integrity", {}).get("canonical_hash")
    if not got:
        raise PromotionError("WEP missing integrity.canonical_hash")
    exp = compute_wep_canonical_hash(wep)
    if got != exp:
        raise PromotionError(f"WEP canonical_hash mismatch: expected {exp}, got {got}")
    return {"ok": True, "wep_hash": exp, "hash_alg": wep["integrity"].get("hash_alg", "SHA-256")}


# -----------------------------
# Writer auth
# -----------------------------
def _require_writer(world_dir: Path, writer_id: str) -> Dict[str, Any]:
    wd = load_json(world_dir / "world_descriptor.json")
    if writer_id not in wd.get("writer_set", []):
        raise PromotionError("authorization failure: writer not in writer_set")
    return wd


# -----------------------------
# XID existence check (3b)
# -----------------------------
def _require_xid_commit(world_dir: Path, xid_hash: str) -> Dict[str, Any]:
    """
    Enforce that xid_hash has already been committed in this world (XID_COMMIT exists).
    Returns a small proof object (seq, entry_hash) if found.
    """
    ledger_dir = world_dir / "ledger"
    for seq, etype, path in scan_ledger(ledger_dir):
        if etype != "XID_COMMIT":
            continue
        entry = load_json(path)
        payload = entry.get("payload", {})
        if isinstance(payload, dict) and payload.get("xid_hash") == xid_hash:
            return {"seq": seq, "entry_hash": entry.get("entry_hash")}
    raise PromotionError(f"xid_hash not committed in world (missing XID_COMMIT): {xid_hash}")


# -----------------------------
# Proposal commit
# -----------------------------
def append_proposal_commit(world_dir: Path, wep: Dict[str, Any], writer_id: str, timestamp: str) -> Dict[str, Any]:
    wd = _require_writer(world_dir, writer_id)

    verify_wep(wep)
    wep_hash = wep["integrity"]["canonical_hash"]
    wep_hash_alg = wep["integrity"].get("hash_alg", "SHA-256")

    payload = {
        "wep_hash": wep_hash,
        "wep_hash_alg": wep_hash_alg,
        "wep_ref": f"artifact:wep:{wep_hash}",
    }

    entry = append_entry(world_dir, "PROPOSAL_COMMIT", payload, timestamp)

    pr = {
        "pr_version": "PR_V1",
        "target_world": {"world_id": wd["world_id"], "ledger_ruleset_id": wd["ledger_ruleset_id"]},
        "wep_hash": wep_hash,
        "wep_hash_alg": wep_hash_alg,
        "world_entry_hash": entry["entry_hash"],
        "issued_at": timestamp,
        "writer": {"writer_id": writer_id},
    }
    return {"entry": entry, "receipt": pr}


# -----------------------------
# XID_COMMIT from WEP
# -----------------------------
def append_xid_commit(world_dir: Path, wep: Dict[str, Any], writer_id: str, timestamp: str) -> Dict[str, Any]:
    _require_writer(world_dir, writer_id)

    verify_wep(wep)
    proposed = wep.get("proposed_entry", {})
    if not isinstance(proposed, dict):
        raise PromotionError("WEP missing proposed_entry object")

    entry_type = proposed.get("entry_type")
    if entry_type != "XID_COMMIT":
        raise PromotionError(f"WEP proposed_entry.entry_type must be XID_COMMIT (got {entry_type!r})")

    payload = proposed.get("payload")
    if not isinstance(payload, dict):
        raise PromotionError("WEP proposed_entry.payload must be a JSON object")

    for k in ("xid_ref", "xid_hash", "xid_hash_alg"):
        if k not in payload:
            raise PromotionError(f"XID_COMMIT payload missing required field: {k}")

    wep_hash = wep["integrity"]["canonical_hash"]
    wep_hash_alg = wep["integrity"].get("hash_alg", "SHA-256")

    payload2 = dict(payload)
    payload2.setdefault("issuer", writer_id)

    basis = payload2.get("basis")
    if basis is None:
        basis = {}
    if not isinstance(basis, dict):
        raise PromotionError("XID_COMMIT payload.basis must be an object if present")

    basis = dict(basis)
    basis["wep_hash"] = wep_hash
    basis["wep_hash_alg"] = wep_hash_alg
    payload2["basis"] = basis

    entry = append_entry(world_dir, "XID_COMMIT", payload2, timestamp)
    return {"entry": entry}


# -----------------------------
# Outcome anchoring
# -----------------------------
def verify_ial_outcome(outcome: Dict[str, Any]) -> Dict[str, Any]:
    from .ial import compute_outcome_canonical_hash

    if outcome.get("outcome_version") != "IAL_OUTCOME_V1":
        raise PromotionError(f"Expected outcome_version IAL_OUTCOME_V1 (got {outcome.get('outcome_version')!r})")

    got = outcome.get("integrity", {}).get("canonical_hash")
    if not got:
        raise PromotionError("Outcome missing integrity.canonical_hash")

    exp = compute_outcome_canonical_hash(outcome)
    if got != exp:
        raise PromotionError(f"Outcome canonical_hash mismatch: expected {exp}, got {got}")

    oid = outcome.get("outcome_id")
    if oid is not None and oid != exp:
        raise PromotionError(f"Outcome outcome_id mismatch: expected {exp}, got {oid}")

    return {"ok": True, "outcome_hash": exp, "hash_alg": outcome["integrity"].get("hash_alg", "SHA-256")}


def _derive_xid_hash_from_outcome(outcome: Dict[str, Any]) -> str:
    """
    3c: outcome MUST self-bind to an XID via outcome.object_ref.hash.
    """
    obj = outcome.get("object_ref")
    if not isinstance(obj, dict):
        raise PromotionError("Outcome missing required object_ref (3c)")
    h = obj.get("hash")
    if not isinstance(h, str) or not h:
        raise PromotionError("Outcome missing required object_ref.hash (3c)")
    return h


def append_outcome_commit(
    world_dir: Path,
    outcome: Dict[str, Any],
    writer_id: str,
    timestamp: str,
    *,
    xid_hash: Optional[str] = None,
) -> Dict[str, Any]:
    """
    3b+3c:
      - 3c: outcome.object_ref.hash is authoritative binding.
      - xid_hash parameter is optional; if provided, it MUST match outcome.object_ref.hash.
      - 3b: the resulting xid_hash MUST exist as an XID_COMMIT in the world.
    """
    wd = _require_writer(world_dir, writer_id)

    bound_xid = _derive_xid_hash_from_outcome(outcome)
    if xid_hash is not None and xid_hash != bound_xid:
        raise PromotionError(f"xid_hash mismatch: outcome.object_ref.hash={bound_xid} vs --xid-hash={xid_hash}")
    xid_hash_final = bound_xid

    xid_proof = _require_xid_commit(world_dir, xid_hash_final)

    vr = verify_ial_outcome(outcome)
    outcome_hash = vr["outcome_hash"]
    outcome_hash_alg = vr["hash_alg"]

    payload: Dict[str, Any] = {
        "outcome_hash": outcome_hash,
        "outcome_hash_alg": outcome_hash_alg,
        "outcome_ref": f"artifact:outcome:{outcome_hash}",
        "issuer": writer_id,
        "outcome_type": outcome.get("outcome_type"),
        "producer": outcome.get("producer", {}),
        "xid_hash": xid_hash_final,
        "xid_commit": xid_proof,  # {seq, entry_hash}
    }

    entry = append_entry(world_dir, "OUTCOME_COMMIT", payload, timestamp)

    anchored = json_clone(outcome)
    anchored.setdefault("anchor", {})
    if not isinstance(anchored["anchor"], dict):
        anchored["anchor"] = {}
    anchored["anchor"]["world_id"] = wd["world_id"]
    anchored["anchor"]["world_entry_hash"] = entry["entry_hash"]
    anchored["anchor"]["canonicality"] = "CANONICAL"

    return {"entry": entry, "anchored_outcome": anchored}


def json_clone(x: Any) -> Any:
    import json
    return json.loads(json.dumps(x, ensure_ascii=False, separators=(",", ":")))
