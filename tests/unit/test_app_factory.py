from fastapi.testclient import TestClient

from deploy_samurai.main import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_preflight_allows_local_flutter_origin() -> None:
    client = TestClient(create_app())

    response = client.options(
        "/v1/health",
        headers={
            "Origin": "http://127.0.0.1:8077",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:8077"
