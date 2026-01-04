# ADR 0001 – Initial Architecture for Receipt-to-Money-Manager Tool

## Status
Accepted

## Date
2026-01-02

## Context

The goal is to build a personal, lightweight application that converts supermarket
receipt photos into a Money Manager–compatible TSV file.

Key constraints:
- Single user (personal use)
- Less than ~1000 unique receipt items
- Local-first deployment preferred
- Telegram used as the user interface
- Receipts only from Walmart and Sam’s Club
- Manual review is acceptable for unknown items
- No need for high availability or multi-user support

The system must:
- Accept receipt photos
- Extract item names and prices
- Map items to predefined categories/subcategories
- Allow manual resolution of unknown items
- Export data in Money Manager TSV format

## Decision

We will implement a **local, monolithic application** consisting of:

1. A **Telegram bot** using the polling method as the user interface
2. A **local backend process** responsible for OCR, parsing, mapping, and export
3. **SQLite** as the persistent storage layer
4. **Store-specific parsers** for Walmart and Sam’s Club receipts
5. A **local file-based workflow** for image storage and TSV export

The system will run entirely on the user’s local machine.

## Rationale

### Telegram Bot
- Eliminates the need to build a mobile or web UI
- Easily supports photo uploads and conversational workflows
- Polling mode works without public hosting or HTTPS
- Ideal for personal automation tools

### Local Deployment
- Maximizes privacy (receipt data never leaves the machine)
- Avoids cloud costs and operational complexity
- Suitable for a tool used by a single person

### SQLite
- Lightweight, embedded, zero-configuration database
- Sufficient for <1000 items and small session history
- Safer and more maintainable than ad-hoc JSON files
- Allows future evolution without redesign

### Store-Specific Parsing
- Receipts are limited to Walmart and Sam’s Club
- Store-specific logic is simpler and more reliable than a generic parser
- Keeps parsing logic readable and maintainable

### OCR Abstraction
- OCR is isolated behind an interface
- Allows switching between local OCR and API-based OCR in the future
- Prevents vendor lock-in

## Consequences

### Positive
- Very low operational overhead
- Easy to debug and extend
- Fast iteration cycle
- Clear separation of concerns
- Future-proof enough for modest evolution

### Negative
- Bot only works while the local machine is running
- Not suitable for multi-user or large-scale usage
- OCR accuracy depends on implementation quality

## Alternatives Considered

### JSON-based Storage
- Rejected in favor of SQLite for better consistency, querying, and evolution

### Web Application UI
- Rejected due to higher development and maintenance cost

### Telegram Webhooks
- Rejected due to HTTPS and public hosting requirements

### Generic Receipt Parsing Engine
- Rejected as unnecessary complexity given known receipt formats

## Notes

This architecture intentionally favors simplicity and maintainability over scalability.
If requirements change (multi-user, cloud hosting, additional stores), this ADR should
be revisited and superseded.
