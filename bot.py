import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (если используешь локально)
load_dotenv()

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация OpenAI клиента
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Обработчик команды /start
async def start(update: Update, context):
    await update.message.reply_text(
        "Привет! Я — бот-гадалка 🔮\nНажми кнопку 'Гадать' или напиши свой вопрос, и я сделаю мистический расклад ✨"
    )

# Обработчик команды /guess
async def guess(update: Update, context):
    await update.message.reply_text(
        "Напиши свой вопрос, и я сделаю расклад ✨\n\n"
        "Пример вопросов:\n"
        "1. Что меня ждёт в ближайшем будущем?\n"
        "2. Какой путь мне выбрать?\n"
        "3. Чего мне опасаться?\n"
        "Будь конкретным в своём вопросе 🧘‍♀️"
    )

# Обработчик сообщений — делает расклад через OpenAI
async def handle_message(update: Update, context):
    question = update.message.text
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты гадалка. Отвечай мистически, как будто делаешь расклад Таро."},
                {"role": "user", "content": question}
            ],
            max_tokens=300
        )
        answer = response.choices[0].message.content.strip()
        await update.message.reply_text(f"🔮 Ответ:\n{answer}")
    except Exception as e:
        logger.error(f"Ошибка при обращении к OpenAI: {e}")
        await update.message.reply_text(f"❌ Ошибка:\n{e}")

# Запуск приложения
def main():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN or not os.getenv("OPENAI_API_KEY"):
        raise Exception("❗ Не заданы переменные TELEGRAM_TOKEN или OPENAI_API_KEY")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("guess", guess))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()

