"""
Data loading utilities for CUAD dataset.
"""

import json
import os
from typing import List, Dict, Tuple


def load_cuad_contracts(data_dir: str, max_contracts: int = None) -> List[Tuple[str, Dict]]:
    """
    Load CUAD contracts with metadata.

    Returns:
        List of (contract_text, metadata) tuples
    """
    cuad_path = os.path.join(data_dir, "CUADv1.json")

    if not os.path.exists(cuad_path):
        raise FileNotFoundError(f"CUAD dataset not found at {cuad_path}")

    with open(cuad_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    contracts = []
    entries = data["data"][:max_contracts] if max_contracts else data["data"]

    for entry in entries:
        title = entry["title"]

        for paragraph in entry["paragraphs"]:
            context = paragraph["context"]
            qas = paragraph["qas"]

            clause_types = set()
            for qa in qas:
                question = qa["question"]
                if "related to" in question and '"' in question:
                    clause_type = question.split('"')[1]
                    clause_types.add(clause_type)

            metadata = {
                "title": title,
                "clause_types": list(clause_types),
                "length": len(context)
            }
            contracts.append((context, metadata))

    return contracts


def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            last_period = text.rfind(".", start + chunk_size - 100, end)
            if last_period > start:
                end = last_period + 1

        chunks.append(text[start:end].strip())
        start = end - overlap

    return chunks


def load_documents(
    data_dir: str,
    max_contracts: int = 50,
    chunk_size: int = 2000
) -> Tuple[List[str], List[Dict]]:
    """
    Load and process CUAD contracts for indexing.

    Returns:
        (texts, metadatas) for vector store
    """
    print(f"Loading up to {max_contracts} contracts...")
    contracts = load_cuad_contracts(data_dir, max_contracts)

    texts = []
    metadatas = []

    for contract_text, metadata in contracts:
        chunks = chunk_text(contract_text, chunk_size)

        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append({
                "title": metadata["title"],
                "clause_types": ", ".join(metadata["clause_types"][:5]),
                "chunk_index": i,
                "total_chunks": len(chunks)
            })

    print(f"Created {len(texts)} chunks from {len(contracts)} contracts.")
    return texts, metadatas
