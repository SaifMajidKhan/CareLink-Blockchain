import json
import os

from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3


BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")


class BlockchainService:

    def __init__(self):

        rpc_url = os.getenv(
            "BLOCKCHAIN_RPC_URL",
            "http://127.0.0.1:8545"
        )

        self.web3 = Web3(
            Web3.HTTPProvider(
                rpc_url,
                request_kwargs={"timeout": 15}
            )
        )

        if not self.web3.is_connected():
            raise ConnectionError(
                "Blockchain network is unavailable"
            )

        expected_chain_id = int(
            os.getenv("BLOCKCHAIN_CHAIN_ID", "31337")
        )

        if self.web3.eth.chain_id != expected_chain_id:
            raise RuntimeError(
                "Connected to incorrect blockchain network"
            )

        contract_address = os.getenv(
            "BLOCKCHAIN_CONTRACT_ADDRESS"
        )

        writer_address = os.getenv(
            "BLOCKCHAIN_WRITER_ADDRESS"
        )

        if not contract_address or not writer_address:
            raise ValueError(
                "Missing blockchain configuration"
            )

        self.contract_address = (
            Web3.to_checksum_address(contract_address)
        )

        self.writer_address = (
            Web3.to_checksum_address(writer_address)
        )

        self.private_key = os.getenv(
            "BLOCKCHAIN_PRIVATE_KEY"
        )

        abi_path = (
            BASE_DIR
            / "abi"
            / "CareLinkIntegrity.json"
        )

        with open(
            abi_path,
            "r",
            encoding="utf-8"
        ) as file:

            abi = json.load(file)

        if not self.web3.eth.get_code(
            self.contract_address
        ):
            raise RuntimeError(
                "Smart contract is not deployed"
            )

        self.contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=abi
        ) 

        if self.private_key:

            account = self.web3.eth.account.from_key(
                self.private_key
            )

            if account.address != self.writer_address:
                raise ValueError(
                    "Private key does not match writer address"
                )

    @staticmethod
    def _bytes32(value: str) -> bytes:

        raw = Web3.to_bytes(hexstr=value)

        if len(raw) != 32:
            raise ValueError(
                "Expected a 32-byte hexadecimal value"
            )

        return raw

    def is_writer_authorized(self) -> bool:

        return self.contract.functions.authorizedWriters(
            self.writer_address
        ).call()

    def register_record(
        self,
        record_ref: str,
        version: int,
        fingerprint: str
    ) -> dict:

        if not self.is_writer_authorized():
            raise PermissionError(
                "Blockchain writer is not authorized"
            )

        function = self.contract.functions.registerRecord(
            self._bytes32(record_ref),
            version,
            self._bytes32(fingerprint)
        )

        if self.private_key:

            transaction = function.build_transaction({
                "from": self.writer_address,
                "nonce": self.web3.eth.get_transaction_count(
                    self.writer_address,
                    "pending"
                ),
                "chainId": self.web3.eth.chain_id
            })

            signed = (
                self.web3.eth.account.sign_transaction(
                    transaction,
                    self.private_key
                )
            )

            tx_hash = self.web3.eth.send_raw_transaction(
                signed.raw_transaction
            )

        else:

            if self.web3.eth.chain_id != 31337:
                raise RuntimeError(
                    "Unlocked accounts are for local development only"
                )

            tx_hash = function.transact({
                "from": self.writer_address
            })

        receipt = (
            self.web3.eth.wait_for_transaction_receipt(
                tx_hash,
                timeout=60
            )
        )

        if receipt.status != 1:
            raise RuntimeError(
                "Blockchain registration failed"
            )

        return {
            "record_ref": record_ref,
            "version": version,
            "fingerprint": fingerprint,
            "transaction_hash": Web3.to_hex(tx_hash),
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed,
            "chain_id": self.web3.eth.chain_id,
            "contract_address": self.contract_address,
            "status": "registered"
        }

    def record_exists(
        self,
        record_ref: str,
        version: int
    ) -> bool:

        return self.contract.functions.recordExists(
            self._bytes32(record_ref),
            version
        ).call()

    def verify_record(
        self,
        record_ref: str,
        version: int,
        fingerprint: str
    ) -> dict:

        try:

            if not self.record_exists(
                record_ref,
                version
            ):
                return {
                    "status": "not_registered",
                    "verified": None
                }

            verified = (
                self.contract.functions.verifyRecord(
                    self._bytes32(record_ref),
                    version,
                    self._bytes32(fingerprint)
                ).call()
            )

            return {
                "status": (
                    "verified"
                    if verified
                    else "mismatch"
                ),
                "verified": verified
            }

        except Exception:

            return {
                "status": "verification_unavailable",
                "verified": None
            }

    def get_record(
        self,
        record_ref: str,
        version: int
    ) -> dict:

        record = self.contract.functions.getRecord(
            self._bytes32(record_ref),
            version
        ).call()

        return {
            "record_ref": record_ref,
            "version": version,
            "fingerprint": Web3.to_hex(record[0]),
            "registered_at": record[1],
            "registered_by": record[2],
            "exists": record[3]
        }

    def get_latest_version(
        self,
        record_ref: str
    ) -> int:

        return self.contract.functions.getLatestVersion(
            self._bytes32(record_ref)
        ).call()