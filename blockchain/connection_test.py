import json
from pathlib import Path
from web3 import Web3

BASE_DIR = Path(__file__).resolve().parent

RPC_URL = "http://127.0.0.1:8545"

# Connect to the local Ethereum network
web3 = Web3(Web3.HTTPProvider(RPC_URL))

if not web3.is_connected():
    raise ConnectionError(
        "Unable to connect to the Hardhat blockchain"
    )

print("\n========== BLOCKCHAIN CONNECTION ==========")

print("Connected:", web3.is_connected())
print("Chain ID:", web3.eth.chain_id)
print("Latest block:", web3.eth.block_number)

# Read the deployment address
deployment_path = (
    BASE_DIR
    / "ignition"
    / "deployments"
    / "chain-31337"
    / "deployed_addresses.json"
)

with open(deployment_path, "r") as file:
    deployments = json.load(file)

contract_address = Web3.to_checksum_address(
    deployments[
        "CareLinkIntegrityModule#CareLinkIntegrity"
    ]
)

# Load the smart contract ABI
artifact_path = (
    BASE_DIR
    / "artifacts"
    / "contracts"
    / "CareLinkIntegrity.sol"
    / "CareLinkIntegrity.json"
)

with open(artifact_path, "r") as file:
    artifact = json.load(file)

abi = artifact["abi"]

# Verify deployed contract bytecode
bytecode = web3.eth.get_code(contract_address)

if not bytecode:
    raise RuntimeError(
        "No contract found at the deployment address"
    )

# Create a Python contract instance
registry = web3.eth.contract(
    address=contract_address,
    abi=abi
)

print("\n========== SMART CONTRACT ==========")

print("Contract address:", registry.address)

owner = registry.functions.owner().call()

print("Contract owner:", owner)

authorized = (
    registry.functions
    .authorizedWriters(owner)
    .call()
)

print("Owner authorized:", authorized)

print("\nPython blockchain integration successful!")