from __future__ import annotations

import hashlib
from typing import Any

from .canonjson import canonical_json_bytes


def sha256_hex_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_hex_canon(obj: Any) -> str:
    return sha256_hex_bytes(canonical_json_bytes(obj))


def prefixed_sha256(obj: Any) -> str:
    return "sha256:" + sha256_hex_canon(obj)
