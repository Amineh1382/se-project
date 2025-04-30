
print("start")

import telebot
import pandas as pd

TOKEN = "8077575525:AAGFAshSHUqVl_XFIBHsXvqdZ6bXSCMaGag"
bot = telebot.TeleBot(TOKEN)

songs_df = pd.read_csv("spotify.csv")
songs_df["artist"] = songs_df["artist"].astype(str).str.lower()
songs_df["genre"] = songs_df["genre"].astype(str).str.lower()


@bot.message_handler(commands=["artist"])
def search_by_artist(message):
    artist_name = message.text[len("/artist ") :].strip().lower()
    if not artist_name:
        bot.reply_to(message, "Please enter an artist name after /artist.")
        return

    results = songs_df[songs_df["artist"].str.contains(artist_name, na=False)]
    if not results.empty:
        response = "\n".join(
            f"{row['track_name']} by {row['artist'].title()} ({row['release_date']})"
            for _, row in results.head(10).iterrows()
        )
    else:
        response = "No songs found for this artist."

    bot.reply_to(message, response)


@bot.message_handler(commands=["genre"])
def search_by_genre(message):
    genre_name = message.text[len("/genre ") :].strip().lower()
    if not genre_name:
        bot.reply_to(message, "Please enter a genre after /genre.")
        return

    results = songs_df[songs_df["genre"].str.contains(genre_name, na=False)]
    if not results.empty:
        response = "\n".join(
            f"{row['track_name']} by {row['artist'].title()} ({row['release_date']})"
            for _, row in results.head(10).iterrows()
        )
    else:
        response = "No songs found for this genre."

    bot.reply_to(message, response)


bot.polling()

print("finish")