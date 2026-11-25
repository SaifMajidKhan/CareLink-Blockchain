from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.routers.patients import router as patients_router
from backend.app.routers.medications import router as medications_router
from backend.app.routers import predictions
from backend.app.routers import reports
from backend.app.routers import blockchain

from backend.app.core.database import (
    check_database_connection
)

from blockchain.services.blockchain_service import (
    BlockchainService
)


app = FastAPI(
    title="CareLink API",
    description=(
        "AI-Based Medication Adherence Prediction "
        "and Blockchain-Powered Medical Record "
        "Integrity Verification"
    ),
    version="0.2.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/", tags=["General"])
def root():

    return {
        "application": "CareLink",
        "message": "Welcome to CareLink API",
        "version": "0.2.0",
        "status": "running"
    }


@app.get("/health", tags=["Health"])
def health():

    return {
        "status": "healthy",
        "service": "carelink-backend"
    }


@app.get("/health/database", tags=["Health"])
def database_health():

    connected = check_database_connection()

    return JSONResponse(
        status_code=200 if connected else 503,
        content={
            "service": "postgresql",
            "connected": connected,
            "status": (
                "healthy"
                if connected
                else "unavailable"
            )
        }
    )


@app.get("/health/blockchain", tags=["Health"])
def blockchain_health():

    try:

        service = BlockchainService()

        authorized = service.is_writer_authorized()

        return JSONResponse(
            status_code=200 if authorized else 503,
            content={
                "service": "ethereum",
                "connected": True,
                "chain_id": service.web3.eth.chain_id,
                "contract_address": service.contract_address,
                "writer_authorized": authorized,
                "status": (
                    "healthy"
                    if authorized
                    else "writer_unauthorized"
                )
            }
        )

    except Exception:

        return JSONResponse(
            status_code=503,
            content={
                "service": "ethereum",
                "connected": False,
                "status": "unavailable"
            }
        )
    
app.include_router(patients_router)
app.include_router(medications_router)
app.include_router(predictions.router)
app.include_router(reports.router)
app.include_router(blockchain.router)