from __future__ import annotations
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _ub64(s: str) -> bytes:
    pad = "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s + pad)


class Ed25519Keypair:
    """
    Deterministic Ed25519 keypair wrapper for XKID.
    Stores raw keys encoded as URL-safe base64 (no padding).
    """

    def __init__(self, sk: Ed25519PrivateKey):
        self.sk = sk
        self.vk = sk.public_key()

    @staticmethod
    def generate() -> "Ed25519Keypair":
        return Ed25519Keypair(Ed25519PrivateKey.generate())

    def secret_b64u(self) -> str:
        return _b64u(
            self.sk.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    def public_b64u(self) -> str:
        return _b64u(
            self.vk.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
        )

    @staticmethod
    def from_secret_b64u(secret: str) -> "Ed25519Keypair":
        sk = Ed25519PrivateKey.from_private_bytes(_ub64(secret))
        return Ed25519Keypair(sk)


def sign_detached(secret_b64u: str, msg: bytes) -> str:
    kp = Ed25519Keypair.from_secret_b64u(secret_b64u)
    return _b64u(kp.sk.sign(msg))


def verify_detached(public_b64u: str, msg: bytes, sig_b64u: str) -> bool:
    try:
        vk = Ed25519PublicKey.from_public_bytes(_ub64(public_b64u))
        vk.verify(_ub64(sig_b64u), msg)
        return True
    except Exception:
        return False
