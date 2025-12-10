"""
Backward-compatible wrapper for CUAD loading utilities.

The primary implementation lives in data_loader.py. This module keeps the old
import path usable for any callers that still expect utils.cuad_loader.
"""

from .data_loader import load_cuad_contracts, load_documents, chunk_text

__all__ = ["load_cuad_contracts", "load_documents", "chunk_text"]
