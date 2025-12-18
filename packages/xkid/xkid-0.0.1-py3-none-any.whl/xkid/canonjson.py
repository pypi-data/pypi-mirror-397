from __future__ import annotations

import json
import unicodedata
from decimal import Decimal
from typing import Any, Dict, List, Tuple


class CanonError(ValueError):
    pass


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def loads_no_dupe_keys(s: str) -> Any:
    def hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k, v in pairs:
            if k in out:
                raise CanonError(f"Duplicate key: {k}")
            out[k] = v
        return out

    return json.loads(s, object_pairs_hook=hook)


def _normalize(x: Any) -> Any:
    if x is None or isinstance(x, (bool, int)):
        return x
    if isinstance(x, float):
        if x != x or x in (float("inf"), float("-inf")):
            raise CanonError("Non-finite number (NaN/Infinity) not allowed")
        return Decimal(str(x))
    if isinstance(x, Decimal):
        return x
    if isinstance(x, str):
        return _nfc(x)
    if isinstance(x, list):
        return [_normalize(v) for v in x]
    if isinstance(x, dict):
        return {_nfc(str(k)): _normalize(v) for k, v in x.items()}
    raise CanonError(f"Unsupported type: {type(x)}")


def _dec_to_str(d: Decimal) -> str:
    if d.is_zero():
        return "0"
    sign, digits, exp = d.as_tuple()
    if exp >= 0:
        s = "".join(map(str, digits)) + ("0" * exp)
        return ("-" if sign else "") + s
    n = len(digits)
    point = n + exp
    if point <= 0:
        s = "0." + ("0" * (-point)) + "".join(map(str, digits))
    else:
        s = "".join(map(str, digits[:point])) + "." + "".join(map(str, digits[point:]))
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s == "-0":
        s = "0"
    return ("-" if sign else "") + s.lstrip("+")


def _emit(x: Any) -> str:
    if x is None:
        return "null"
    if x is True:
        return "true"
    if x is False:
        return "false"
    if isinstance(x, int):
        return str(x)
    if isinstance(x, Decimal):
        return _dec_to_str(x)
    if isinstance(x, str):
        return json.dumps(x, ensure_ascii=False, separators=(",", ":"))
    if isinstance(x, list):
        return "[" + ",".join(_emit(v) for v in x) + "]"
    if isinstance(x, dict):
        items = sorted(x.items(), key=lambda kv: kv[0])
        return "{" + ",".join(_emit(k) + ":" + _emit(v) for k, v in items) + "}"
    raise CanonError(f"Unsupported normalized type: {type(x)}")


def canonical_json_bytes(obj: Any) -> bytes:
    norm = _normalize(obj)
    s = _emit(norm)
    return s.encode("utf-8")
