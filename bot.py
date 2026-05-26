import os
import io
import logging
import asyncio
from telegram import Update, Document
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from pdf_handler import extract_text_from_pdf

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends professional onboarding instructions."""
    welcome_text = (
        "🤖 *Welcome to microcryptosofts PDF Engine!*\n\n"
        "I am configured to parse documents and extract raw text effortlessly.\n\n"
        "📥 *How to use me:*\n"
        "Simply send or forward any `.pdf` document directly into this chat window. "
        "I will detect it, run digital extraction, or perform OCR if it's scanned."
    )
    await update.message.reply_text(text=welcome_text, parse_mode="Markdown")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processes incoming documents, validates them, and routes output based on length."""
    user_document: Document = update.message.document
    
    if not user_document.file_name.lower().endswith('.pdf'):
        await update.message.reply_text("❌ Invalid file. Please submit a file with a `.pdf` extension.")
        return

    # User feedback loop initiation
    status_notification = await update.message.reply_text("⏳ Processing your file... Please hold on.")
    temporary_file_path = f"process_{user_document.file_id}.pdf"
    
    try:
        # Secure the file asset locally
        logger.info(f"Downloading {user_document.file_name} from Telegram server context...")
        telegram_system_file = await context.bot.get_file(user_document.file_id)
        await telegram_system_file.download_to_drive(temporary_file_path)
        
        # Thread isolation prevents long PDF extractions from locking up the polling loop
        extracted_payload = await asyncio.to_thread(extract_text_from_pdf, temporary_file_path)
        
        if not extracted_payload or not extracted_payload.strip():
            await status_notification.edit_text("⚠️ Conversion complete, but no text layers could be safely generated.")
            return

        # Delivery logic switch: message limits cap text responses safely around 4096 characters
        if len(extracted_payload) <= 3500:
            formatted_response = (
                "📝 *PDF Converted Successfully*\n"
                "👇 _Here is your extracted text:_\n\n"
                f"{extracted_payload}"
            )
            await status_notification.delete()
            await update.message.reply_text(text=formatted_response, parse_mode="Markdown")
        else:
            await status_notification.edit_text("📦 Processing complete. Content exceeds message length limits. Packing into text file...")
            
            memory_file = io.BytesIO(extracted_payload.encode('utf-8'))
            clean_name = user_document.file_name.rsplit('.', 1)[0]
            memory_file.name = f"Converted_{clean_name}.txt"
            
            await update.message.reply_document(
                document=memory_file,
                caption="✅ *PDF Converted Successfully*\nYour document's full raw text dataset is attached above."
            )
            await status_notification.delete()

    except Exception as workflow_error:
        logger.error(f"Critical workflow crash encountered: {str(workflow_error)}")
        await status_notification.edit_text("❌ An error occurred while attempting to render your PDF layout models.")
        
    finally:
        if os.path.exists(temporary_file_path):
            os.remove(temporary_file_path)

# --- Python 3.14+ Compliant Event Lifecycle Engine ---
async def start_polling_engine() -> None:
    if not BOT_TOKEN:
        raise ValueError("Critical System Var 'BOT_TOKEN' absent from Environment panel.")

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    logger.info("System Initializing. Polling loops active under Python 3.14 async runtime context.")
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

def main() -> None:
    asyncio.run(start_polling_engine())

if __name__ == "__main__":
    main()
