from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BlockchainAnchorResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: str
    entity_id: int
    record_ref: str
    version: int
    serialization_version: int
    fingerprint: str
    transaction_hash: str | None
    block_number: int | None
    chain_id: int
    contract_address: str
    status: str
    retry_count: int
    created_at: datetime
    anchored_at: datetime | None


class BlockchainSummary(BaseModel):

    total: int
    registered: int
    pending: int
    failed: int
    medication_events: int
    ai_predictions: int
    medical_reports: int


class BlockchainAnchorPage(BaseModel):

    items: list[BlockchainAnchorResponse]
    total: int
    skip: int
    limit: int


class BlockchainVerification(BaseModel):

    anchor_id: int
    record_ref: str
    version: int
    status: str
    verified: bool | None
    message: str