import hashlib
from pathlib import Path

from blockchain.services.hashing_service import (
    generate_record_reference,
    generate_salt
)

from blockchain.services.blockchain_service import (
    BlockchainService
)


def generate_file_fingerprint(
    file_path: str | Path,
    salt: str
) -> str:

    salt_bytes = bytes.fromhex(salt)

    if len(salt_bytes) != 32:
        raise ValueError("Salt must contain 32 bytes")

    hasher = hashlib.sha256()

    hasher.update(b"CareLink:PDF:v1:")
    hasher.update(salt_bytes)

    with open(file_path, "rb") as file:

        while chunk := file.read(65536):
            hasher.update(chunk)

    return "0x" + hasher.hexdigest()


class ReportIntegrityService:

    def __init__(
        self,
        blockchain: BlockchainService
    ):
        self.blockchain = blockchain

    def register_report(
        self,
        file_path: str | Path
    ) -> dict:

        record_ref = generate_record_reference()
        salt = generate_salt()

        fingerprint = generate_file_fingerprint(
            file_path,
            salt
        )

        registration = self.blockchain.register_record(
            record_ref,
            1,
            fingerprint
        )

        return {
            **registration,
            "salt": salt,
            "file_name": Path(file_path).name,
            "serialization_version": 1
        }

    def verify_report(
        self,
        file_path: str | Path,
        record_ref: str,
        salt: str,
        version: int = 1
    ) -> dict:

        fingerprint = generate_file_fingerprint(
            file_path,
            salt
        )

        return self.blockchain.verify_record(
            record_ref,
            version,
            fingerprint
        )