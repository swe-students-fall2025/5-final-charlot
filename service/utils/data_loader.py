"""
Data loading utilities for CUAD dataset.
"""

import json
import os
from typing import List, Dict, Tuple


def load_cuad_contracts(data_dir: str = None, max_contracts: int = None) -> List[Tuple[str, Dict]]:
    """
    Load CUAD contracts with metadata from Hugging Face or local file.

    Args:
        data_dir: Optional path to local CUADv1.json file. If None, downloads from Hugging Face.
        max_contracts: Maximum number of contracts to load

    Returns:
        List of (contract_text, metadata) tuples
    """
    # Try local file first if data_dir is provided
    if data_dir:
        cuad_path = os.path.join(data_dir, "CUADv1.json")
        if os.path.exists(cuad_path):
            print(f"Loading CUAD from local file: {cuad_path}")
            with open(cuad_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            entries = data["data"][:max_contracts] if max_contracts else data["data"]
        else:
            print(f"Local file not found at {cuad_path}, falling back to Hugging Face...")
            entries = _load_from_huggingface(max_contracts)
    else:
        print("Loading CUAD from Hugging Face...")
        entries = _load_from_huggingface(max_contracts)

    # Process entries
    contracts = []
    for entry in entries:
        title = entry["title"]

        for paragraph in entry["paragraphs"]:
            context = paragraph["context"]
            qas = paragraph.get("qas", [])

            clause_types = set()
            for qa in qas:
                question = qa.get("question", "")
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


def _load_from_huggingface(max_contracts: int | None = None) -> List[Dict]:
    """
    Load CUAD dataset from Hugging Face without executing remote code.

    Returns:
        List of contract entries in SQuAD format
    """
    try:
        from huggingface_hub import hf_hub_download

        repo_id = "theatticusproject/cuad"
        candidate_files = [
            "CUADv1.json",
            "CUAD_v1.json",
            "CUAD_v1/CUAD_v1.json",  # actual location in repo
            "train.json"
        ]
        last_error = None
        local_path = None

        print("Downloading CUAD from Hugging Face (no remote code)...")
        for filename in candidate_files:
            try:
                local_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=filename,
                    repo_type="dataset"
                )
                print(f"Downloaded {filename} from Hugging Face")
                break
            except Exception as download_error:
                last_error = download_error
                print(f"Could not download {filename}: {download_error}")

        if not local_path:
            raise RuntimeError(f"Unable to fetch CUAD files from Hugging Face: {last_error}")

        with open(local_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        entries = raw_data.get("data", [])
        if not isinstance(entries, list):
            raise RuntimeError(f"Unexpected CUAD format in {local_path}")

        if max_contracts:
            entries = entries[:max_contracts]

        print(f"Loaded {len(entries)} contracts from Hugging Face")
        return entries

    except ImportError:
        raise ImportError(
            "The 'huggingface-hub' library is required to download CUAD from Hugging Face. "
            "Install it with: pip install huggingface-hub"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Failed to load CUAD from Hugging Face: {e}")


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
