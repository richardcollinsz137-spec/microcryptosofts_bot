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

# Configure precise console state logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fetch Token from Render Environment Dashboard
BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Professional, clean greeting text sequence."""
    welcome_msg = (
        "💼 *Hello! I am Matt, your PDF Text Extraction Assistant.*\n\n"
        "Send me any PDF file (digitally generated or scanned), and I will "
        "automatically parse and extract the embedded text for you 24/7.\n\n"
        "📎 _Drop a PDF file directly into this chat to begin._"
    )
    await update.message.reply_text(text=welcome_msg, parse_mode="Markdown")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Intercepts, downloads, processes, and serves document files safely."""
    doc: Document = update.message.document
    
    # Structural Guard: Double verify payload file suffix matches PDF signature
    if not doc.file_name.lower().endswith('.pdf'):
        await update.message.reply_text("❌ Invalid input. Please attach a valid file ending with `.pdf`.")
        return

    # Notify user that processing pipeline has locked the resource
    processing_msg = await update.message.reply_text("⏳ Processing your file... Please hold on.")
    
    local_temp_path = f"temp_{doc.file_id}.pdf"
    
    try:
        # Step 1: Download binary block locally
        logger.info(f"Downloading raw stream for: {doc.file_name}")
        telegram_file = await context.bot.get_file(doc.file_id)
        await telegram_file.download_to_drive(local_temp_path)
        
        # Step 2: Extract text stream natively 
        text_payload = await asyncio.to_thread(extract_text_from_pdf, local_temp_path)
        
        # Guard Check: Handle blank layouts gracefully
        if not text_payload or not text_payload.strip():
            await processing_msg.edit_text("⚠️ Extraction finished, but no readable text layer or structures could be found in this document.")
            return

        # Step 3: Text Threshold Evaluation (If > 3500 chars, pack as text document file)
        if len(text_payload) <= 3500:
            success_template = (
                "✅ *PDF Converted Successfully*\n"
                "📊 _Here is your extracted text:_\n\n"
                f"{text_payload}"
            )
            await processing_msg.delete()
            await update.message.reply_text(text=success_template, parse_mode="Markdown")
        else:
            await processing_msg.edit_text("📦 Text too large for a standard chat message. Compiling into file...")
            
            # Formulate raw bytes stream buffer dynamically
            file_buffer = io.BytesIO(text_payload.encode('utf-8'))
            file_buffer.name = f"Extracted_{doc.file_name.rsplit('.', 1)[0]}.txt"
            
            await update.message.reply_document(
                document=file_buffer,
                caption="✅ *PDF Converted Successfully*\nYour complete extraction data is ready below."
            )
            await processing_msg.delete()

    except Exception as error:
        logger.error(f"Critical error processing workflow execution block: {str(error)}")
        await processing_msg.edit_text("❌ An unexpected tracking failure occurred while attempting to render your PDF.")
        
    finally:
        # Cleanup Disk Storage Footprint
        if os.path.exists(local_temp_path):
            os.remove(local_temp_path)

# --- Python 3.14 Native Async Bootstrapper ---
async def main_async() -> None:
    if not BOT_TOKEN:
        raise ValueError("Missing 'BOT_TOKEN' environment key assignment.")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    logger.info("Matt PDF Engine Booted. Running background polling loops natively...")
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

def main() -> None:
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
