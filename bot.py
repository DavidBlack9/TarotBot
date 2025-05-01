import logging
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os

# Получаем токен Telegram и API-ключ OpenAI из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Настроим логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Устанавливаем ключ API OpenAI
openai.api_key = OPENAI_API_KEY

# Функция старта
async def start(update: Update, context):
    user_name = update.effective_user.first_name
    welcome_message = f"Привет, {user_name}! Я могу помочь тебе с гаданием на Таро. Нажми на кнопку 'Гадать' и задай свой вопрос!"
    await update.message.reply_text(welcome_message)

# Функция обработки команды "Гадать"
async def guess(update: Update, context):
    await update.message.reply_text(
        "Напиши свой вопрос, и я сделаю расклад ✨\n\n"
        "Пример вопросов:\n"
        "1. Что меня ждет в будущем?\n"
        "2. Какой выбор мне сделать?\n"
        "3. Что мне делать в сложной ситуации?\n"
        "Будь конкретным в вопросе!"
    )

# Функция обработки текстовых сообщений (ответ на вопрос)
async def handle_message(update: Update, context):
    question = update.message.text
    try:
        # Отправляем запрос к ChatGPT (OpenAI)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Используем модель GPT-3.5
            messages=[
                {"role": "system", "content": "Ты гадалка. Отвечай мистически, как будто делаешь расклад карт Таро."},
                {"role": "user", "content": question}
            ],
            max_tokens=300
        )
        answer = response['choices'][0]['message']['content'].strip()
        await update.message.reply_text(f"🔮 Ответ:\n{answer}")
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        await update.message.reply_text(f"❌ Ошибка:\n{e}")

# Основная функция для настройки и запуска бота
def main():
    # Создаем приложение Telegram с токеном
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("guess", guess))

    # Обработчик всех текстовых сообщений (для вопросов)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
