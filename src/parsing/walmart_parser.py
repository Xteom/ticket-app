from dataclasses import dataclass


@dataclass
class ParsedLine:
    raw_name: str
    amount: float
    confidence: float = 0.7


def parse_walmart(ocr_text: str) -> list[ParsedLine]:
    """
    Extract item lines for Walmart receipts.

    Placeholder:
    - Implement simple regex heuristics:
      - Identify lines with a price at the end
      - Exclude TOTAL/SUBTOTAL/TAX lines
    """
    raise NotImplementedError("Implement Walmart parsing logic")
