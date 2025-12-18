from __future__ import annotations

import json
from pathlib import Path

import pytest

from xkid.id import id_v1_digest, id_v1_entrogravity_spherical, id_v1_oscillation


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "id_v1_golden.json"

def _require_fixture() -> dict:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            f"golden fixture missing: {FIXTURE_PATH}. Run: python tools/freeze_golden_vectors.py"
        )
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_golden_vectors_match_reference() -> None:
    fx = _require_fixture()

    # Recompute with reference implementation
    osc = id_v1_oscillation(
        {
            "dim": 6,
            "eta": 0.1,
            "steps": 8,
            "index": 3,
            "component": 0,
            "amplitude": 1.0,
        }
    )

    # "Spirelica" (for now) == entrogravity spherical reference generator.
    ent_min = id_v1_entrogravity_spherical(
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

    ent_steps_64 = id_v1_entrogravity_spherical(
        {
            "q": 1e-6,
            "D0": 1.0,
            "xmax": 1e5,
            "xmin": 10.0,
            "steps": 64,
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

    ent_range_small = id_v1_entrogravity_spherical(
        {
            "q": 1e-6,
            "D0": 1.0,
            "xmax": 1e3,
            "xmin": 1.0,
            "steps": 64,
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

    ent_q_small = id_v1_entrogravity_spherical(
        {
            "q": 1e-9,
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

    dig = id_v1_digest({"text": "hello", "algo": "sha256"})

    # Enforce exact identity + exact payload bytes (via payload_hex)
    assert osc["xid"] == fx["oscillation_small"]["xid"]
    assert osc["xid_struct"]["payload_hex"] == fx["oscillation_small"]["payload_hex"]

    assert ent_min["xid"] == fx["entrogravity_min"]["xid"]
    assert ent_min["xid_struct"]["payload_hex"] == fx["entrogravity_min"]["payload_hex"]

    assert ent_steps_64["xid"] == fx["spirelica_steps_64"]["xid"]
    assert (
        ent_steps_64["xid_struct"]["payload_hex"]
        == fx["spirelica_steps_64"]["payload_hex"]
    )

    assert ent_range_small["xid"] == fx["spirelica_range_small"]["xid"]
    assert (
        ent_range_small["xid_struct"]["payload_hex"]
        == fx["spirelica_range_small"]["payload_hex"]
    )

    assert ent_q_small["xid"] == fx["spirelica_q_small"]["xid"]
    assert (
        ent_q_small["xid_struct"]["payload_hex"] == fx["spirelica_q_small"]["payload_hex"]
    )

    assert dig["xid"] == fx["digest_hello"]["xid"]
    assert dig["xid_struct"]["payload_hex"] == fx["digest_hello"]["payload_hex"]
