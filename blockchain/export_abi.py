import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

artifact_path = (
    BASE_DIR
    / "artifacts"
    / "contracts"
    / "CareLinkIntegrity.sol"
    / "CareLinkIntegrity.json"
)

output_path = (
    BASE_DIR
    / "abi"
    / "CareLinkIntegrity.json"
)

with open(artifact_path, "r", encoding="utf-8") as file:
    artifact = json.load(file)

output_path.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(output_path, "w", encoding="utf-8") as file:
    json.dump(artifact["abi"], file, indent=4)

print("ABI exported successfully!")
print("Location:", output_path)
print("ABI entries:", len(artifact["abi"]))