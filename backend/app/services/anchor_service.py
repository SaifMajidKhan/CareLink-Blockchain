import os

from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session
from web3 import Web3

from backend.app.models.blockchain_anchor import (
    BlockchainAnchor
)

from blockchain.services.blockchain_service import (
    BlockchainService
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(
    PROJECT_ROOT / "blockchain" / ".env"
)


def get_blockchain_configuration():

    chain_id = int(
        os.getenv("BLOCKCHAIN_CHAIN_ID", "31337")
    )

    contract_address = os.getenv(
        "BLOCKCHAIN_CONTRACT_ADDRESS"
    )

    if not contract_address:
        raise ValueError(
            "Blockchain contract address is missing"
        )

    return {
        "chain_id": chain_id,
        "contract_address": Web3.to_checksum_address(
            contract_address
        )
    }


def find_anchor(
    db: Session,
    entity_type: str,
    entity_id: int,
    version: int
):

    statement = select(BlockchainAnchor).where(
        BlockchainAnchor.entity_type == entity_type,
        BlockchainAnchor.entity_id == entity_id,
        BlockchainAnchor.version == version
    )

    return db.scalars(statement).first()


def validate_anchor_network(
    service: BlockchainService,
    anchor: BlockchainAnchor
):

    if service.web3.eth.chain_id != anchor.chain_id:
        raise RuntimeError(
            "Anchor belongs to a different blockchain"
        )

    if (
        service.contract_address.lower()
        != anchor.contract_address.lower()
    ):
        raise RuntimeError(
            "Anchor belongs to a different contract"
        )


def submit_anchor(
    db: Session,
    anchor_id: int
):

    statement = (
        select(BlockchainAnchor)
        .where(BlockchainAnchor.id == anchor_id)
        .with_for_update()
    )

    anchor = db.scalars(statement).one()

    if anchor.status == "registered":
        db.commit()
        return anchor

    anchor.retry_count += 1

    try:

        service = BlockchainService()

        validate_anchor_network(service, anchor)

        result = service.register_record_safe(
            record_ref=anchor.record_ref,
            version=anchor.version,
            fingerprint=anchor.fingerprint
        )

        anchor.transaction_hash = (
            result.get("transaction_hash")
            or anchor.transaction_hash
        )

        anchor.block_number = (
            result.get("block_number")
            or anchor.block_number
        )

        anchor.status = "registered"

        if result.get("registered_at") is not None:
            anchor.anchored_at = datetime.fromtimestamp(
                result["registered_at"],
                tz=timezone.utc
            )
        else:
            anchor.anchored_at = datetime.now(
                timezone.utc
            )

        anchor.last_error = None

    except Exception as exc:

        anchor.status = "failed"

        anchor.last_error = type(exc).__name__

    db.commit()
    db.refresh(anchor)

    return anchor