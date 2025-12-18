from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    # Run the installed console script entrypoint via python -m, for test stability.
    # If your project exposes "xkid" as a console_script, this still works because
    # it executes the same code path through the module.
    return subprocess.run(
        [sys.executable, "-m", "xkid.cli.app", *args],
        check=False,
        text=True,
        capture_output=True,
    )


def _write_empty_revocations_v1(path: Path) -> None:
    path.write_text(
        json.dumps(
            {"schema": "xkid.Revocations.v1", "updated_at": 0, "entries": []},
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def test_sysop_revoke_adds_entry(tmp_path: Path) -> None:
    store = tmp_path / "revocations.json"
    _write_empty_revocations_v1(store)

    cp = _run(
        [
            "sysop",
            "revoke",
            "--store",
            str(store),
            "--claim",
            "sha256:test-claim",
            "--reason",
            "unit_test",
            "--out",
            "json",
        ]
    )
    assert cp.returncode == 0, (cp.stdout, cp.stderr)

    obj = json.loads(store.read_text(encoding="utf-8"))
    assert obj["schema"] == "xkid.Revocations.v1"
    assert len(obj["entries"]) == 1
    assert obj["entries"][0]["kind"] == "claim_hash"
    assert obj["entries"][0]["key"] == "sha256:test-claim"


def test_sysop_revoke_idempotent(tmp_path: Path) -> None:
    store = tmp_path / "revocations.json"
    _write_empty_revocations_v1(store)

    cp1 = _run(
        [
            "sysop",
            "revoke",
            "--store",
            str(store),
            "--cert",
            "sha256:test-cert",
            "--out",
            "json",
        ]
    )
    assert cp1.returncode == 0, (cp1.stdout, cp1.stderr)

    cp2 = _run(
        [
            "sysop",
            "revoke",
            "--store",
            str(store),
            "--cert",
            "sha256:test-cert",
            "--out",
            "json",
        ]
    )
    assert cp2.returncode == 0, (cp2.stdout, cp2.stderr)

    obj = json.loads(store.read_text(encoding="utf-8"))
    assert obj["schema"] == "xkid.Revocations.v1"
    assert len(obj["entries"]) == 1
    assert obj["entries"][0]["kind"] == "cert_hash"
    assert obj["entries"][0]["key"] == "sha256:test-cert"
