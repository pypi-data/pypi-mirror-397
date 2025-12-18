from __future__ import annotations

import json
from pathlib import Path

from xkid.revocation import (
    ensure_v1,
    find_revocation,
    revoke_cert_hash,
    revoke_claim_hash,
    revoke_device_hash,
    SCHEMA_REVOCATIONS_V1,
)


def test_ensure_v1_upgrades_legacy() -> None:
    legacy = {
        "revoked_claim_hashes": ["c1", "c2"],
        "revoked_cert_hashes": ["k1"],
    }
    v1 = ensure_v1(legacy, now=123)
    assert v1["schema"] == SCHEMA_REVOCATIONS_V1
    assert isinstance(v1["entries"], list)

    hit = find_revocation(v1, claim_hash="c2")
    assert hit.revoked is True
    assert hit.kind == "claim_hash"


def test_revoke_idempotent(tmp_path: Path) -> None:
    p = tmp_path / "revocations.json"
    p.write_text(json.dumps({"schema": SCHEMA_REVOCATIONS_V1, "updated_at": 0, "entries": []}), encoding="utf-8")

    r1 = revoke_claim_hash(p, "c123", reason="test", now=100)
    assert len(r1["entries"]) == 1

    r2 = revoke_claim_hash(p, "c123", reason="test", now=101)
    assert len(r2["entries"]) == 1  # idempotent


def test_revoke_multiple_kinds(tmp_path: Path) -> None:
    p = tmp_path / "revocations.json"
    p.write_text(json.dumps({"schema": SCHEMA_REVOCATIONS_V1, "updated_at": 0, "entries": []}), encoding="utf-8")

    revoke_cert_hash(p, "k999", now=200)
    revoke_device_hash(p, "d777", now=201)

    obj = json.loads(p.read_text(encoding="utf-8"))
    assert obj["schema"] == SCHEMA_REVOCATIONS_V1

    assert find_revocation(obj, cert_hash="k999").revoked is True
    assert find_revocation(obj, device_hash="d777").revoked is True
    assert find_revocation(obj, cert_hash="nope").revoked is False
