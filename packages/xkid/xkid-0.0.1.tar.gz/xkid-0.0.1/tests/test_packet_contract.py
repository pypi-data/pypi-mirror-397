import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> str:
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return p.stdout.strip()


def test_packet_contract_null_plus_one_oscillation():
    out = run(
        [
            "xkid",
            "--out",
            "json",
            "id",
            "generate",
            "--lens",
            "oscillation",
            "--param",
            "steps=8",
        ]
    )
    got = json.loads(out)

    assert got["schema"] == "xkid.CommandResult.v1"
    assert got["ok"] is True
    assert got["cmd"] == "id.generate"

    o = got["output"]
    assert o["schema"] == "xkid.IdOutput.v1"

    # Packet must exist for oscillator (struct is default ON).
    assert "packet" in o, "Expected output.packet to be present"
    p = o["packet"]

    assert p["schema"] == "xkid.Packet.v1"

    # Transport contract: packet carries the b32k block and must match xid.
    assert "b32k" in p
    assert p["b32k"] == o["xid"]

    # Canonical bytes: packet.bytes_hex must match xid_struct.payload_hex
    xs = o.get("xid_struct") or {}
    assert p["bytes_hex"] == xs["payload_hex"]

    # Commitment: sha256 must be 64 hex chars
    sha = p["sha256_hex"]
    assert isinstance(sha, str)
    assert len(sha) == 64
    int(sha, 16)  # must parse as hex
