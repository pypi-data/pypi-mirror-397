import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "tests" / "golden"


def _with_global_flags(cmd: list[str]) -> list[str]:
    """
    Ensure global CLI flags appear before subcommands.

    Argparse treats --out as a *global* flag. If it appears after
    `lens` / `id`, it is rejected as "unrecognized arguments".

    Tests always force JSON output to keep goldens stable.
    """
    if not cmd or cmd[0] != "xkid":
        raise ValueError("Expected command to start with 'xkid'")
    return ["xkid", "--out", "json"] + cmd[1:]


def run(cmd: list[str]) -> str:
    cmd = _with_global_flags(cmd)
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return p.stdout.strip()


def run_no_check(cmd: list[str]) -> str:
    cmd = _with_global_flags(cmd)
    p = subprocess.run(
        cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return p.stdout.strip()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_lens_list_golden():
    out = run(["xkid", "lens", "list"])
    got = json.loads(out)
    exp = load_json(GOLDEN / "lens_list.json")

    # schema + command identity are invariants
    assert got["schema"] == exp["schema"]
    assert got["cmd"] == exp["cmd"]

    # lens registry must match exactly
    assert got["output"] == exp["output"]


def test_id_oscillation_golden():
    out = run(
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
    got = json.loads(out)
    exp = load_json(GOLDEN / "id_oscillation.json")

    # invariants
    assert got["schema"] == exp["schema"]
    assert got["cmd"] == exp["cmd"]
    assert got["ok"] is True

    # lens + params invariant
    assert got["output"]["lens"] == "oscillation"
    assert got["output"]["params"] == exp["output"]["params"]

    # structural invariants (not timestamp/runtime)
    assert got["output"]["trace_len"] == exp["output"]["trace_len"]
    assert got["output"]["xid_struct"] == exp["output"]["xid_struct"]


def test_need_trace_rejected_for_digest():
    out = run_no_check(
        [
            "xkid",
            "id",
            "generate",
            "--lens",
            "digest",
            "--param",
            "text=hello",
            "--need-trace",
        ]
    )
    got = json.loads(out)

    assert got["schema"] == "xkid.CommandResult.v1"
    assert got["ok"] is False
    assert got["cmd"] == "cli.error"
    assert got["errors"], "Expected at least one error"
    msg = got["errors"][0]["message"]
    assert "does not support required capability: trace" in msg
