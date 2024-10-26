import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import os

# Set up logging to see any errors or warnings
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! Send me a message, and I will echo it back to you.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    received_text = update.message.text
    await update.message.reply_text(f"Echo: {received_text}")

def main():
    if API_TOKEN is None:
        logger.error("API_TOKEN not found. Check your .env file.")
        return

    app = Application.builder().token(API_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("Bot started. Listening for messages...")
    app.run_polling()

if __name__ == "__main__":
    main()
