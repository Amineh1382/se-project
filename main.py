import telebot

# توکن بات
TOKEN = "8077575525:AAEGyTaH1B1U28xRGwJLLBl10u0WllXISi8"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to Spotify Music Explorer Bot! Ready to explore some music?")

def main():
    print("Bot is running...")
    try:
        bot.polling(none_stop=True, interval=0, timeout=60)
    except Exception as e:
        print(f"Polling error: {e}")

if __name__ == "__main__":
    main()