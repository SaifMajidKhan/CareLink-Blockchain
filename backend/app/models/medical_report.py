from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    CheckConstraint,
    func
)

from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class MedicalReport(Base):

    __tablename__ = "medical_reports"

    __table_args__ = (
        CheckConstraint(
            "version = 1",
            name="ck_report_version"
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

    prediction_id: Mapped[int] = mapped_column(
        ForeignKey("ai_predictions.id"),
        nullable=False,
        index=True
    )

    record_ref: Mapped[str] = mapped_column(
        String(66),
        unique=True,
        nullable=False
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )