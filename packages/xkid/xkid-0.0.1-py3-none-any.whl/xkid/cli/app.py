from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from xkid.instance import ensure_instance, load_instance
from typing import Any, Dict, List, Optional, Tuple

from xkid.attest import AttestInputs, make_challenge, sign_attestation, verify_attestation
from xkid.cli.emit import emit_result
from xkid.core.result import err_result, ok_result
from xkid.lenses.registry import lens_describe, lens_list, lens_run
from xkid.packet import packet_v1_from_id_output
from xkid.revocation import revoke_cert_hash, revoke_claim_hash, revoke_device_hash
from xkid.cli.contract import (
    CMD_ID_GENERATE,
    CMD_LENS_DESCRIBE,
    CMD_LENS_LIST,
    NULL_PLUS_ONE,
    NULL_PLUS_ONE_MOUNT_LENS,
    SCHEMA_ID_OUTPUT,
)


def _parse_kv(s: str) -> tuple[str, Any]:
    if "=" not in s:
        raise ValueError("Expected k=v")
    k, v = s.split("=", 1)
    try:
        v2 = json.loads(v)
    except Exception:
        v2 = v
    return k, v2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="xkid", add_help=True)

    # Global flags
    p.add_argument("--out", choices=["json", "pretty", "raw"], default="json")
    p.add_argument("--debug", action="store_true")

    sub = p.add_subparsers(dest="family", required=True)

    # lens
    p_lens = sub.add_parser("lens")
    lens_sub = p_lens.add_subparsers(dest="lens_cmd", required=True)
    lens_sub.add_parser("list")
    p_ld = lens_sub.add_parser("describe")
    p_ld.add_argument("name")

    # id
    p_id = sub.add_parser("id")
    id_sub = p_id.add_subparsers(dest="id_cmd", required=True)
    p_gen = id_sub.add_parser("generate")
    p_gen.add_argument("--lens", required=True)
    p_gen.add_argument("--param", action="append", default=[], help="k=v (v may be JSON)")
    p_gen.add_argument("--params", default=None, help='JSON object (e.g. \'{"steps":8}\')')

    # caller intent (want)
    # Defaults preserve current goldens: struct ON, trace OFF.
    p_gen.add_argument("--need-struct", action="store_true", help="require structural output (xid_struct)")
    p_gen.add_argument("--no-struct", action="store_true", help="suppress structural output (omit xid_struct)")
    p_gen.add_argument("--need-trace", action="store_true", help="require trace output (trace array)")
    p_gen.add_argument("--no-trace", action="store_true", help="suppress trace output (omit trace array)")

    # sysop
    p_sysop = sub.add_parser("sysop")
    sysop_sub = p_sysop.add_subparsers(dest="sysop_cmd", required=True)

    # sysop instance (local, non-crypto identity)
    p_i = sysop_sub.add_parser("instance", help="Instance identity helpers (non-crypto)")
    inst_sub = p_i.add_subparsers(dest="instance_cmd", required=True)

    p_i_init = inst_sub.add_parser("init", help="Create instance.json if missing; print instance_id")
    p_i_init.add_argument("--name", required=True, help="Logical name (e.g. rookinc, citadel, jr)")
    p_i_init.add_argument("--root", default=".", help="Directory to anchor instance.json")

    p_i_who = inst_sub.add_parser("whoami", help="Print stable instance_id")
    p_i_who.add_argument("--root", default=".", help="Directory to anchor instance.json")

    p_i_show = inst_sub.add_parser("show", help="Print full instance record JSON")
    p_i_show.add_argument("--root", default=".", help="Directory to anchor instance.json")

    p_ch = sysop_sub.add_parser("challenge")
    p_ch.add_argument("--bytes", type=int, default=32, help="nonce size in bytes (default: 32)")

    p_at = sysop_sub.add_parser("attest")
    p_at.add_argument("--challenge", required=True, help="challenge nonce (base64url from sysop challenge)")
    # v1: hard-bind to the Null+1 mount. Keep it explicit.
    p_at.add_argument("--lens", default=NULL_PLUS_ONE_MOUNT_LENS, help=f"default: {NULL_PLUS_ONE_MOUNT_LENS}")
    p_at.add_argument("--param", action="append", default=[], help="k=v (v may be JSON)")
    p_at.add_argument("--params", default=None, help='JSON object (e.g. \'{"steps":8}\')')

    p_v = sysop_sub.add_parser("verify")
    p_v.add_argument("--challenge", default=None, help="expected challenge (recommended)")
    p_v.add_argument("--attestation", default=None, help="path to attestation JSON (else read stdin)")

    # sysop revoke (v1)
    p_r = sysop_sub.add_parser("revoke")
    p_r.add_argument("--store", required=True, help="path to local revocations.json store")
    g = p_r.add_mutually_exclusive_group(required=True)
    g.add_argument("--claim", help="claim hash key to revoke (e.g. sha256:...)")
    g.add_argument("--cert", help="certificate hash key to revoke (e.g. sha256:...)")
    g.add_argument("--device", help="device hash key to revoke (e.g. sha256:...)")
    p_r.add_argument("--reason", default=None, help="optional human reason string")

    return p


