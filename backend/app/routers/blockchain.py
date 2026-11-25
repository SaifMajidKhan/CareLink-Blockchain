from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.blockchain_anchor import BlockchainAnchor

from backend.app.schemas.blockchain import (
    BlockchainAnchorResponse,
    BlockchainSummary,
    BlockchainAnchorPage,
    BlockchainVerification
)

from backend.app.services.anchor_service import (
    validate_anchor_network
)

from blockchain.services.blockchain_service import (
    BlockchainService
)


router = APIRouter(
    prefix="/blockchain",
    tags=["Blockchain Explorer"]
)


def get_anchor_or_404(db, anchor_id):

    anchor = db.get(BlockchainAnchor, anchor_id)

    if anchor is None:
        raise HTTPException(
            status_code=404,
            detail="Blockchain anchor not found"
        )

    return anchor


@router.get("/summary", response_model=BlockchainSummary)
def blockchain_summary(
    db: Session = Depends(get_db)
):

    rows = db.execute(
        select(
            BlockchainAnchor.entity_type,
            BlockchainAnchor.status,
            func.count(BlockchainAnchor.id)
        ).group_by(
            BlockchainAnchor.entity_type,
            BlockchainAnchor.status
        )
    ).all()

    summary = {
        "total": 0,
        "registered": 0,
        "pending": 0,
        "failed": 0,
        "medication_events": 0,
        "ai_predictions": 0,
        "medical_reports": 0
    }

    entity_keys = {
        "medication_event": "medication_events",
        "ai_prediction": "ai_predictions",
        "medical_report": "medical_reports"
    }

    for entity_type, status, count in rows:

        summary["total"] += count

        if status in ("registered", "pending", "failed"):
            summary[status] += count

        key = entity_keys.get(entity_type)

        if key:
            summary[key] += count

    return summary


@router.get("/anchors", response_model=BlockchainAnchorPage)
def list_anchors(

    entity_type: Literal[
        "medication_event",
        "ai_prediction",
        "medical_report"
    ] | None = None,

    status: Literal[
        "registered",
        "pending",
        "failed"
    ] | None = None,

    search: str | None = Query(
        default=None,
        max_length=100
    ),

    skip: int = Query(default=0, ge=0),

    limit: int = Query(default=20, ge=1, le=100),

    db: Session = Depends(get_db)
):

    filters = []

    if entity_type:
        filters.append(
            BlockchainAnchor.entity_type == entity_type
        )

    if status:
        filters.append(
            BlockchainAnchor.status == status
        )

    if search and search.strip():

        value = search.strip()

        filters.append(
            or_(
                BlockchainAnchor.record_ref.icontains(
                    value, autoescape=True
                ),
                BlockchainAnchor.transaction_hash.icontains(
                    value, autoescape=True
                ),
                BlockchainAnchor.fingerprint.icontains(
                    value, autoescape=True
                )
            )
        )

    total = db.scalar(
        select(func.count(BlockchainAnchor.id))
        .where(*filters)
    )

    statement = (
        select(BlockchainAnchor)
        .where(*filters)
        .order_by(BlockchainAnchor.id.desc())
        .offset(skip)
        .limit(limit)
    )

    anchors = db.scalars(statement).all()

    return {
        "items": anchors,
        "total": total or 0,
        "skip": skip,
        "limit": limit
    }


@router.get(
    "/anchors/{anchor_id}",
    response_model=BlockchainAnchorResponse
)
def get_anchor(
    anchor_id: int,
    db: Session = Depends(get_db)
):

    return get_anchor_or_404(db, anchor_id)


@router.get(
    "/anchors/{anchor_id}/verify",
    response_model=BlockchainVerification
)
def verify_anchor(
    anchor_id: int,
    db: Session = Depends(get_db)
):

    anchor = get_anchor_or_404(db, anchor_id)

    response = {
        "anchor_id": anchor.id,
        "record_ref": anchor.record_ref,
        "version": anchor.version
    }

    try:

        service = BlockchainService()

        validate_anchor_network(service, anchor)

        result = service.verify_record(
            record_ref=anchor.record_ref,
            version=anchor.version,
            fingerprint=anchor.fingerprint
        )

        status = result["status"]

        messages = {
            "verified": "Stored fingerprint matches the smart contract",
            "mismatch": "Stored fingerprint differs from the smart contract",
            "not_registered": "Record was not found on the smart contract",
            "verification_unavailable": "Blockchain verification unavailable"
        }

        return {
            **response,
            "status": status,
            "verified": (
                True if status == "verified"
                else False if status == "mismatch"
                else None
            ),
            "message": messages.get(
                status,
                "Verification not confirmed"
            )
        }

    except Exception:

        return {
            **response,
            "status": "verification_unavailable",
            "verified": None,
            "message": "Unable to verify fingerprint on the configured blockchain"
        }