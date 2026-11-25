from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String,
    Integer,
    BigInteger,
    DateTime,
    Text,
    UniqueConstraint,
    CheckConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class BlockchainAnchor(Base):

    __tablename__ = "blockchain_anchors"

    __table_args__ = (
        UniqueConstraint(
            "entity_type",
            "entity_id",
            "version",
            name="uq_anchor_entity_version"
        ),
        UniqueConstraint(
            "chain_id",
            "contract_address",
            "record_ref",
            "version",
            name="uq_anchor_chain_record_version"
        ),
        CheckConstraint(
            "version >= 1",
            name="ck_anchor_version"
        ),
        CheckConstraint(
            "status IN ('pending', 'registered', 'failed')",
            name="ck_anchor_status"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    entity_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    record_ref: Mapped[str] = mapped_column(
        String(66),
        nullable=False
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )

    serialization_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    salt: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )

    fingerprint: Mapped[str] = mapped_column(
        String(66),
        nullable=False
    )

    transaction_hash: Mapped[Optional[str]] = mapped_column(
        String(66),
        nullable=True
    )

    block_number: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True
    )

    chain_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    contract_address: Mapped[str] = mapped_column(
        String(42),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        index=True
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    last_error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    anchored_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )