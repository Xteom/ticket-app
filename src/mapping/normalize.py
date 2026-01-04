import re
import unicodedata


def normalize_item_name(name: str) -> str:
    """
    Normalize receipt item names to stable keys for matching.

    Placeholder: tweak rules based on Walmart/Sam's formatting.
    """
    s = name.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^a-z0-9 \-\.]", "", s)  # keep it conservative
    return s.strip()