def _load_params(args: Any) -> Dict[str, Any]:
    params: Dict[str, Any] = {}
    if getattr(args, "params", None):
        params.update(json.loads(args.params))
    for kv in getattr(args, "param", []) or []:
        k, v = _parse_kv(kv)
        params[k] = v
    return params


def _load_need_flags(args: Any) -> tuple[bool, bool]:
    # Defaults preserve current behavior/goldens:
    want_struct = True
    want_trace = False

    need_struct = bool(getattr(args, "need_struct", False))
    no_struct = bool(getattr(args, "no_struct", False))
    need_trace = bool(getattr(args, "need_trace", False))
    no_trace = bool(getattr(args, "no_trace", False))

    if need_struct and no_struct:
        raise ValueError("Conflicting flags: --need-struct and --no-struct")
    if need_trace and no_trace:
        raise ValueError("Conflicting flags: --need-trace and --no-trace")

    if need_struct:
        want_struct = True
    if no_struct:
        want_struct = False

    if need_trace:
        want_trace = True
    if no_trace:
        want_trace = False

    return want_struct, want_trace


def _read_json_file(path: str) -> Dict[str, Any]:
    return json.loads(open(path, "r", encoding="utf-8").read())


def _extract_global_flags(argv: List[str]) -> Tuple[List[str], Dict[str, Any]]:
    """
    Allow global flags (--out, --debug) to appear anywhere in argv, including
    after subcommands. Argparse subparsers + parse_intermixed_args do not mix
    reliably, so we do a tiny pre-scan.

    Returns: (argv_without_globals, globals_dict)
    """
    out_val: Optional[str] = None
    debug_val: bool = False

    i = 0
    new_argv: List[str] = []
    while i < len(argv):
        a = argv[i]

        if a == "--out":
            if i + 1 >= len(argv):
                raise ValueError("Missing value for --out")
            out_val = argv[i + 1]
            i += 2
            continue

        if a.startswith("--out="):
            out_val = a.split("=", 1)[1]
            i += 1
            continue

        if a == "--debug":
            debug_val = True
            i += 1
            continue

        new_argv.append(a)
        i += 1

    g: Dict[str, Any] = {"out": out_val, "debug": debug_val}
    return new_argv, g


