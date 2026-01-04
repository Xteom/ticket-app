PRAGMA foreign_keys = ON;

-- User table (even if single-user, it helps keep things clean)
CREATE TABLE IF NOT EXISTS users (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  telegram_user_id TEXT UNIQUE NOT NULL,
  default_account TEXT,
  created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Mapping from normalized item key to category/subcategory
CREATE TABLE IF NOT EXISTS item_mappings (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id         INTEGER NOT NULL,
  normalized_key  TEXT NOT NULL,      -- normalized item name used for matching
  canonical_name  TEXT NOT NULL,      -- display name / original item name
  category        TEXT NOT NULL,
  subcategory     TEXT NOT NULL,
  created_at      TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(user_id, normalized_key),
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Receipt session = one uploaded receipt image and processing lifecycle
CREATE TABLE IF NOT EXISTS receipt_sessions (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id         INTEGER NOT NULL,
  account         TEXT NOT NULL,
  store           TEXT,               -- 'WALMART' | 'SAMS' | NULL
  receipt_date    TEXT NOT NULL,      -- mm/dd/yyyy (today)
  status          TEXT NOT NULL,      -- 'PROCESSING' | 'AWAITING_USER' | 'DONE'
  image_path      TEXT,               -- local path (optional)
  created_at      TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Extracted line items from receipt OCR+parse
CREATE TABLE IF NOT EXISTS receipt_lines (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id      INTEGER NOT NULL,
  raw_name        TEXT NOT NULL,
  normalized_key  TEXT NOT NULL,
  amount          REAL NOT NULL,      -- line total price
  confidence      REAL NOT NULL DEFAULT 0.0,
  mapping_id      INTEGER,            -- nullable until resolved
  needs_review    INTEGER NOT NULL DEFAULT 0,
  created_at      TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(session_id) REFERENCES receipt_sessions(id) ON DELETE CASCADE,
  FOREIGN KEY(mapping_id) REFERENCES item_mappings(id) ON DELETE SET NULL
);

-- Simple key-value state for bot conversation per session (optional but handy)
CREATE TABLE IF NOT EXISTS session_state (
  session_id      INTEGER PRIMARY KEY,
  state_json      TEXT NOT NULL,
  updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(session_id) REFERENCES receipt_sessions(id) ON DELETE CASCADE
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_receipt_lines_session ON receipt_lines(session_id);
CREATE INDEX IF NOT EXISTS idx_item_mappings_user_key ON item_mappings(user_id, normalized_key);
