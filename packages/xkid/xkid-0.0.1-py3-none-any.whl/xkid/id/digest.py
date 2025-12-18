from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import hashlib


@dataclass(frozen=True)
class DigestParams:
    text: str
    algo: str = "sha256"


def compute_digest_hex(p: DigestParams) -> Dict[str, str]:
    """
    Deterministic digest computation over UTF-8 bytes of `text`.
    Returns a small summary dict suitable for canonical JSON payloads.
    """
    algo = (p.algo or "").strip().lower()
    if not algo:
        raise ValueError("algo must be a non-empty string")

    try:
        h = hashlib.new(algo)
    except ValueError as e:
        raise ValueError(f"unsupported digest algo: {algo}") from e

    h.update(p.text.encode("utf-8"))
    return {
        "algo": algo,
        "digest_hex": h.hexdigest(),
    }
