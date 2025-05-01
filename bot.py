import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Модель, которую будем использовать (можно поменять)
HF_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"  # Или "gpt2" — быстрее, но слабее

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот-гадалка 🔮 Напиши свой вопрос, и я сделаю расклад ✨")

async def guess(update: Update, context):
    await update.message.reply_text(
        "Напиши свой вопрос, и я сделаю расклад ✨\n\n"
        "Пример вопросов:\n"
        "1. Что меня ждёт в будущем?\n"
        "2. Какой путь мне выбрать?\n"
        "3. Что мне делать в сложной ситуации?\n"
        "Сформулируй вопрос чётко и ясно 🧘‍♀️"
    )

def call_huggingface(question: str) -> str:
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": f"Ты гадалка. Ответь мистически на вопрос: {question}"
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):
            return data[0]["generated_text"]
        else:
            return str(data)
    else:
        logger.error(f"Ошибка Hugging Face API: {response.status_code} - {response.text}")
        return f"❌ Ошибка Hugging Face API:\n{response.status_code} - {response.text}"

async def handle_message(update: Update, context):
    question = update.message.text
    try:
        answer = call_huggingface(question)
        await update.message.reply_text(f"🔮 Ответ:\n{answer}")
    except Exception as e:
        logger.error(f"Ошибка при обращении к Hugging Face: {e}")
        await update.message.reply_text(f"❌ Произошла ошибка:\n{e}")

def main():
    if not TELEGRAM_TOKEN or not HF_API_TOKEN:
        raise Exception("❗ Не заданы переменные окружения TELEGRAM_TOKEN или HF_API_TOKEN")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("guess", guess))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
