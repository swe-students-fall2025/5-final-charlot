"""
Multi-Agent Legal Assistant System.

Agents:
- Retriever: Document search and retrieval
- Reasoner: Logical analysis and verification
- Explainer: Plain-language translation

Orchestration via LangGraph.
"""

from .orchestrator import build_graph, run_query, format_response
from .state import AgentState

__all__ = ["build_graph", "run_query", "format_response", "AgentState"]
