# Receipt Bot – Money Manager Import Tool

A lightweight, local-first Telegram bot that converts Walmart and Sam’s Club
receipt photos into a Money Manager–compatible TSV file.

This tool is designed for **personal use** and prioritizes simplicity, privacy,
and maintainability over scale.

---

## Features

- 📸 Upload receipt photos via Telegram
- 🧾 OCR extraction of receipt text
- 🏪 Store-specific parsing (Walmart, Sam’s Club)
- 🗂 Persistent item-to-category mapping
- 🧠 Learns from previous receipts
- 📝 Manual resolution of unknown items
- 📤 Export to Money Manager TSV format
- 🔒 Runs entirely on your local machine

---

## Non-Goals

This project intentionally does **not** aim to:
- Support multiple users
- Provide a web or mobile UI
- Handle arbitrary receipt formats
- Be always-on or cloud-hosted

---

## High-Level Architecture

