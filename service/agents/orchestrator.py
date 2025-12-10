"""
Multi-Agent Orchestrator using LangGraph.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END

from .state import AgentState
from .retriever import create_retriever_agent
from .reasoner import create_reasoner_agent
from .explainer import create_explainer_agent


def build_graph(vector_db=None, model_name="gpt-4o-mini", temperature=0):
    """
    Build the multi-agent workflow graph.

    Flow: Retriever -> Reasoner -> Explainer
    """
    llm = ChatOpenAI(model=model_name, temperature=temperature)

    retriever = create_retriever_agent(vector_db, llm)
    reasoner = create_reasoner_agent(llm)
    explainer = create_explainer_agent(llm)

    workflow = StateGraph(AgentState)

    workflow.add_node("retriever", retriever)
    workflow.add_node("reasoner", reasoner)
    workflow.add_node("explainer", explainer)

    workflow.set_entry_point("retriever")
    workflow.add_edge("retriever", "reasoner")
    workflow.add_edge("reasoner", "explainer")
    workflow.add_edge("explainer", END)

    return workflow.compile()


def run_query(app, query: str) -> dict:
    """Run a query through the multi-agent system."""
    initial_state = {
        "user_query": query,
        "retrieved_documents": [],
        "reasoning_chain": [],
        "verification_status": "",
        "final_explanation": "",
        "messages": [HumanMessage(content=query)]
    }
    return app.invoke(initial_state)


def format_response(state: dict) -> str:
    """Format the response for display."""
    lines = [
        "=" * 60,
        "LEGAL ASSISTANT ANALYSIS",
        "=" * 60,
        f"\nQUESTION: {state['user_query']}\n",
        f"DOCUMENTS: Found {len(state['retrieved_documents'])} relevant documents\n",
        f"STATUS: {state['verification_status']}\n",
        "EXPLANATION:",
        "-" * 60,
        state["final_explanation"],
        "=" * 60
    ]
    return "\n".join(lines)
