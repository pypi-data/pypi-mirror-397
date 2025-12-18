from __future__ import annotations

import json
import hashlib
from typing import Any


def canonical_bytes(obj: Any) -> bytes:
    """
    Canonical JSON encoding:
    - UTF-8
    - sorted keys
    - no NaN / Infinity
    - stable separators
    """
    text = json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return text.encode("utf-8")


def canonical_dumps(obj: Any) -> str:
    return canonical_bytes(obj).decode("utf-8")


def canon_hash(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()
