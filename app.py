import os
import threading
import google.generativeai as genai
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from flask import Flask

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

web_app = Flask(__name__)

@web_app.route('/')
def health_check():
    return "Bot FuyuNoKoe está online!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    web_app.run(host='0.0.0.0', port=port)

async def start(update, context):
    await update.message.reply_text('Olá! Sou o FuyuNoKoe_bot, a voz do inverno. ❄️')

async def help_command(update, context):
    await update.message.reply_text('Comandos:\n/start - Iniciar\n/help - Ajuda')

async def responder(update, context):
    user_message = update.message.text
    if update.message.from_user.is_bot:
        return

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash')
    try:
        response = model.generate_content(user_message)
        resposta_ai = response.text
    except Exception as e:
        print(f"Erro Gemini: {e}")
        resposta_ai = "Desculpa, tive um problema. Pode repetir?"

    await update.message.reply_text(resposta_ai)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    print('Bot FuyuNoKoe com Gemini rodando...')
    app.run_polling()
