from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_root_endpoint():

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "CareLink"
    assert data["status"] == "running"


def test_health_endpoint():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy",
        "service": "carelink-backend"
    }

def test_database_healthy(monkeypatch):

    monkeypatch.setattr(
        "backend.app.main.check_database_connection",
        lambda: True
    )

    response = client.get("/health/database")

    assert response.status_code == 200
    assert response.json()["connected"] is True


def test_database_unavailable(monkeypatch):

    monkeypatch.setattr(
        "backend.app.main.check_database_connection",
        lambda: False
    )

    response = client.get("/health/database")

    assert response.status_code == 503
    assert response.json()["connected"] is False


def test_blockchain_healthy(monkeypatch):

    from types import SimpleNamespace

    class MockBlockchainService:

        contract_address = "0x" + "1" * 40

        web3 = SimpleNamespace(
            eth=SimpleNamespace(chain_id=31337)
        )

        def is_writer_authorized(self):
            return True

    monkeypatch.setattr(
        "backend.app.main.BlockchainService",
        MockBlockchainService
    )

    response = client.get("/health/blockchain")

    assert response.status_code == 200
    assert response.json()["connected"] is True
    assert response.json()["writer_authorized"] is True
    assert response.json()["chain_id"] == 31337


def test_blockchain_unavailable(monkeypatch):

    def unavailable_service():

        raise ConnectionError(
            "Blockchain network unavailable"
        )

    monkeypatch.setattr(
        "backend.app.main.BlockchainService",
        unavailable_service
    )

    response = client.get("/health/blockchain")

    assert response.status_code == 503
    assert response.json()["connected"] is False