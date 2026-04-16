import os
import threading
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests
from flask import Flask

# ===== TOKENS (lidos das variáveis de ambiente do Render) =====
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')

# ===== Servidor Flask (para manter o bot "acordado") =====
web_app = Flask(__name__)

@web_app.route('/')
def health_check():
    return "Bot FuyuNoKoe está online!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    web_app.run(host='0.0.0.0', port=port)

# ===== Funções do Bot do Telegram =====
async def start(update, context):
    await update.message.reply_text('Olá! Sou o FuyuNoKoe_bot, a voz do inverno. ❄️\nMande qualquer mensagem e conversaremos.')

async def help_command(update, context):
    await update.message.reply_text('Comandos:\n/start - Iniciar\n/help - Ajuda\n\nPara conversar, basta digitar qualquer texto.')

async def responder(update, context):
    user_message = update.message.text
    if update.message.from_user.is_bot:
        return

    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': 'Você é o FuyuNoKoe_bot, uma IA calma e poética.'},
            {'role': 'user', 'content': user_message}
        ]
    }

    try:
        response = requests.post('https://api.deepseek.com/v1/chat/completions', headers=headers, json=data, timeout=30)
        response.raise_for_status()
        resposta_ai = response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Erro na API: {e}")
        resposta_ai = "Desculpa, tive um problema. Pode repetir?"

    await update.message.reply_text(resposta_ai)

# ===== Inicialização =====
if __name__ == '__main__':
    # Inicia o servidor Flask em uma thread separada
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Configura e inicia o bot do Telegram
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    print('Bot FuyuNoKoe com DeepSeek rodando...')
    app.run_polling()
