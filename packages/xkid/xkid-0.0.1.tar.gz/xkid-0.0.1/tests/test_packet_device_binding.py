import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run_json(cmd: list[str]) -> dict:
    """
    Run xkid with global flags in the correct position and return parsed JSON.
    """
    if not cmd or cmd[0] != "xkid":
        raise ValueError("Expected command to start with 'xkid'")
    full = ["xkid", "--out", "json"] + cmd[1:]
    p = subprocess.run(
        full,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return json.loads(p.stdout)


def test_packet_device_binding_default_is_none_for_oscillation():
    got = _run_json(
        [
            "xkid",
            "id",
            "generate",
            "--lens",
            "oscillation",
            "--param",
            "steps=8",
        ]
    )

    assert got["schema"] == "xkid.CommandResult.v1"
    assert got["ok"] is True
    assert got["cmd"] == "id.generate"

    out = got["output"]
    assert out["schema"] == "xkid.IdOutput.v1"

    # Packet must exist for oscillator (struct default ON).
    assert "packet" in out, "Expected output.packet to be present"
    pkt = out["packet"]
    assert pkt["schema"] == "xkid.Packet.v1"

    # Device binding must be explicit and stable.
    assert "device" in pkt, "Expected packet.device to be present"
    assert pkt["device"] == {"binding": "none", "present": False}
