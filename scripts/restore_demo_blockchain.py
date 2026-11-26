import argparse
import json

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import select
from web3 import Web3

from backend.app.core.database import SessionLocal
from backend.app.models.blockchain_anchor import BlockchainAnchor

from backend.app.services.anchor_service import (
    validate_anchor_network
)

from blockchain.services.blockchain_service import (
    BlockchainService
)


def main():

    parser = argparse.ArgumentParser(
        description="Restore CareLink local demo blockchain anchors"
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply recovery instead of previewing it"
    )

    args = parser.parse_args()

    service = BlockchainService()

    endpoint = urlparse(service.web3.provider.endpoint_uri)

    if (
        service.web3.eth.chain_id != 31337
        or endpoint.hostname not in ("localhost", "127.0.0.1")
    ):
        raise RuntimeError(
            "Recovery is restricted to the local demo blockchain"
        )

    if not service.is_writer_authorized():
        raise RuntimeError("Blockchain writer is not authorized")

    with SessionLocal() as db:

        if db.get_bind().url.database != "carelink_blockchain":
            raise RuntimeError("Incorrect demo database")

        anchors = db.scalars(
            select(BlockchainAnchor)
            .where(BlockchainAnchor.status == "registered")
            .order_by(
                BlockchainAnchor.record_ref,
                BlockchainAnchor.version
            )
        ).all()

        print("\n===== CARELINK DEMO RECOVERY =====")
        print(f"Database anchors: {len(anchors)}")
        print(f"Chain ID: {service.web3.eth.chain_id}")
        print(f"Contract: {service.contract_address}")

        missing = []
        existing = []

        for anchor in anchors:

            validate_anchor_network(service, anchor)

            result = service.verify_record(
                anchor.record_ref,
                anchor.version,
                anchor.fingerprint
            )

            status = result["status"]

            print(
                f"Anchor #{anchor.id} | "
                f"{anchor.entity_type} | "
                f"Version {anchor.version} | "
                f"{status}"
            )

            if status == "not_registered":
                missing.append(anchor)

            elif status == "verified":
                existing.append(anchor)

            else:
                raise RuntimeError(
                    f"Unsafe recovery state for anchor "
                    f"#{anchor.id}: {status}"
                )

        print(f"\nMissing registrations: {len(missing)}")
        print(f"Existing registrations: {len(existing)}")

        # Confirm existing registrations have valid
        # transaction evidence before skipping them.
        for anchor in existing:

            if not anchor.transaction_hash:
                raise RuntimeError(
                    f"Missing transaction evidence for #{anchor.id}"
                )

            receipt = service.web3.eth.get_transaction_receipt(
                anchor.transaction_hash
            )

            transaction = service.web3.eth.get_transaction(
                anchor.transaction_hash
            )

            function, values = (
                service.contract.decode_function_input(
                    transaction["input"]
                )
            )

            actual = list(values.values())

            if (
                receipt.status != 1
                or receipt.blockNumber != anchor.block_number
                or not transaction["to"]
                or transaction["to"].lower()
                != service.contract_address.lower()
                or function.fn_name != "registerRecord"
                or actual != [
                    Web3.to_bytes(hexstr=anchor.record_ref),
                    anchor.version,
                    Web3.to_bytes(hexstr=anchor.fingerprint)
                ]
            ):
                raise RuntimeError(
                    f"Stale transaction evidence for #{anchor.id}"
                )

        # Check that missing versions can be restored
        # sequentially before submitting transactions.
        latest_versions = {}

        for anchor in missing:

            ref = anchor.record_ref

            if ref not in latest_versions:
                latest_versions[ref] = (
                    service.get_latest_version(ref)
                )

            if anchor.version != latest_versions[ref] + 1:
                raise RuntimeError(
                    f"Version sequence conflict for #{anchor.id}"
                )

            latest_versions[ref] = anchor.version

        if not args.apply:

            print("\nPreview only. No changes were made.")
            print("Run again with --apply to restore.")
            return

        if not missing:
            print("\nAll registrations already restored.")
            return

        backup_dir = Path("backend/generated_reports")
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        backup_path = (
            backup_dir / f"anchor_backup_{timestamp}.json"
        )

        backup = [
            {
                "id": anchor.id,
                "record_ref": anchor.record_ref,
                "version": anchor.version,
                "fingerprint": anchor.fingerprint,
                "transaction_hash": anchor.transaction_hash,
                "block_number": anchor.block_number,
                "retry_count": anchor.retry_count,
                "anchored_at": (
                    anchor.anchored_at.isoformat()
                    if anchor.anchored_at else None
                )
            }
            for anchor in anchors
        ]

        backup_path.write_text(
            json.dumps(backup, indent=2),
            encoding="utf-8"
        )

        print(f"\nBackup saved: {backup_path}")

        restored = 0

        for anchor in missing:

            result = service.register_record(
                record_ref=anchor.record_ref,
                version=anchor.version,
                fingerprint=anchor.fingerprint
            )

            verification = service.verify_record(
                anchor.record_ref,
                anchor.version,
                anchor.fingerprint
            )

            if verification["verified"] is not True:
                raise RuntimeError(
                    f"Verification failed for #{anchor.id}"
                )

            record = service.get_record(
                anchor.record_ref,
                anchor.version
            )

            anchor.transaction_hash = result["transaction_hash"]
            anchor.block_number = result["block_number"]

            anchor.anchored_at = datetime.fromtimestamp(
                record["registered_at"],
                tz=timezone.utc
            )

            anchor.retry_count += 1
            anchor.last_error = None

            db.commit()

            restored += 1

            print(
                f"Restored anchor #{anchor.id} | "
                f"Block {anchor.block_number} | VERIFIED"
            )

        print("\n===== RECOVERY COMPLETE =====")
        print(f"Restored: {restored}")
        print(f"Previously verified: {len(existing)}")
        print(f"Total: {restored + len(existing)}")


if __name__ == "__main__":
    main()