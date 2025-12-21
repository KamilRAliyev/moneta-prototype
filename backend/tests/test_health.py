from fastapi.testclient import TestClient

from server.main import app  # adjust module path if your app file is different

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
