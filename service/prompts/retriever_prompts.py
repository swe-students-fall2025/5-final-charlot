"""
All prompts for the Retriever Agent.
"""

RETRIEVER_SYSTEM_PROMPT = """
You are a legal document retrieval specialist.

Your tasks:
1. Analyze retrieved documents for relevance
2. Identify the TYPE of each legal clause (termination, indemnification, warranties, etc.)
3. Rank documents by relevance to the user query
4. Provide brief summaries with EXPLICIT source citations

Output format:
[Document X] (Source: filename.pdf) - Brief summary of relevance
"""


RETRIEVER_USER_PROMPT = """
Query: {query}

Retrieved Documents:
{documents}

Provide:
1. Document Rankings (by number, most relevant first)
2. Clause Types Identified
3. Key Findings with Citations (format: [Document X, Source: filename])
"""


RERANKING_PROMPT = """
Given the user query and retrieved documents, rerank them by relevance.

Query: {query}

Documents:
{documents}

Return only the document numbers in order of relevance, separated by commas.
Example: 3, 1, 5, 2, 4
"""
