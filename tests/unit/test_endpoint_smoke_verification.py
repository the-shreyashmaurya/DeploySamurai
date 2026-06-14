from dataclasses import dataclass

from deploy_samurai.services.verification.smoke import (
    build_endpoint_url,
    check_endpoint_health,
)


@dataclass
class FakeResponse:
    status_code: int


class FakeEndpointClient:
    def __init__(self, status_code: int | None = None, error: Exception | None = None) -> None:
        self.status_code = status_code
        self.error = error
        self.calls: list[tuple[str, float]] = []

    def get(self, url: str, timeout: float = 10.0) -> FakeResponse:
        self.calls.append((url, timeout))
        if self.error is not None:
            raise self.error
        assert self.status_code is not None
        return FakeResponse(status_code=self.status_code)


def test_build_endpoint_url_normalizes_slashes() -> None:
    assert build_endpoint_url("https://api.example.com/", "/health") == "https://api.example.com/health"


def test_check_endpoint_health_passes_for_success_status() -> None:
    client = FakeEndpointClient(status_code=204)

    check = check_endpoint_health("https://api.example.com", "/health", client, timeout=2.0)

    assert check.status == "passed"
    assert check.evidence == "GET https://api.example.com/health returned HTTP 204."
    assert client.calls == [("https://api.example.com/health", 2.0)]


def test_check_endpoint_health_fails_for_error_status() -> None:
    check = check_endpoint_health(
        "https://api.example.com",
        "health",
        FakeEndpointClient(status_code=503),
    )

    assert check.status == "failed"
    assert check.evidence == "GET https://api.example.com/health returned HTTP 503."


def test_check_endpoint_health_fails_when_request_errors() -> None:
    check = check_endpoint_health(
        "https://api.example.com",
        "health",
        FakeEndpointClient(error=TimeoutError("timed out")),
    )

    assert check.status == "failed"
    assert "GET https://api.example.com/health failed: timed out" == check.evidence
