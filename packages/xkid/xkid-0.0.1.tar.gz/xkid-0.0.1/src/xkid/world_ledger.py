from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .hashutil import prefixed_sha256

LEDGER_FN_RE = re.compile(r"^(?P<seq>\d{8})_(?P<etype>[A-Z_]+)\.json$")


class LedgerError(ValueError):
    pass


def entry_hash_material(entry: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(entry)
    out.pop("entry_hash", None)
    return out


def compute_entry_hash(entry: Dict[str, Any]) -> str:
    return prefixed_sha256(entry_hash_material(entry))


def format_entry_filename(seq: int, entry_type: str) -> str:
    return f"{seq:08d}_{entry_type}.json"


def load_json(path: Path) -> Dict[str, Any]:
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def write_json_atomic(path: Path, obj: Dict[str, Any]) -> None:
    import json

    tmp = path.with_name(".tmp_" + path.name)
    tmp.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def scan_ledger(ledger_dir: Path) -> List[Tuple[int, str, Path]]:
    rows: List[Tuple[int, str, Path]] = []
    if not ledger_dir.exists():
        return rows
    for p in ledger_dir.iterdir():
        if not p.is_file():
            continue
        m = LEDGER_FN_RE.match(p.name)
        if not m:
            continue
        rows.append((int(m.group("seq")), m.group("etype"), p))
    rows.sort(key=lambda t: t[0])
    return rows


def get_head(ledger_dir: Path) -> Tuple[Optional[Dict[str, Any]], int]:
    rows = scan_ledger(ledger_dir)
    if not rows:
        return None, 0

    for i, (seq, et, p) in enumerate(rows):
        if seq != i:
            raise LedgerError(f"Ledger seq gap or mismatch: expected {i:08d}, got {seq:08d} ({p.name})")

        entry = load_json(p)
        if entry.get("header", {}).get("seq") != seq:
            raise LedgerError(f"Header seq mismatch in {p.name}")
        if entry.get("header", {}).get("entry_type") != et:
            raise LedgerError(f"Header entry_type mismatch in {p.name}")

        expected = compute_entry_hash(entry)
        if entry.get("entry_hash") != expected:
            raise LedgerError(f"entry_hash mismatch in {p.name}: expected {expected}")

        if seq == 0:
            if entry.get("prev_hash", None) is not None:
                raise LedgerError("Genesis prev_hash must be null")
        else:
            prev_entry = load_json(rows[seq - 1][2])
            if entry.get("prev_hash") != prev_entry.get("entry_hash"):
                raise LedgerError(f"prev_hash mismatch at {p.name}")

    return load_json(rows[-1][2]), len(rows)


def _read_world_descriptor(world_dir: Path) -> Dict[str, Any]:
    wd_path = world_dir / "world_descriptor.json"
    if not wd_path.exists():
        raise LedgerError("Missing world_descriptor.json")
    return load_json(wd_path)


def _read_world_id(world_dir: Path) -> str:
    return _read_world_descriptor(world_dir)["world_id"]


def _read_ruleset_id(world_dir: Path) -> str:
    return _read_world_descriptor(world_dir)["ledger_ruleset_id"]


def append_entry(world_dir: Path, entry_type: str, payload: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
    ledger_dir = world_dir / "ledger"
    ledger_dir.mkdir(parents=True, exist_ok=True)

    head, next_seq = get_head(ledger_dir)
    prev_hash = None if next_seq == 0 else head["entry_hash"]  # type: ignore[index]

    entry: Dict[str, Any] = {
        "header": {
            "world_id": _read_world_id(world_dir),
            "entry_type": entry_type,
            "seq": next_seq,
            "ruleset_id": _read_ruleset_id(world_dir),
            "timestamp": timestamp,
        },
        "payload": payload,
        "prev_hash": prev_hash,
    }
    entry["entry_hash"] = compute_entry_hash(entry)

    fn = format_entry_filename(next_seq, entry_type)
    write_json_atomic(ledger_dir / fn, entry)
    return entry
