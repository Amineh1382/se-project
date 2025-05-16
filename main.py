import telebot
from handlers import setup_handlers
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

def main():
    print("Bot is running...")
    setup_handlers(bot)
    try:
        bot.polling(none_stop=True, interval=0, timeout=60)
    except Exception as e:
        print(f"Polling error: {e}")

if __name__ == "__main__":
    main()