import json
from pathlib import Path

from xkid.lenses import registry

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden" / "lens_contract.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_lens_contract_requires_version_bump_on_change():
    """
    Step 5A rule:
      If a lens contract changes, the lens version MUST also change.

    Mechanism:
      Compare current registry contract hashes to tests/golden/lens_contract.json.

    If you intentionally change a contract, do BOTH:
      1) bump lens version in src/xkid/lenses/registry.py
      2) regenerate tests/golden/lens_contract.json
    """
    exp = load_json(GOLDEN)
    assert exp["schema"] == "xkid.LensContract.v1"

    exp_map = {x["name"]: x for x in exp["lenses"]}

    # Ensure no lens removed/added silently without golden update
    cur_names = sorted(registry._LENSES.keys())
    exp_names = sorted(exp_map.keys())
    assert cur_names == exp_names, f"Lens set changed: got={cur_names} exp={exp_names}"

    # Enforce: contract change => version bump
    for name in cur_names:
        d = registry._LENSES[name]
        cur_version = d.get("version")
        cur_hash = registry._contract_hash(d)

        e = exp_map[name]
        exp_version = e["version"]
        exp_hash = e["contract_sha256"]

        if cur_hash != exp_hash:
            # If contract changed, version must change (and goldens must be regenerated)
            assert cur_version != exp_version, (
                f"Lens '{name}' contract changed but version did not bump "
                f"(version={cur_version}).\n"
                f"Fix: bump version in registry.py, then regenerate tests/golden/lens_contract.json"
            )
