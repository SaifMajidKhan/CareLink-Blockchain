from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    AwareDatetime
)


class MedicationCreate(BaseModel):

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

    patient_id: int = Field(gt=0)

    medication_name: str = Field(
        min_length=2,
        max_length=150
    )

    dosage: str = Field(
        min_length=1,
        max_length=100
    )

    status: Literal[
        "Taken",
        "Missed",
        "Pending"
    ]

    scheduled_at: AwareDatetime


class MedicationResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    patient_id: int
    record_ref: str
    version: int
    medication_name: str
    dosage: str
    status: str
    scheduled_at: datetime
    recorded_at: datetime


class AnchorResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    record_ref: str
    version: int
    fingerprint: str
    transaction_hash: str | None
    block_number: int | None
    chain_id: int
    contract_address: str
    status: str
    retry_count: int
    anchored_at: datetime | None


class MedicationWithAnchor(BaseModel):

    medication: MedicationResponse
    blockchain: AnchorResponse


class IntegrityResponse(BaseModel):

    medication_id: int
    record_ref: str
    version: int
    status: str
    verified: bool | None
    message: str