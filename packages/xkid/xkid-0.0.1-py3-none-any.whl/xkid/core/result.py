from __future__ import annotations

import platform
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _utc_now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _runtime() -> Dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }


def ok_result(
    *,
    cmd: str,
    input_: Dict[str, Any],
    output: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "schema": "xkid.CommandResult.v1",
        "cmd": cmd,
        "ok": True,
        "ts": _utc_now(),
        "runtime": _runtime(),
        "input": input_,
        "output": output,
        "artifacts": {},
        "warnings": [],
        "errors": [],
    }


def err_result(
    *,
    cmd: str,
    exc: Exception,
    debug: bool = False,
) -> Dict[str, Any]:
    diag: Dict[str, Any] = {
        "code": exc.__class__.__name__,
        "message": str(exc),
        "detail": None,
        "trace": None,
    }

    if debug:
        import traceback

        diag["trace"] = traceback.format_exc()

    return {
        "schema": "xkid.CommandResult.v1",
        "cmd": cmd,
        "ok": False,
        "ts": _utc_now(),
        "runtime": _runtime(),
        "input": {},
        "output": {},
        "artifacts": {},
        "warnings": [],
        "errors": [diag],
    }
