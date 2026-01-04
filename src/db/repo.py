import json
import sqlite3
from typing import Optional, Any


class Repo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # ---------- users ----------
    def get_or_create_user(self, telegram_user_id: str, default_account: Optional[str]) -> int:
        cur = self.conn.execute(
            "SELECT id FROM users WHERE telegram_user_id = ?",
            (telegram_user_id,),
        )
        row = cur.fetchone()
        if row:
            return int(row["id"])

        self.conn.execute(
            "INSERT INTO users (telegram_user_id, default_account) VALUES (?, ?)",
            (telegram_user_id, default_account),
        )
        self.conn.commit()
        return int(self.conn.execute("SELECT last_insert_rowid()").fetchone()[0])

    def set_default_account(self, user_id: int, account: str) -> None:
        self.conn.execute("UPDATE users SET default_account = ? WHERE id = ?", (account, user_id))
        self.conn.commit()

    def get_default_account(self, user_id: int) -> Optional[str]:
        row = self.conn.execute("SELECT default_account FROM users WHERE id = ?", (user_id,)).fetchone()
        return row["default_account"] if row else None

    # ---------- mappings ----------
    def find_mapping(self, user_id: int, normalized_key: str) -> Optional[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM item_mappings WHERE user_id = ? AND normalized_key = ?",
            (user_id, normalized_key),
        ).fetchone()

    def upsert_mapping(self, user_id: int, normalized_key: str, canonical_name: str, category: str, subcategory: str) -> int:
        existing = self.find_mapping(user_id, normalized_key)
        if existing:
            self.conn.execute(
                """UPDATE item_mappings
                   SET canonical_name=?, category=?, subcategory=?, updated_at=datetime('now')
                   WHERE id=?""",
                (canonical_name, category, subcategory, existing["id"]),
            )
            self.conn.commit()
            return int(existing["id"])

        self.conn.execute(
            """INSERT INTO item_mappings (user_id, normalized_key, canonical_name, category, subcategory)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, normalized_key, canonical_name, category, subcategory),
        )
        self.conn.commit()
        return int(self.conn.execute("SELECT last_insert_rowid()").fetchone()[0])

    # ---------- receipt sessions ----------
    def create_session(self, user_id: int, account: str, receipt_date: str, image_path: str | None) -> int:
        self.conn.execute(
            """INSERT INTO receipt_sessions (user_id, account, receipt_date, status, image_path)
               VALUES (?, ?, ?, 'PROCESSING', ?)""",
            (user_id, account, receipt_date, image_path),
        )
        self.conn.commit()
        return int(self.conn.execute("SELECT last_insert_rowid()").fetchone()[0])

    def set_session_store(self, session_id: int, store: str) -> None:
        self.conn.execute(
            "UPDATE receipt_sessions SET store=?, updated_at=datetime('now') WHERE id=?",
            (store, session_id),
        )
        self.conn.commit()

    def set_session_status(self, session_id: int, status: str) -> None:
        self.conn.execute(
            "UPDATE receipt_sessions SET status=?, updated_at=datetime('now') WHERE id=?",
            (status, session_id),
        )
        self.conn.commit()

    def get_session(self, session_id: int) -> sqlite3.Row:
        row = self.conn.execute("SELECT * FROM receipt_sessions WHERE id=?", (session_id,)).fetchone()
        if not row:
            raise ValueError(f"session not found: {session_id}")
        return row

    # ---------- receipt lines ----------
    def add_line(self, session_id: int, raw_name: str, normalized_key: str, amount: float, confidence: float = 0.0) -> int:
        self.conn.execute(
            """INSERT INTO receipt_lines (session_id, raw_name, normalized_key, amount, confidence)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, raw_name, normalized_key, amount, confidence),
        )
        self.conn.commit()
        return int(self.conn.execute("SELECT last_insert_rowid()").fetchone()[0])

    def list_lines(self, session_id: int) -> list[sqlite3.Row]:
        cur = self.conn.execute(
            "SELECT * FROM receipt_lines WHERE session_id=? ORDER BY id ASC",
            (session_id,),
        )
        return list(cur.fetchall())

    def set_line_mapping(self, line_id: int, mapping_id: int) -> None:
        self.conn.execute(
            "UPDATE receipt_lines SET mapping_id=?, needs_review=0 WHERE id=?",
            (mapping_id, line_id),
        )
        self.conn.commit()

    def unresolved_lines(self, session_id: int) -> list[sqlite3.Row]:
        cur = self.conn.execute(
            "SELECT * FROM receipt_lines WHERE session_id=? AND mapping_id IS NULL ORDER BY id ASC",
            (session_id,),
        )
        return list(cur.fetchall())

    # ---------- session state ----------
    def set_state(self, session_id: int, state: dict[str, Any]) -> None:
        payload = json.dumps(state, ensure_ascii=False)
        self.conn.execute(
            """INSERT INTO session_state (session_id, state_json)
               VALUES (?, ?)
               ON CONFLICT(session_id) DO UPDATE SET state_json=excluded.state_json, updated_at=datetime('now')""",
            (session_id, payload),
        )
        self.conn.commit()

    def get_state(self, session_id: int) -> dict[str, Any]:
        row = self.conn.execute("SELECT state_json FROM session_state WHERE session_id=?", (session_id,)).fetchone()
        if not row:
            return {}
        return json.loads(row["state_json"])
