from pathlib import Path


class OCREngine:
    def __init__(self) -> None:
        # TODO: init local OCR (e.g., tesseract wrapper) or API client
        pass

    def extract_text(self, image_path: Path) -> str:
        """
        Return raw OCR text for the receipt.

        Placeholder:
        - Implement local OCR or API OCR
        - Consider returning structured blocks later (lines + coordinates)
        """
        raise NotImplementedError("Implement OCR here")
