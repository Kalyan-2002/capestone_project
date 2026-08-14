
from typing import Literal

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from .state import SupportState

from .llm import (
    classify_intent as llm_classify_intent,
    generate_retrieval_answer,
    generate_direct_answer
)

from .retriever import retrieve


# Node 1: classify_intent

def classify_intent_node(
    state: SupportState
) -> SupportState:
    """
    Classify incoming query as:

    policy_question
    or
    general_question
    """

    query = state["query"]

    intent = llm_classify_intent(
        query
    )

    if intent == "policy_question":

        route = "retrieve_and_answer"

    else:

        route = "direct_answer"

    return {
        **state,
        "intent": intent,
        "route": route
    }


# Node 2: retrieve_and_answer

def retrieve_and_answer_node(
    state: SupportState
) -> SupportState:
    """
    Retrieve the most relevant ChromaDB chunk and
    generate an answer.

    MOCK_LLM branching occurs inside the generation
    function.
    """

    query = state["query"]

    context, sources = retrieve(
        query
    )

    answer, confidence = (
        generate_retrieval_answer(
            query=query,
            context=context
        )
    )

    return {
        **state,
        "retrieved_context": context,
        "sources": sources,
        "answer": answer,
        "confidence": confidence
    }


# Node 3: direct_answer

def direct_answer_node(
    state: SupportState
) -> SupportState:
    """
    Handle unrelated/general questions without retrieval.
    """

    answer, confidence = (
        generate_direct_answer()
    )

    return {
        **state,
        "sources": [],
        "retrieved_context": "",
        "answer": answer,
        "confidence": confidence
    }


# Conditional routing

def route_after_classification(
    state: SupportState
) -> Literal[
    "retrieve_and_answer",
    "direct_answer"
]:

    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


# Build LangGraph

def build_graph():
    """
    Build and compile the LangGraph StateGraph.
    """

    graph = StateGraph(
        SupportState
    )

    # Required 3 nodes
    graph.add_node(
        "classify_intent",
        classify_intent_node
    )

    graph.add_node(
        "retrieve_and_answer",
        retrieve_and_answer_node
    )

    graph.add_node(
        "direct_answer",
        direct_answer_node
    )

    # Start -> classify
    graph.add_edge(
        START,
        "classify_intent"
    )

    # Conditional edge
    graph.add_conditional_edges(
        "classify_intent",
        route_after_classification,
        {
            "retrieve_and_answer":
                "retrieve_and_answer",

            "direct_answer":
                "direct_answer"
        }
    )

    # Both branches finish
    graph.add_edge(
        "retrieve_and_answer",
        END
    )

    graph.add_edge(
        "direct_answer",
        END
    )

    return graph.compile()


# Create reusable compiled graph
support_graph = build_graph()
