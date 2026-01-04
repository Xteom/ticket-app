from __future__ import annotations
import logging
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from src.db.repo import Repo
from src.ocr.ocr_engine import OCREngine
from src.bot.handlers import ReceiptService

log = logging.getLogger(__name__)


def build_app(token: str, repo: Repo, downloads_dir: Path) -> Application:
    ocr = OCREngine()
    service = ReceiptService(repo=repo, ocr=ocr, downloads_dir=downloads_dir)

    app = Application.builder().token(token).build()

    # --- Commands ---
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Send me a receipt photo. Optional: /setaccount <name>. I will return a Money Manager .tsv."
        )

    async def setaccount(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage: /setaccount Cash")
            return
        account = " ".join(context.args).strip()
        user_id = repo.get_or_create_user(str(update.effective_user.id), default_account=None)
        repo.set_default_account(user_id, account)
        await update.message.reply_text(f"Default account set to: {account}")

    async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Export last session stored in conversation (placeholder)
        await update.message.reply_text("TODO: implement /export <session_id> or export last session.")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setaccount", setaccount))
    app.add_handler(CommandHandler("export", export))

    # --- Photo handler ---
    async def on_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
        tg_user_id = str(update.effective_user.id)
        user_id = repo.get_or_create_user(tg_user_id, default_account=None)

        default_account = repo.get_default_account(user_id) or "Cash"
        # Optional: allow account override in caption like: "account=Debit"
        caption = (update.message.caption or "").strip()
        account = _parse_account_from_caption(caption) or default_account

        # Download highest resolution photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        downloads_dir.mkdir(parents=True, exist_ok=True)
        local_path = downloads_dir / f"receipt_{photo.file_id}.jpg"
        await file.download_to_drive(custom_path=str(local_path))

        await update.message.reply_text("Got it. Processing receipt...")

        try:
            result = service.process_receipt(user_id=user_id, account=account, image_path=local_path)

            if result.unknown_count > 0:
                await update.message.reply_text(
                    f"Processed. I found {result.unknown_count} unknown items.\n"
                    f"TODO: implement interactive resolution flow for session {result.session_id}."
                )
            else:
                # Export and send TSV immediately
                tsv = service.export_tsv(user_id=user_id, session_id=result.session_id)
                out_path = downloads_dir / f"money_manager_{result.session_id}.tsv"
                out_path.write_text(tsv, encoding="utf-8")
                await update.message.reply_document(document=open(out_path, "rb"), filename=out_path.name)
        except NotImplementedError as e:
            await update.message.reply_text(f"Not implemented yet: {e}")
        except Exception as e:
            log.exception("processing failed")
            await update.message.reply_text(f"Error: {e}")

    app.add_handler(MessageHandler(filters.PHOTO, on_photo))

    return app


def _parse_account_from_caption(caption: str) -> str | None:
    # very simple: look for "account=..."
    lowered = caption.lower()
    if "account=" not in lowered:
        return None
    try:
        after = caption.split("account=", 1)[1]
        return after.strip()
    except Exception:
        return None
