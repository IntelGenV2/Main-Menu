"""Cryptography helpers for history and direct-message encryption."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def derive_key(secret: str) -> bytes:
    """Create a Fernet key from any passphrase-like string."""
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


class CryptoBox:
    def __init__(self, secret: str) -> None:
        self._fernet = Fernet(derive_key(secret))

    def encrypt_text(self, plain: str) -> str:
        return self._fernet.encrypt(plain.encode("utf-8")).decode("utf-8")

    def decrypt_text(self, token: str) -> str:
        return self._fernet.decrypt(token.encode("utf-8")).decode("utf-8")


def generate_identity_keypair() -> tuple[str, str]:
    private_key = x25519.X25519PrivateKey.generate()
    public_key = private_key.public_key()
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return (
        base64.b64encode(private_bytes).decode("ascii"),
        base64.b64encode(public_bytes).decode("ascii"),
    )


def fingerprint_public_key(public_key_b64: str) -> str:
    pub = base64.b64decode(public_key_b64.encode("ascii"))
    return hashlib.sha256(pub).hexdigest()[:20]


def _session_key(private_key_b64: str, peer_public_key_b64: str) -> bytes:
    private_key = x25519.X25519PrivateKey.from_private_bytes(base64.b64decode(private_key_b64))
    peer_public = x25519.X25519PublicKey.from_public_bytes(base64.b64decode(peer_public_key_b64))
    shared_secret = private_key.exchange(peer_public)
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"pymessenger-direct-v1").derive(shared_secret)


def encrypt_direct_payload(private_key_b64: str, peer_public_key_b64: str, payload: dict) -> dict:
    key = _session_key(private_key_b64, peer_public_key_b64)
    nonce = os.urandom(12)
    plain = json.dumps(payload, ensure_ascii=True).encode("utf-8")
    cipher = AESGCM(key).encrypt(nonce, plain, None)
    return {
        "nonce_b64": base64.b64encode(nonce).decode("ascii"),
        "cipher_b64": base64.b64encode(cipher).decode("ascii"),
    }


def decrypt_direct_payload(private_key_b64: str, peer_public_key_b64: str, encrypted_payload: dict) -> dict:
    key = _session_key(private_key_b64, peer_public_key_b64)
    nonce = base64.b64decode(encrypted_payload["nonce_b64"])
    cipher = base64.b64decode(encrypted_payload["cipher_b64"])
    plain = AESGCM(key).decrypt(nonce, cipher, None)
    return json.loads(plain.decode("utf-8"))

