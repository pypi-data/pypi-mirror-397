from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Dict


def _run(args: list[str], env: Dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    e = os.environ.copy()
    if env:
        e.update(env)
    return subprocess.run(
        [sys.executable, "-m", "xkid.cli.app", *args],
        check=False,
        text=True,
        capture_output=True,
        env=e,
    )


def _stdout_json(cp: subprocess.CompletedProcess[str]) -> dict:
    # CLI always emits JSON for --out json, even on errors.
    return json.loads(cp.stdout)


def test_sysop_attest_required_fails_when_no_device_available() -> None:
    # Required binding, but forbid external binding -> provider returns no device -> should fail.
    cp = _run(
        ["sysop", "attest", "--challenge", "test", "--out", "json"],
        env={
            "XKID_ATTEST_KEY": "dev-test-key",
            "XKID_DEVICE_BINDING": "required",
            "XKID_DEVICE_ALLOW_EXTERNAL": "0",
        },
    )
    assert cp.returncode != 0, (cp.stdout, cp.stderr)
    obj = _stdout_json(cp)
    assert obj["ok"] is False
    msg = obj["errors"][0]["message"]
    assert "Device binding required" in msg


def test_sysop_attest_required_passes_when_device_present() -> None:
    cp = _run(
        ["sysop", "attest", "--challenge", "test", "--out", "json"],
        env={
            "XKID_ATTEST_KEY": "dev-test-key",
            "XKID_DEVICE_BINDING": "required",
        },
    )
    assert cp.returncode == 0, (cp.stdout, cp.stderr)
    obj = _stdout_json(cp)
    assert obj["ok"] is True
    dev = obj["output"]["attestation"]["device"]
    assert dev["present"] is True
    assert dev["binding"] != "none"
    assert isinstance(dev.get("kid"), str) and dev["kid"]


def test_sysop_attest_sealed_fails_with_nonsealed_provider() -> None:
    # Default provider is A-mode external; sealed must fail.
    cp = _run(
        ["sysop", "attest", "--challenge", "test", "--out", "json"],
        env={
            "XKID_ATTEST_KEY": "dev-test-key",
            "XKID_DEVICE_BINDING": "sealed",
        },
    )
    assert cp.returncode != 0, (cp.stdout, cp.stderr)
    obj = _stdout_json(cp)
    assert obj["ok"] is False
    msg = obj["errors"][0]["message"]
    assert "Sealed device binding required" in msg