def main(argv: Optional[List[str]] = None) -> int:
    argv0 = sys.argv[1:] if argv is None else list(argv)

    parser = build_parser()

    try:
        argv1, g = _extract_global_flags(argv0)

        args = parser.parse_args(argv1)

        # Apply extracted globals (if provided)
        if g.get("out") is not None:
            args.out = g["out"]
        if g.get("debug") is True:
            args.debug = True

        if args.family == "lens":
            if args.lens_cmd == "list":
                out = {"schema": "xkid.LensList.v1", "lenses": lens_list()}
                res = ok_result(cmd=CMD_LENS_LIST, input_={}, output=out)
                return emit_result(res, out=args.out)

            if args.lens_cmd == "describe":
                out = lens_describe(args.name)
                res = ok_result(cmd=CMD_LENS_DESCRIBE, input_={"name": args.name}, output=out)
                return emit_result(res, out=args.out)

        if args.family == "id" and args.id_cmd == "generate":
            params = _load_params(args)
            want_struct, want_trace = _load_need_flags(args)

            # 1) Run lens first so capability errors surface cleanly (precedence invariant).
            lens_out = lens_run(
                args.lens,
                params,
                need_struct=want_struct,
                need_trace=want_trace,
            )

            # 2) Null+1 hardening: only oscillator is permitted as mount.
            if NULL_PLUS_ONE and args.lens != NULL_PLUS_ONE_MOUNT_LENS:
                raise ValueError(
                    f"Null+1: only lens '{NULL_PLUS_ONE_MOUNT_LENS}' is permitted for id.generate (got '{args.lens}')"
                )

            # 3) Option B: promote LensOutput -> IdOutput at CLI boundary.
            out: Dict[str, Any] = dict(lens_out)
            out["schema"] = SCHEMA_ID_OUTPUT

            # 4) Future-proof structure (Null+1: empty stack).
            out["mount"] = {"name": args.lens, "params": params}
            out["lens_stack"] = []

            # 5) Packet: logical artifact + wire encoding.
            xid_struct = out.get("xid_struct") or {}
            payload_hex = xid_struct.get("payload_hex")
            xid = out.get("xid")
            if isinstance(payload_hex, str) and isinstance(xid, str):
                out["packet"] = packet_v1_from_id_output(
                    xid=xid,
                    payload_hex=payload_hex,
                    codec="b32k",
                )

            res = ok_result(
                cmd=CMD_ID_GENERATE,
                input_={"lens": args.lens, "params": params},
                output=out,
            )
            return emit_result(res, out=args.out)

        if args.family == "sysop":
            if args.sysop_cmd == "challenge":
                out = make_challenge(n_bytes=int(args.bytes))
                res = ok_result(cmd="sysop.challenge", input_={"bytes": int(args.bytes)}, output=out)
                return emit_result(res, out=args.out)

            if args.sysop_cmd == "attest":
                params = _load_params(args)

                # v1: keep sysop attestation pinned to Null+1 mount.
                lens_name = getattr(args, "lens", NULL_PLUS_ONE_MOUNT_LENS)
                if NULL_PLUS_ONE and lens_name != NULL_PLUS_ONE_MOUNT_LENS:
                    raise ValueError(
                        f"Null+1: only lens '{NULL_PLUS_ONE_MOUNT_LENS}' is permitted for sysop.attest (got '{lens_name}')"
                    )

                # Always require struct for attestation (needs payload_hex).
                lens_out = lens_run(
                    lens_name,
                    params,
                    need_struct=True,
                    need_trace=False,
                )

                xid = lens_out.get("xid")
                xid_struct = lens_out.get("xid_struct") or {}
                payload_hex = xid_struct.get("payload_hex")

                if not isinstance(xid, str) or not isinstance(payload_hex, str):
                    raise ValueError("sysop.attest requires xid + xid_struct.payload_hex (struct must be available)")

                pkt = packet_v1_from_id_output(
                    xid=xid,
                    payload_hex=payload_hex,
                    codec="b32k",
                )

                # Device binding lives inside pkt["device"] (policy-driven).
                device_obj = pkt.get("device")
                if not isinstance(device_obj, dict):
                    device_obj = {"binding": "none", "present": False}

                # Enforce device policy at the trust boundary (sysop.attest).
                # Packet construction must remain total; enforcement belongs here.
                from xkid.device.policy import policy_from_env

                pol = policy_from_env()
                bp = getattr(pol, "binding_policy", "advisory")

                if bp == "none":
                    # explicit opt-out: attest without device binding
                    device_obj = {"binding": "none", "present": False}

                elif bp == "required":
                    if not bool(device_obj.get("present", False)):
                        raise ValueError("Device binding required but no device identity present")

                elif bp == "sealed":
                    if device_obj.get("binding") != "sealed":
                        raise ValueError("Sealed device binding required but provider is not sealed")

                att = sign_attestation(
                    AttestInputs(
                        challenge=str(args.challenge),
                        packet_sha256_hex=str(pkt.get("sha256_hex")),
                        packet_codec=str(pkt.get("codec")),
                        packet_b32k=str(pkt.get("b32k")),
                        device=device_obj,
                    )
                )

                out = {
                    "schema": "xkid.SysopAttestResult.v1",
                    "attestation": att,
                }
                res = ok_result(cmd="sysop.attest", input_={"challenge": args.challenge}, output=out)
                return emit_result(res, out=args.out)

            if args.sysop_cmd == "verify":
                if args.attestation:
                    att = _read_json_file(args.attestation)
                else:
                    att = json.loads(sys.stdin.read())

                report = verify_attestation(att, challenge=args.challenge)
                res = ok_result(
                    cmd="sysop.verify",
                    input_={"challenge": args.challenge, "attestation": args.attestation or "<stdin>"},
                    output=report,
                )
                return emit_result(res, out=args.out)

            if args.sysop_cmd == "revoke":
                store_path = Path(str(args.store))
                reason = getattr(args, "reason", None)

                if getattr(args, "claim", None):
                    revoke_claim_hash(store_path, str(args.claim), reason=reason)
                    which = {"kind": "claim_hash", "key": str(args.claim)}
                elif getattr(args, "cert", None):
                    revoke_cert_hash(store_path, str(args.cert), reason=reason)
                    which = {"kind": "cert_hash", "key": str(args.cert)}
                elif getattr(args, "device", None):
                    revoke_device_hash(store_path, str(args.device), reason=reason)
                    which = {"kind": "device_hash", "key": str(args.device)}
                else:
                    raise ValueError("sysop.revoke requires one of: --claim, --cert, --device")

                out = {
                    "schema": "xkid.SysopRevokeResult.v1",
                    "store": str(store_path),
                    "revoked": which,
                }
                res = ok_result(
                    cmd="sysop.revoke",
                    input_={"store": str(store_path), **which, "reason": reason},
                    output=out,
                )
                return emit_result(res, out=args.out)

            if args.sysop_cmd == "instance":
                root = Path(str(args.root))

                if args.instance_cmd == "init":
                    rec = ensure_instance(root, name=str(args.name))
                    out = {
                        "schema": "xkid.SysopInstanceInitResult.v1",
                        "instance_id": rec.instance_id,
                        "path": str(root / "instance.json"),
                    }
                    res = ok_result(
                        cmd="sysop.instance.init",
                        input_={"name": str(args.name), "root": str(root)},
                        output=out,
                    )
                    return emit_result(res, out=args.out)

                if args.instance_cmd == "whoami":
                    rec = load_instance(root)
                    out = {
                        "schema": "xkid.SysopInstanceWhoamiResult.v1",
                        "instance_id": rec.instance_id,
                    }
                    res = ok_result(
                        cmd="sysop.instance.whoami",
                        input_={"root": str(root)},
                        output=out,
                    )
                    return emit_result(res, out=args.out)

                if args.instance_cmd == "show":
                    rec = load_instance(root)
                    out = {
                        "schema": "xkid.SysopInstanceShowResult.v1",
                        "record": rec.__dict__,
                    }
                    res = ok_result(
                        cmd="sysop.instance.show",
                        input_={"root": str(root)},
                        output=out,
                    )
                    return emit_result(res, out=args.out)
        raise ValueError("Unhandled command")

    except Exception as e:
        res = err_result(
            cmd="cli.error",
            exc=e,
            debug=bool(getattr(locals().get("args", None), "debug", False)),
        )
        emit_result(res, out=getattr(locals().get("args", None), "out", "json"))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())