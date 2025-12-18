from __future__ import annotations

import codecs
import json
from typing import Any, Dict, Tuple

import pytest

from b32k.codec import decode, load_b32k_alphabet
from xkid.id import id_v1_digest, id_v1_entrogravity_spherical, id_v1_oscillation


def _alphabet() -> Tuple[list[str], Dict[str, int]]:
    symbols, index = load_b32k_alphabet()
    assert len(symbols) == 32768
    assert len(index) == 32768
    return symbols, index


def _payload_bytes_from_xid(xid: str) -> bytes:
    _, index = _alphabet()
    return decode(xid, index)


def _assert_structural(out: Dict[str, Any]) -> None:
    assert "xid" in out
    assert "xid_json" in out
    assert "xid_struct" in out

    xid = out["xid"]
    s = out["xid_struct"]

    for k in ("length_symbols", "codepoints", "symbol_indices", "payload_len", "payload_hex"):
        assert k in s

    assert s["length_symbols"] == len(xid)
    assert s["codepoints"] == [ord(ch) for ch in xid]

    symbols, index = _alphabet()
    assert s["symbol_indices"] == [index[ch] for ch in xid]
    assert [symbols[i] for i in s["symbol_indices"]] == list(xid)

    payload = _payload_bytes_from_xid(xid)
    assert s["payload_len"] == len(payload)
    assert s["payload_hex"] == payload.hex()

    escaped = xid.encode("unicode_escape").decode("ascii")
    roundtrip = codecs.decode(escaped, "unicode_escape")
    assert roundtrip == xid

    assert json.loads(out["xid_json"]) == xid


def _find_non_alphabet_symbol(index: Dict[str, int]) -> str:
    candidates = [
        "A", "z", "0", "\n", "\r", "\t", " ", "🚀", "🧪", "🧿", "Ω", "Ж", "中",
        "\uFFFF", "\U0010FFFF",
    ]
    for c in candidates:
        if c not in index:
            return c

    for cp in range(0, 2048):
        c = chr(cp)
        if c not in index:
            return c

    raise RuntimeError("Could not find a non-alphabet symbol to use as a failure vector.")


def test_id_v1_oscillation_structural_invariants() -> None:
    out = id_v1_oscillation(
        {
            "dim": 6,
            "eta": 0.1,
            "steps": 8,
            "index": 3,
            "component": 0,
            "amplitude": 1.0,
        }
    )
    assert out["lens"] == "oscillation"
    assert out["trace_len"] == 8
    _assert_structural(out)


def test_id_v1_entrogravity_structural_invariants() -> None:
    out = id_v1_entrogravity_spherical(
        {
            "q": 1e-6,
            "D0": 1.0,
            "xmax": 1e5,
            "xmin": 10.0,
            "steps": 200,
            "cap": False,
            "D": 0.0,
            "alpha": 0.0,
            "beta": 0.0,
            "eps": 1e-12,
            "mu_inf": 0.0,
            "A_inf": 0.0,
            "rho_inf": 1e-6,
            "F_inf": 0.0,
            "phi_inf": 0.0,
            "rho_floor": 1e-15,
        }
    )
    assert out["lens"] == "entrogravity_spherical"
    assert "summary" in out
    _assert_structural(out)

    summary = out["summary"]
    assert summary["trace_len"] > 0
    assert summary["chi_max"] == summary["chi_max"]  # not NaN
    assert summary["chi_min"] == summary["chi_min"]  # not NaN
    assert summary["chi_max"] >= summary["chi_min"]


def test_id_v1_digest_structural_invariants() -> None:
    out = id_v1_digest({"text": "hello", "algo": "sha256"})
    assert out["lens"] == "digest"
    _assert_structural(out)


def test_decode_rejects_symbol_not_in_alphabet() -> None:
    _, index = _alphabet()
    bad = _find_non_alphabet_symbol(index)

    out = id_v1_oscillation(
        {
            "dim": 6,
            "eta": 0.1,
            "steps": 8,
            "index": 3,
            "component": 0,
            "amplitude": 1.0,
        }
    )
    xid = out["xid"]

    with pytest.raises(Exception):
        decode(xid + bad, index)
