from dataclasses import dataclass


@dataclass
class ParsedLine:
    raw_name: str
    amount: float
    confidence: float = 0.7


def parse_sams(ocr_text: str) -> list[ParsedLine]:
    """
    Extract item lines for Sam's Club receipts.

    Placeholder: implement store-specific parsing.
    """
    raise NotImplementedError("Implement Sam's parsing logic")
