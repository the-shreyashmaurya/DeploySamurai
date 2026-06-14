from __future__ import annotations

from typing import TypedDict

from deploy_samurai.schemas.architecture import ArchitectureReasoningResponse
from deploy_samurai.schemas.normalized_repo import NormalizedRepoMetadata
from deploy_samurai.services.architecture_reasoning.boundaries import (
    BoundaryHeuristicResult,
    infer_service_boundaries,
)
from deploy_samurai.services.architecture_reasoning.llm import ArchitectureSummaryProvider
from deploy_samurai.services.architecture_reasoning.topology import (
    ArchitectureTypeDecision,
    decide_architecture_type,
)


class ArchitectureReasoningState(TypedDict, total=False):
    metadata: NormalizedRepoMetadata
    boundaries: BoundaryHeuristicResult
    topology: ArchitectureTypeDecision
    response: ArchitectureReasoningResponse


def generate_architecture_summary(
    metadata: NormalizedRepoMetadata,
    summary_provider: ArchitectureSummaryProvider | None = None,
) -> ArchitectureReasoningResponse:
    graph = build_architecture_reasoning_graph(summary_provider)
    final_state = graph.invoke({"metadata": metadata})
    return final_state["response"]


def build_architecture_reasoning_graph(
    summary_provider: ArchitectureSummaryProvider | None = None,
):
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError:
        return _LinearArchitectureReasoningGraph(summary_provider)

    workflow = StateGraph(ArchitectureReasoningState)
    workflow.add_node("infer_boundaries", _infer_boundaries)
    workflow.add_node("decide_topology", _decide_topology)
    workflow.add_node("create_response", _create_response(summary_provider))

    workflow.add_edge(START, "infer_boundaries")
    workflow.add_edge("infer_boundaries", "decide_topology")
    workflow.add_edge("decide_topology", "create_response")
    workflow.add_edge("create_response", END)

    return workflow.compile()


class _LinearArchitectureReasoningGraph:
    def __init__(self, summary_provider: ArchitectureSummaryProvider | None) -> None:
        self.summary_provider = summary_provider

    def invoke(self, state: ArchitectureReasoningState) -> ArchitectureReasoningState:
        state.update(_infer_boundaries(state))
        state.update(_decide_topology(state))
        state.update(_create_response(self.summary_provider)(state))
        return state


def _infer_boundaries(state: ArchitectureReasoningState) -> ArchitectureReasoningState:
    return {"boundaries": infer_service_boundaries(state["metadata"])}


def _decide_topology(state: ArchitectureReasoningState) -> ArchitectureReasoningState:
    boundaries = state["boundaries"]
    return {
        "topology": decide_architecture_type(
            state["metadata"],
            boundaries.service_candidates,
            boundaries.communication_flows,
        )
    }


def _create_response(summary_provider: ArchitectureSummaryProvider | None):
    def create_response(state: ArchitectureReasoningState) -> ArchitectureReasoningState:
        boundaries = state["boundaries"]
        topology = state["topology"]
        response = ArchitectureReasoningResponse(
            architecture_type=topology.architecture_type,
            summary=_deterministic_summary(
                state["metadata"],
                topology,
                len(boundaries.service_candidates),
            ),
            service_candidates=boundaries.service_candidates,
            communication_flows=boundaries.communication_flows,
            notes=[*boundaries.notes, *topology.rationale],
        )

        if summary_provider is not None:
            response.summary = summary_provider.summarize(state["metadata"], response)

        return {"response": ArchitectureReasoningResponse.model_validate(response)}

    return create_response


def _deterministic_summary(
    metadata: NormalizedRepoMetadata,
    topology: ArchitectureTypeDecision,
    service_count: int,
) -> str:
    architecture_label = topology.architecture_type.replace("_", " ")
    article = "a" if topology.architecture_type == "modular_monolith" else ""
    architecture_phrase = f"{article} {architecture_label}".strip()
    return (
        f"{metadata.name} is best approached as {architecture_phrase} for now. "
        f"The analyzer found {service_count} candidate service boundary or boundaries "
        f"from the {metadata.framework} {metadata.language} repository metadata."
    )
