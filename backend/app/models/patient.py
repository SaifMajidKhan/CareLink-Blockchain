from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    CheckConstraint,
    func
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class Patient(Base):

    __tablename__ = "patients"

    __table_args__ = (
        CheckConstraint(
            "age >= 1 AND age <= 120",
            name="ck_patient_age"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    condition: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )