from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    JSON,
    CheckConstraint,
    func
)

from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class AIPrediction(Base):

    __tablename__ = "ai_predictions"

    __table_args__ = (
        CheckConstraint(
            "risk_score_bps >= 0 AND risk_score_bps <= 10000",
            name="ck_prediction_risk_score"
        ),
        CheckConstraint(
            "risk_level IN ('Low', 'Medium', 'High')",
            name="ck_prediction_risk_level"
        ),
        CheckConstraint(
            "version = 1",
            name="ck_prediction_version"
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
        unique=True,
        nullable=False
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )

    input_features: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )

    risk_score_bps: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    risk_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    model_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    model_sha256: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )

    algorithm: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    dataset_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )