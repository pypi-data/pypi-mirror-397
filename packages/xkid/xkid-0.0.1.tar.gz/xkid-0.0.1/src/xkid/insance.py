# src/xkid/instance.py
from __future__ import annotations

import json
import os
import platform
import socket
import time
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_INSTANCE_FILENAME = "instance.json"


@dataclass(frozen=True)
class InstanceRecord:
    kind: str
    name: str
    instance_id: str
    created_unix: int
    host: str
    platform: str
    cwd: str
    user: Optional[str] = None
    schema_version: str = "0.1"


def instance_path(root: Path, filename: str = DEFAULT_INSTANCE_FILENAME) -> Path:
    """
    Canonical path for an instance record anchored at `root`.
    """
    return root / filename


def load_instance(root: Path, filename: str = DEFAULT_INSTANCE_FILENAME) -> InstanceRecord:
    p = instance_path(root, filename=filename)
    data = json.loads(p.read_text(encoding="utf-8"))
    return InstanceRecord(**data)


def ensure_instance(root: Path, name: str, filename: str = DEFAULT_INSTANCE_FILENAME) -> InstanceRecord:
    """
    Create-once, then stable: ensures an InstanceRecord exists at root/instance.json.
    Returns the record (existing or newly created).
    """
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)

    p = instance_path(root, filename=filename)
    if p.exists():
        return load_instance(root, filename=filename)

    rec = InstanceRecord(
        kind="agent_instance",
        name=name,
        instance_id=uuid.uuid4().hex,
        created_unix=int(time.time()),
        host=socket.gethostname(),
        platform=platform.platform(),
        cwd=str(root.resolve()),
        user=os.environ.get("USER") or os.environ.get("USERNAME"),
    )

    p.write_text(json.dumps(asdict(rec), indent=2) + "\n", encoding="utf-8")
    return rec


def whoami(root: Path, filename: str = DEFAULT_INSTANCE_FILENAME) -> str:
    """
    Convenience: returns the stable instance_id for the instance anchored at root.
    """
    return load_instance(root, filename=filename).instance_id


def as_json(root: Path, filename: str = DEFAULT_INSTANCE_FILENAME) -> Dict[str, Any]:
    """
    Convenience: returns the instance record as a dict.
    """
    return asdict(load_instance(root, filename=filename))

