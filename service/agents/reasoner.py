"""
Reasoner Agent: Constructs verifiable logical connections.
"""

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate


def create_reasoner_agent(llm):
    """
    Create a Reasoner Agent that analyzes and verifies legal information.
    """

    def reason(state: dict) -> dict:
        query = state["user_query"]
        documents = state["retrieved_documents"]

        reasoning_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a legal reasoning specialist.
1. Analyze retrieved legal documents
2. Identify relevant clauses and terms
3. Construct logical chains with citations
4. Verify claims against evidence
5. Flag gaps or uncertainties

IMPORTANT: Only cite supported claims. Do NOT provide legal advice."""),
            ("human", """Query: {query}

Evidence:
{documents}

Provide:
1. Key Legal Concepts
2. Evidence with Citations
3. Logical Connections
4. Verification Status
5. Gaps/Uncertainties""")
        ])

        chain = reasoning_prompt | llm
        result = chain.invoke({
            "query": query,
            "documents": "\n\n".join(documents)
        })

        reasoning_chain = [
            step.strip() for step in result.content.split("\n") if step.strip()
        ]

        content_lower = result.content.lower()
        if "insufficient" in content_lower or "not supported" in content_lower:
            status = "INSUFFICIENT_EVIDENCE"
        elif "partially" in content_lower:
            status = "PARTIALLY_VERIFIED"
        else:
            status = "VERIFIED"

        return {
            **state,
            "reasoning_chain": reasoning_chain,
            "verification_status": status,
            "messages": state["messages"] + [
                AIMessage(content=f"[Reasoner] Status: {status}\n\n{result.content}")
            ]
        }

    return reason
