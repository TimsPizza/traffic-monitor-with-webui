import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_query_endpoint():
    # 测试查询接口
    response = client.post(
        "/api/query", json={"filters": [], "time_range": "last_24_hours"}
    )
    assert response.status_code == 200
    assert "data" in response.json()


def test_auth_endpoint():
    # 测试认证接口
    response = client.post(
        "/api/auth/login", json={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "token" in response.json()
