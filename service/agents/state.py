"""
Shared state definition for the multi-agent system.
"""

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """State shared between agents in the workflow."""
    user_query: str
    retrieved_documents: list[str]
    reasoning_chain: list[str]
    verification_status: str
    final_explanation: str
    messages: Annotated[Sequence[BaseMessage], operator.add]
