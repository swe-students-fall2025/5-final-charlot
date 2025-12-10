"""
Embedding models for vector search.
"""

from langchain_huggingface import HuggingFaceEmbeddings


def get_embedder(model_name: str = "BAAI/bge-small-en"):
    """Get embedding model (lighter default to reduce memory footprint)."""
    return HuggingFaceEmbeddings(model_name=model_name)
