"""Hash utilities shared across deliberate."""

import hashlib


def hash_task(task: str) -> str:
    """Create a stable truncated hash of a task string."""
    normalized = task[:500].lower().strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
