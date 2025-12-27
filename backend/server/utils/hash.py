"""Hash calculation utilities."""

import hashlib
import json
from typing import Any, Dict


def calculate_transaction_hash(row_id: int, ingested_content: Dict[str, Any]) -> str:
    """Calculate SHA-256 hash for change tracking.

    Args:
        row_id: Row index in statement file
        ingested_content: Raw row data as dictionary

    Returns:
        SHA-256 hash as hex string (64 characters)
    """
    # Normalize content by sorting keys for consistent hashing
    normalized_content = json.dumps(ingested_content, sort_keys=True)
    hash_input = f"{row_id}:{normalized_content}"
    return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
