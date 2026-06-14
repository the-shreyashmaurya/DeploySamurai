from __future__ import annotations

import json
from typing import Protocol

from deploy_samurai.schemas.architecture import ArchitectureReasoningResponse
from deploy_samurai.schemas.normalized_repo import NormalizedRepoMetadata


class ArchitectureSummaryProvider(Protocol):
    def summarize(
        self,
        metadata: NormalizedRepoMetadata,
        response: ArchitectureReasoningResponse,
    ) -> str:
        pass


class OpenAIArchitectureSummaryProvider:
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: int = 30,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    def summarize(
        self,
        metadata: NormalizedRepoMetadata,
        response: ArchitectureReasoningResponse,
    ) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key, timeout=self.timeout_seconds)
        prompt = _summary_prompt(metadata, response)
        result = client.responses.create(
            model=self.model,
            input=prompt,
            temperature=0.2,
        )
        text = getattr(result, "output_text", "").strip()
        return text or response.summary


def create_openai_summary_provider() -> OpenAIArchitectureSummaryProvider | None:
    from deploy_samurai.core.config import settings

    if not settings.openai_api_key or not settings.openai_model:
        return None

    return OpenAIArchitectureSummaryProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        timeout_seconds=settings.openai_timeout_seconds,
    )


def _summary_prompt(
    metadata: NormalizedRepoMetadata,
    response: ArchitectureReasoningResponse,
) -> str:
    payload = {
        "repo_metadata": metadata.model_dump(),
        "validated_architecture": response.model_dump(by_alias=True),
    }
    return (
        "Write a concise architecture recommendation summary for DeploySamurai. "
        "Do not add new services, resources, or flows. Only summarize the validated JSON.\n\n"
        f"{json.dumps(payload, indent=2)}"
    )
