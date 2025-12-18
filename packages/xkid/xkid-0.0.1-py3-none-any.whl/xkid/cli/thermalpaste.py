from __future__ import annotations

import argparse
import base64
import json
import os

from xkid.thermalpaste.types import KeySpec
from xkid.thermalpaste.providers.null_provider import NullThermalpasteProvider


def _b64_nonce(n: int = 32) -> str:
    return base64.b64encode(os.urandom(n)).decode("ascii")


def add_thermalpaste_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("thermalpaste", help="Export thermalpaste device binding claim")
    p.add_argument("--provider", default="null", help="Provider id (currently only: null)")
    p.add_argument("--name", default="jr-device-root", help="Key name/handle label")
    p.add_argument("--alg", default="ES256", help="Algorithm (informative for now)")
    p.add_argument("--kty", default="EC", help="Key type (informative for now)")
    p.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    p.set_defaults(_xkid_cmd="sysop.thermalpaste")


def run_sysop_thermalpaste(args: argparse.Namespace) -> dict:
    # Provider selection (expand later)
    if args.provider != "null":
        raise SystemExit(f"thermalpaste provider not available yet: {args.provider}")

    provider = NullThermalpasteProvider()

    spec = KeySpec(
        kty=args.kty,
        alg=args.alg,
        purpose=["sign", "verify"],
        user_auth="none",
        require_hardware=True,
        require_non_exportable=True,
        require_sealed=False,
    )

    kid = provider.ensure_key(args.name, spec)
    nonce_b64 = _b64_nonce()
    claim = provider.export_claim(kid, nonce_b64).to_json()

    return {
        "ok": True,
        "cmd": "sysop.thermalpaste",
        "output": {
            "nonce_b64": nonce_b64,
            "claim": claim,
        },
        "errors": [],
        "artifacts": {},
        "input": {
            "provider": args.provider,
            "name": args.name,
            "kty": args.kty,
            "alg": args.alg,
        },
    }
