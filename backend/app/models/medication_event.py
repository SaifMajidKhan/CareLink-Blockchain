from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class MedicationEvent(Base):

    __tablename__ = "medication_events"

    __table_args__ = (
        UniqueConstraint(
            "record_ref",
            "version",
            name="uq_medication_record_version"
        ),
        CheckConstraint(
            "version >= 1",
            name="ck_medication_version"
        ),
        CheckConstraint(
            "status IN ('Taken', 'Missed', 'Pending')",
            name="ck_medication_status"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    record_ref: Mapped[str] = mapped_column(
        String(66),
        nullable=False
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    medication_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    dosage: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )