"""
Embedding models for vector search.
"""

from langchain_huggingface import HuggingFaceEmbeddings


def get_embedder(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    """Get embedding model (defaults to a lightweight model for speed)."""
    return HuggingFaceEmbeddings(model_name=model_name)
