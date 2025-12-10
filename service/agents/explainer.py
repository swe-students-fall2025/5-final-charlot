"""
Explainer Agent: Translates legal reasoning into plain language.
"""

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate


DISCLAIMER = """

---
**IMPORTANT DISCLAIMER**: This is educational information only, not legal advice.
Please consult a qualified attorney for specific legal matters."""


def create_explainer_agent(llm):
    """
    Create an Explainer Agent that translates legal concepts to plain language.
    """

    def explain(state: dict) -> dict:
        query = state["user_query"]
        reasoning_chain = state["reasoning_chain"]
        verification_status = state["verification_status"]

        explainer_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a legal education specialist.
Act as a TUTOR, not advisor.

Guidelines:
1. Use simple, everyday language
2. Provide analogies and examples
3. Highlight key points
4. Emphasize this is NOT legal advice
5. Encourage professional consultation"""),
            ("human", """Question: {query}

Analysis:
{reasoning}

Status: {status}

Provide:
1. Simple Explanation
2. Key Points
3. What to Watch For
4. Suggested Next Steps
5. Disclaimer""")
        ])

        chain = explainer_prompt | llm
        result = chain.invoke({
            "query": query,
            "reasoning": "\n".join(reasoning_chain),
            "status": verification_status
        })

        final_explanation = result.content + DISCLAIMER

        return {
            **state,
            "final_explanation": final_explanation,
            "messages": state["messages"] + [
                AIMessage(content=f"[Explainer]\n\n{final_explanation}")
            ]
        }

    return explain
