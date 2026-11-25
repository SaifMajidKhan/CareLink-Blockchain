# CareLink Blockchain Integration Guide

## 1. Overview

The CareLink blockchain module provides integrity verification for medication adherence records, AI predictions and PDF medical reports using salted SHA-256 fingerprints and an Ethereum smart contract.

Sensitive medical information remains off-chain. The blockchain stores opaque record references, version numbers, fingerprints and registration metadata.

## 2. Technologies

- Solidity 0.8.34
- Hardhat 3
- Viem
- Python 3.11
- Web3.py
- SHA-256
- Ethereum-compatible local development network

## 3. Installation

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r blockchain/requirements.txt

cd blockchain
npm ci
npx hardhat compile
```

Start the local blockchain in a separate terminal:

```powershell
npx hardhat node
```

Deploy the contract:

```powershell
npx hardhat ignition deploy ignition/modules/CareLinkIntegrity.ts --network localhost
```

Copy `.env.example` to `.env` and configure the deployed contract address and authorized development writer address.

Never commit private keys or the actual `.env` file.

## 4. Python Service Interface

```python
from blockchain.services.blockchain_service import (
    BlockchainService
)

from blockchain.services.hashing_service import (
    generate_record_reference,
    generate_salt,
    generate_fingerprint
)

service = BlockchainService()

record_ref = generate_record_reference()
salt = generate_salt()

record = {
    "patient_ref": "PAT-DEMO-001",
    "status": "Taken",
    "version": 1
}

fingerprint = generate_fingerprint(record, salt)

result = service.register_record_safe(
    record_ref,
    1,
    fingerprint
)
```

The backend must persist the record reference, salt, version, original versioned payload and fingerprint before attempting blockchain registration.

Registration metadata should be updated after successful confirmation.

## 5. Verification

Retrieve the current record and its original salt from the database.

```python
fingerprint = generate_fingerprint(
    current_record,
    stored_salt
)

result = service.verify_record(
    stored_record_ref,
    stored_version,
    fingerprint
)
```

Do not generate a new salt during verification.

## 6. Verification Statuses

| Status | Meaning |
|---|---|
| verified | Fingerprint matches the blockchain anchor |
| mismatch | Fingerprint differs from the registered anchor |
| not_registered | Record version has no blockchain anchor |
| verification_unavailable | Verification could not be completed |

The backend may additionally expose a pending status for records awaiting registration.

## 7. Record Versioning

The initial record must use version 1.

Legitimate corrections must create a new version with a new fingerprint and salt. The original record reference remains unchanged.

Previous versions and their salts must be preserved.

Existing blockchain versions cannot be overwritten.

## 8. AI Prediction Integration

AI predictions can be registered using the same hashing and blockchain services.

The versioned payload should include the prediction reference, risk score, risk category, model version and relevant prediction timestamp.

Blockchain verification confirms that the prediction record has not changed since registration. It does not establish whether the prediction is medically accurate.

## 9. PDF Verification

Use `ReportIntegrityService` from `blockchain.services.report_service`.

PDF fingerprints are generated from the exact binary file contents.

Persist the original report's record reference, salt and version. Uploaded reports must be verified against the corresponding stored anchor.

Re-exporting a PDF or changing its metadata can change its fingerprint.

## 10. Backend Responsibilities

- Maintain persistent off-chain records and version history.
- Securely store secret salts.
- Keep blockchain signing credentials server-side.
- Persist registration status and transaction metadata.
- Retry failed or uncertain registrations using the original reference, version and fingerprint.
- Prevent concurrent registration conflicts.
- Recover missing transaction metadata from blockchain events when necessary.
- Enforce application-level authentication and authorization.

Use a durable pending-registration queue or outbox so blockchain outages do not prevent medication records from being saved.

## 11. Frontend Responsibilities

The Angular dashboard should communicate exclusively through FastAPI.

Display verification statuses, transaction references and version history.

Never expose private keys, secret salts or unrestricted blockchain administration functions.

## 12. Testing

From the repository root:

```powershell
python -m pytest blockchain/python_tests -v
python -m blockchain.integration_demo
python -m blockchain.report_demo
python -m blockchain.retry_demo
```

Solidity tests:

```powershell
cd blockchain
npx hardhat test
```

The live integration demonstrations require a running local blockchain and a deployed contract.

## 13. Current Limitations

The Hardhat development blockchain is intended for academic demonstration. Its state normally resets when the node restarts.

The current Python service supports sequential registration and basic retry reconciliation. Production deployments require durable transaction tracking, concurrency management, stronger key management, monitoring and independent security review.

Only synthetic patient data should be used during demonstrations.

Blockchain integrity verification does not prove that the original medical information was correct or that a patient actually consumed medication.