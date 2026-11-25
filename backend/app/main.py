from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="CareLink API",
    description=(
        "AI-Based Medication Adherence Prediction "
        "and Blockchain-Powered Medical Record "
        "Integrity Verification"
    ),
    version="0.1.0"
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
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health", tags=["Health"])
def health():

    return {
        "status": "healthy",
        "service": "carelink-backend"
    }