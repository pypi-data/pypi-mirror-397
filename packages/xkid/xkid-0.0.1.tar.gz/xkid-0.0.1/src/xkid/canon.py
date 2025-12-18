from __future__ import annotations
import json
from typing import Any


def canon_json_bytes(obj: Any) -> bytes:
    """
    Deterministic canonical JSON encoding.
    - Sorted keys
    - No whitespace
    - UTF-8 encoding
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
