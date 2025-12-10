"""
Utility modules for the Legal Assistant.

- embeddings: Embedding models
- vectorstore: Vector database operations
- data_loader: Dataset loading and processing
"""

from .embeddings import get_embedder
from .vectorstore import build_vectorstore, save_vectorstore, load_vectorstore
from .data_loader import load_documents, chunk_text

__all__ = [
    "get_embedder",
    "build_vectorstore",
    "save_vectorstore",
    "load_vectorstore",
    "load_documents",
    "chunk_text"
]
