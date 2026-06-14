from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from deploy_samurai.schemas.verification import VerificationCheck
from deploy_samurai.services.verification.evidence import build_evidence

DEFAULT_TIMEOUT_SECONDS = 10.0
SUCCESSFUL_STATUS_RANGE = range(200, 400)


class EndpointClientLike(Protocol):
    def get(self, url: str, timeout: float = DEFAULT_TIMEOUT_SECONDS):
        pass


@dataclass(frozen=True)
class EndpointResponse:
    status_code: int
    body: str = ""


class UrlLibEndpointClient:
    def get(self, url: str, timeout: float = DEFAULT_TIMEOUT_SECONDS) -> EndpointResponse:
        request = Request(url, method="GET")
        try:
            with urlopen(request, timeout=timeout) as response:
                body = response.read(1024).decode("utf-8", errors="replace")
                return EndpointResponse(status_code=response.status, body=body)
        except HTTPError as exc:
            return EndpointResponse(status_code=exc.code, body=exc.reason)
        except URLError as exc:
            raise RuntimeError(str(exc.reason)) from exc


def build_endpoint_url(base_url: str, endpoint_path: str) -> str:
    normalized_base_url = base_url.rstrip("/") + "/"
    normalized_path = endpoint_path.lstrip("/")
    return urljoin(normalized_base_url, normalized_path)


def check_endpoint_health(
    base_url: str,
    endpoint_path: str,
    endpoint_client: EndpointClientLike | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> VerificationCheck:
    client = endpoint_client or UrlLibEndpointClient()
    url = build_endpoint_url(base_url, endpoint_path)

    try:
        response = client.get(url, timeout=timeout)
    except Exception as exc:
        detail = f"GET {url} failed: {exc}"
        return VerificationCheck(
            name=f"endpoint_smoke:{endpoint_path}",
            status="failed",
            evidence=detail,
            evidence_items=[
                build_evidence(
                    source="http.get",
                    detail=detail,
                    metadata={"url": url, "endpoint_path": endpoint_path},
                )
            ],
        )

    status_code = int(getattr(response, "status_code"))
    check_status = "passed" if status_code in SUCCESSFUL_STATUS_RANGE else "failed"
    detail = f"GET {url} returned HTTP {status_code}."
    return VerificationCheck(
        name=f"endpoint_smoke:{endpoint_path}",
        status=check_status,
        evidence=detail,
        evidence_items=[
            build_evidence(
                source="http.get",
                detail=detail,
                metadata={
                    "url": url,
                    "endpoint_path": endpoint_path,
                    "status_code": str(status_code),
                },
            )
        ],
    )
