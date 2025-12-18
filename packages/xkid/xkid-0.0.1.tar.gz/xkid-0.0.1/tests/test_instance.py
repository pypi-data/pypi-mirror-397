# tests/test_instance.py
from __future__ import annotations

from pathlib import Path

from xkid.instance import ensure_instance, load_instance, whoami


def test_instance_is_stable(tmp_path: Path) -> None:
    root = tmp_path / "rookinc"

    rec1 = ensure_instance(root, name="rookinc")
    rec2 = ensure_instance(root, name="rookinc")

    assert rec1.instance_id == rec2.instance_id
    assert whoami(root) == rec1.instance_id

    loaded = load_instance(root)
    assert loaded.instance_id == rec1.instance_id
    assert loaded.name == "rookinc"

