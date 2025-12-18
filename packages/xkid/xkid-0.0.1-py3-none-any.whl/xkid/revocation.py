from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

SCHEMA_REVOCATIONS_V1 = "xkid.Revocations.v1"


@dataclass(frozen=True)
class RevocationHit:
    revoked: bool
    kind: str
    key: str


def ensure_v1(obj: Dict[str, Any], *, now: Optional[int] = None) -> Dict[str, Any]:
    """
    Normalize a revocations object to xkid.Revocations.v1.

    Supports legacy format:
      {
        "revoked_claim_hashes": [...],
        "revoked_cert_hashes":  [...],
      }

    The 'now' argument exists for deterministic tests.
    """
    now_i = int(time.time()) if now is None else int(now)

    if obj.get("schema") == SCHEMA_REVOCATIONS_V1:
        # Ensure required fields exist
        if not isinstance(obj.get("entries"), list):
            obj["entries"] = []
        if not isinstance(obj.get("updated_at"), int):
            obj["updated_at"] = int(obj.get("updated_at") or 0)
        return obj

    entries: list[dict[str, Any]] = []

    for h in obj.get("revoked_claim_hashes", []) or []:
        if isinstance(h, str) and h:
            entries.append({"kind": "claim_hash", "key": h, "revoked_at": now_i})

    for h in obj.get("revoked_cert_hashes", []) or []:
        if isinstance(h, str) and h:
            entries.append({"kind": "cert_hash", "key": h, "revoked_at": now_i})

    return {
        "schema": SCHEMA_REVOCATIONS_V1,
        "updated_at": now_i if entries else 0,
        "entries": entries,
    }


def _load_or_init(path: Path) -> Dict[str, Any]:
    if path.exists():
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("revocations store must be a JSON object")
        return ensure_v1(raw)
    return {"schema": SCHEMA_REVOCATIONS_V1, "updated_at": 0, "entries": []}


def _write(path: Path, obj: Dict[str, Any]) -> Dict[str, Any]:
    # Stable, readable output; tests do not require canonical separators here.
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return obj


def find_revocation(
    obj: Dict[str, Any],
    *,
    claim_hash: str | None = None,
    cert_hash: str | None = None,
    device_hash: str | None = None,
) -> RevocationHit:
    """
    Query a v1 revocations object for a matching entry.
    Exactly one of claim_hash/cert_hash/device_hash should be provided.
    """
    obj2 = ensure_v1(obj)

    keys = [
        ("claim_hash", claim_hash),
        ("cert_hash", cert_hash),
        ("device_hash", device_hash),
    ]
    chosen = [(k, v) for (k, v) in keys if isinstance(v, str) and v]
    if len(chosen) != 1:
        raise ValueError("find_revocation requires exactly one of: claim_hash, cert_hash, device_hash")

    kind, key = chosen[0]
    entries = obj2.get("entries", [])
    if not isinstance(entries, list):
        entries = []

    for e in entries:
        if not isinstance(e, dict):
            continue
        if e.get("kind") == kind and e.get("key") == key:
            return RevocationHit(revoked=True, kind=kind, key=key)

    return RevocationHit(revoked=False, kind=kind, key=key)


def is_revoked(
    obj: Dict[str, Any],
    *,
    claim_hash: str | None = None,
    cert_hash: str | None = None,
    device_hash: str | None = None,
) -> bool:
    """
    Boolean wrapper used by verify.py.
    Exactly one of claim_hash/cert_hash/device_hash must be provided.
    """
    return find_revocation(
        obj,
        claim_hash=claim_hash,
        cert_hash=cert_hash,
        device_hash=device_hash,
    ).revoked


def _revoke(
    path: Path,
    *,
    kind: str,
    key: str,
    reason: Optional[str] = None,
    now: Optional[int] = None,
) -> Dict[str, Any]:
    if not isinstance(key, str) or not key:
        raise ValueError("revocation key must be a non-empty string")

    now_i = int(time.time()) if now is None else int(now)

    obj = _load_or_init(path)
    obj = ensure_v1(obj)
    entries = obj.get("entries", [])
    if not isinstance(entries, list):
        entries = []
        obj["entries"] = entries

    # idempotent
    for e in entries:
        if isinstance(e, dict) and e.get("kind") == kind and e.get("key") == key:
            return obj

    entry: Dict[str, Any] = {"kind": kind, "key": key, "revoked_at": now_i}
    if isinstance(reason, str) and reason:
        entry["reason"] = reason

    entries.append(entry)
    obj["updated_at"] = now_i

    return _write(path, obj)


def revoke_claim_hash(
    path: Path,
    key: str,
    *,
    reason: Optional[str] = None,
    now: Optional[int] = None,
) -> Dict[str, Any]:
    return _revoke(path, kind="claim_hash", key=key, reason=reason, now=now)


def revoke_cert_hash(
    path: Path,
    key: str,
    *,
    reason: Optional[str] = None,
    now: Optional[int] = None,
) -> Dict[str, Any]:
    return _revoke(path, kind="cert_hash", key=key, reason=reason, now=now)


def revoke_device_hash(
    path: Path,
    key: str,
    *,
    reason: Optional[str] = None,
    now: Optional[int] = None,
) -> Dict[str, Any]:
    return _revoke(path, kind="device_hash", key=key, reason=reason, now=now)
