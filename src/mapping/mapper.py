from typing import Optional
from src.db.repo import Repo


def map_or_mark_unknown(repo: Repo, user_id: int, normalized_key: str) -> Optional[int]:
    """
    Return mapping_id if found else None.
    """
    row = repo.find_mapping(user_id, normalized_key)
    return int(row["id"]) if row else None
