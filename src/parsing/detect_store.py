def detect_store(ocr_text: str) -> str | None:
    t = ocr_text.upper()
    if "WALMART" in t:
        return "WALMART"
    if "SAM'S" in t or "SAMS CLUB" in t or "SAM’S" in t:
        return "SAMS"
    return None
