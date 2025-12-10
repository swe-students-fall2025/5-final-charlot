"""
Retriever Agent: Searches for relevant legal documents.
"""

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate


def create_retriever_agent(vector_db, llm):
    """
    Create a Retriever Agent that searches and reranks legal documents.
    """

    def retrieve(state: dict) -> dict:
        query = state["user_query"]

        if vector_db is not None:
            docs = vector_db.similarity_search(query, k=5)
            retrieved_texts = [
                f"[Document {i}] {doc.page_content[:1500]}"
                for i, doc in enumerate(docs, 1)
            ]
        else:
            retrieved_texts = ["No vector database available."]

        rerank_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a legal document retrieval specialist.
Analyze the retrieved documents and identify which are most relevant.
Return a brief summary of key findings."""),
            ("human", """Query: {query}

Documents:
{documents}

Provide:
1. Relevant documents by number
2. Brief summary of findings""")
        ])

        chain = rerank_prompt | llm
        result = chain.invoke({
            "query": query,
            "documents": "\n\n".join(retrieved_texts)
        })

        return {
            **state,
            "retrieved_documents": retrieved_texts,
            "messages": state["messages"] + [
                AIMessage(content=f"[Retriever] Found {len(retrieved_texts)} documents.\n{result.content}")
            ]
        }

    return retrieve
