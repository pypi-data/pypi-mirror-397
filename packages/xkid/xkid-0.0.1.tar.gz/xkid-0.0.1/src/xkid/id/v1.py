# src/xkid/id/v1.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
import json

import b32k
from b32k.codec import encode, decode, load_b32k_alphabet
from xkernel import XKernel, XKernelConfig

from xkid.id.entrogravity import EntrogravitySphericalParams, run_entrogravity_spherical
from xkid.id.digest import DigestParams, compute_digest_hex


# -----------------------------
# Params
# -----------------------------

@dataclass(frozen=True)
class OscillationParams:
    dim: int = 6
    eta: float = 0.1
    steps: int = 64
    index: int = 3
    component: int = 0
    amplitude: float = 1.0


# -----------------------------
# Trace generation
# -----------------------------

def _trace_from_xkernel(p: OscillationParams) -> List[float]:
    cfg = XKernelConfig(eta=p.eta)
    k = XKernel(dim=p.dim, config=cfg)

    state: List[float] = [0.0] * p.dim
    if 0 <= p.component < p.dim:
        state[p.component] = float(p.amplitude)

    trace: List[float] = []
    for _ in range(p.steps):
        state = k.step(state)
        try:
            sample = float(state[p.component])
        except Exception:
            sample = float(len(trace) + 1) * 1e-6
        trace.append(sample)

    return trace


# -----------------------------
# Structural helpers
# -----------------------------

def _xid_struct(
    xid: str,
    symbols: List[str],
    index: Dict[str, int],
) -> Dict[str, Any]:
    """
    Structural (lossless) representation of a Base32768 ID.
    """
    codepoints = [ord(ch) for ch in xid]
    symbol_indices = [index[ch] for ch in xid]
    payload = decode(xid, index)
    return {
        "length_symbols": len(xid),
        "codepoints": codepoints,
        "symbol_indices": symbol_indices,
        "payload_len": len(payload),
        "payload_hex": payload.hex(),
    }


def _encode_canonical_json(obj: Dict[str, Any]) -> bytes:
    """
    Canonical JSON payload bytes (normative):
    - sort_keys=True
    - ensure_ascii=False
    - separators=(",", ":")
    - UTF-8 encoding
    """
    return json.dumps(
        obj,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


# -----------------------------
# ID_V1 lenses
# -----------------------------

def id_v1_oscillation(params: Dict[str, Any]) -> Dict[str, Any]:
    p = OscillationParams(**params)
    trace = _trace_from_xkernel(p)

    # quantize trace → bytes
    ints = [int(round(x * 1_000_000)) for x in trace]
    payload = b"".join(int(i).to_bytes(4, "big", signed=True) for i in ints)

    symbols, index = load_b32k_alphabet()
    xid = encode(payload, symbols)

    return {
        "lens": "oscillation",
        "params": {
            "dim": p.dim,
            "eta": p.eta,
            "steps": p.steps,
            "index": p.index,
            "component": p.component,
            "amplitude": p.amplitude,
        },
        "trace_len": len(trace),
        "xid": xid,
        "xid_json": json.dumps(xid, ensure_ascii=False),
        "xid_struct": _xid_struct(xid, symbols, index),
    }


def id_v1_entrogravity_spherical(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic ID_V1 lens: static spherical Entrogravity reduction.
    Encodes canonical JSON payload bytes via B32K.
    """
    p = EntrogravitySphericalParams(**params)
    summary = run_entrogravity_spherical(p)

    payload_obj: Dict[str, Any] = {
        "lens": "entrogravity_spherical",
        "version": "v1",
        "params": {
            "q": p.q,
            "D0": p.D0,
            "D": p.D,
            "alpha": p.alpha,
            "beta": p.beta,
            "eps": p.eps,
            "xmax": p.xmax,
            "xmin": p.xmin,
            "steps": p.steps,
            "mu_inf": p.mu_inf,
            "A_inf": p.A_inf,
            "rho_inf": p.rho_inf,
            "F_inf": p.F_inf,
            "phi_inf": p.phi_inf,
            "cap": p.cap,
            "rho_floor": p.rho_floor,
        },
        "summary": summary,
        "invariants": {
            "deterministic": True,
            "rho_capped": bool(p.cap),
            "chi_defined": True,
        },
    }

    payload_bytes = _encode_canonical_json(payload_obj)

    symbols, index = load_b32k_alphabet()
    xid = encode(payload_bytes, symbols)

    return {
        "lens": "entrogravity_spherical",
        "params": payload_obj["params"],
        "trace_len": int(summary.get("trace_len", 0)),
        "summary": summary,
        "xid": xid,
        "xid_json": json.dumps(xid, ensure_ascii=False),
        "xid_struct": _xid_struct(xid, symbols, index),
    }


def id_v1_digest(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministic ID_V1 lens: UTF-8 text digest.
    Encodes canonical JSON payload bytes via B32K.
    """
    p = DigestParams(**params)
    d = compute_digest_hex(p)

    payload_obj: Dict[str, Any] = {
        "lens": "digest",
        "version": "v1",
        "params": {
            "algo": d["algo"],
            "text": p.text,
        },
        "digest_hex": d["digest_hex"],
        "invariants": {
            "deterministic": True,
        },
    }

    payload_bytes = _encode_canonical_json(payload_obj)

    symbols, index = load_b32k_alphabet()
    xid = encode(payload_bytes, symbols)

    return {
        "lens": "digest",
        "params": payload_obj["params"],
        "xid": xid,
        "xid_json": json.dumps(xid, ensure_ascii=False),
        "xid_struct": _xid_struct(xid, symbols, index),
    }
