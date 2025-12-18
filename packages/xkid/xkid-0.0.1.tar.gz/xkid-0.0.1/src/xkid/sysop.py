from __future__ import annotations

"""
sysop.py

Thin shim to provide the CLI-facing sysop_* functions.

We keep these wrappers so the CLI can import from `xkid.sysop` even if
implementations live in other modules (attest/verify/revocation, etc.).
"""

from xkid.attest import sysop_attest, sysop_challenge
from xkid.verify import sysop_verify
from xkid.revocation import sysop_revoke

__all__ = [
    "sysop_attest",
    "sysop_challenge",
    "sysop_verify",
    "sysop_revoke",
]
