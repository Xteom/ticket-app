from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src.db.repo import Repo
from src.ocr.ocr_engine import OCREngine
from src.parsing.detect_store import detect_store
from src.parsing.walmart_parser import parse_walmart
from src.parsing.sams_parser import parse_sams
from src.mapping.normalize import normalize_item_name
from src.mapping.mapper import map_or_mark_unknown
from src.export.money_manager_tsv import TSVRow, to_tsv, today_mmddyyyy


@dataclass
class ProcessResult:
    session_id: int
    unknown_count: int


class ReceiptService:
    def __init__(self, repo: Repo, ocr: OCREngine, downloads_dir: Path):
        self.repo = repo
        self.ocr = ocr
        self.downloads_dir = downloads_dir

    def process_receipt(self, user_id: int, account: str, image_path: Path) -> ProcessResult:
        receipt_date = today_mmddyyyy()
        session_id = self.repo.create_session(user_id=user_id, account=account, receipt_date=receipt_date, image_path=str(image_path))

        # OCR
        ocr_text = self.ocr.extract_text(image_path)

        # Store detect
        store = detect_store(ocr_text)
        if store:
            self.repo.set_session_store(session_id, store)

        # Parse
        if store == "WALMART":
            parsed_lines = parse_walmart(ocr_text)
        elif store == "SAMS":
            parsed_lines = parse_sams(ocr_text)
        else:
            # Placeholder: ask user store via Telegram (implement in bot layer)
            parsed_lines = []
            self.repo.set_session_status(session_id, "AWAITING_USER")
            return ProcessResult(session_id=session_id, unknown_count=0)

        # Persist lines + mapping
        for pl in parsed_lines:
            nk = normalize_item_name(pl.raw_name)
            line_id = self.repo.add_line(session_id, pl.raw_name, nk, float(pl.amount), float(pl.confidence))
            mapping_id = map_or_mark_unknown(self.repo, user_id, nk)
            if mapping_id:
                self.repo.set_line_mapping(line_id, mapping_id)

        unknown = self.repo.unresolved_lines(session_id)
        if unknown:
            self.repo.set_session_status(session_id, "AWAITING_USER")
        else:
            self.repo.set_session_status(session_id, "DONE")

        return ProcessResult(session_id=session_id, unknown_count=len(unknown))

    def export_tsv(self, user_id: int, session_id: int) -> str:
        session = self.repo.get_session(session_id)
        account = session["account"]
        date = session["receipt_date"]

        lines = self.repo.list_lines(session_id)
        rows: list[TSVRow] = []

        for line in lines:
            if line["mapping_id"] is None:
                # you can either skip or raise; for now raise
                raise ValueError("Cannot export: unresolved lines exist")

            mapping = self.repo.conn.execute(
                "SELECT category, subcategory, canonical_name FROM item_mappings WHERE id=?",
                (line["mapping_id"],),
            ).fetchone()

            rows.append(
                TSVRow(
                    date=date,
                    account=account,
                    category=mapping["category"],
                    subcategory=mapping["subcategory"],
                    note=line["raw_name"],         # NOTE = item name (your corrected rule)
                    amount=float(line["amount"]),
                )
            )

        return to_tsv(rows)

    def resolve_one_unknown(self, user_id: int, session_id: int, line_id: int, category: str, subcategory: str, canonical_name: Optional[str] = None) -> None:
        """
        Save mapping for this line's normalized key, then attach mapping to line.
        """
        line = self.repo.conn.execute("SELECT * FROM receipt_lines WHERE id=?", (line_id,)).fetchone()
        if not line:
            raise ValueError("line not found")

        nk = line["normalized_key"]
        raw_name = line["raw_name"]
        mapping_id = self.repo.upsert_mapping(
            user_id=user_id,
            normalized_key=nk,
            canonical_name=canonical_name or raw_name,
            category=category,
            subcategory=subcategory,
        )
        self.repo.set_line_mapping(line_id, mapping_id)

        # if no more unknown lines -> mark DONE
        if not self.repo.unresolved_lines(session_id):
            self.repo.set_session_status(session_id, "DONE")
