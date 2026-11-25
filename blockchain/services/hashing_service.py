import hashlib
import json
import secrets


SERIALIZATION_VERSION = 1


def generate_record_reference() -> str:
    """Generate a random 32-byte record reference."""

    return "0x" + secrets.token_hex(32)


def generate_salt() -> str:
    """Generate a cryptographically secure random salt."""

    return secrets.token_hex(32)


def canonicalize_record(record: dict) -> str:
    """Convert a record into consistent JSON."""

    return json.dumps(
        record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False
    )


def generate_fingerprint(
    record: dict,
    salt: str
) -> str:
    """Generate a salted SHA-256 fingerprint."""

    salt_bytes = bytes.fromhex(salt)

    if len(salt_bytes) != 32:
        raise ValueError("Salt must contain 32 bytes")

    payload = {
        "serialization_version": SERIALIZATION_VERSION,
        "record": record
    }

    serialized = canonicalize_record(payload)

    hash_input = (
        b"CareLink:v1:"
        + salt_bytes
        + serialized.encode("utf-8")
    )

    fingerprint = hashlib.sha256(
        hash_input
    ).hexdigest()

    return "0x" + fingerprint