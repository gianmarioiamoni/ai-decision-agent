# app/domain/context/context_hash.py

import hashlib
import json
from typing import Any


def compute_context_hash(
    user_query: str,
    input_context_docs: list[Any] | None = None,
) -> str:
    payload = {
        "query": user_query,
        "context": input_context_docs or [],
    }

    serialized = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
