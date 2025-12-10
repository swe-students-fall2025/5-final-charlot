"""
Vector database operations.
"""

import os
from langchain_community.vectorstores import FAISS


def build_vectorstore(texts: list, metadatas: list, embedder):
    """Build FAISS vector store from texts."""
    return FAISS.from_texts(texts=texts, embedding=embedder, metadatas=metadatas)


def save_vectorstore(vector_db, path: str = "data/embeddings/faiss_index"):
    """Save vector store to disk."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    vector_db.save_local(path)


def load_vectorstore(path: str, embedder):
    """Load vector store from disk."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Vector store not found at {path}")
    return FAISS.load_local(path, embedder, allow_dangerous_deserialization=True)
