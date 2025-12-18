from __future__ import annotations

import json
import sys
from typing import Any, Dict

from xkid.core.canonical import canonical_dumps


def emit_result(result: Dict[str, Any], *, out: str = "json") -> int:
    """
    Emit a CommandResult.
    """
    if out == "raw":
        # Convention: raw prints primary artifact if present
        xid = result.get("output", {}).get("xid")
        if isinstance(xid, str):
            sys.stdout.write(xid + "\n")
            return 0 if result.get("ok") else 1

    if out == "pretty":
        sys.stdout.write(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        )
        return 0 if result.get("ok") else 1

    # canonical JSON (default)
    sys.stdout.write(canonical_dumps(result) + "\n")
    return 0 if result.get("ok") else 1
