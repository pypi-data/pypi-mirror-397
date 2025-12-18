from __future__ import annotations
import base64
import hashlib
from typing import Any

from .canon import canon_json_bytes


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def hash_obj(obj: Any) -> str:
    """
    Deterministic object hash:
    SHA-256 over canonical JSON bytes, encoded as URL-safe base64 (no padding).
    """
    return b64u(sha256(canon_json_bytes(obj)))
