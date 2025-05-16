from telebot import types

def main_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        ("🎵 Random Song", "random_song"),
        ("🔍 Search Song", "search_song"),
        ("😊 Find by Mood", "mood_menu"),
        ("📊 Top Charts", "top_charts")
    ]
    markup.add(*(types.InlineKeyboardButton(text, callback_data=data) for text, data in buttons))
    return markup

def mood_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    moods = [
        ("😊 Happy", "mood_happy"), ("😢 Sad", "mood_sad"),
        ("⚡ Energetic", "mood_energetic"), ("😌 Calm", "mood_calm"),
        ("🎉 Party", "mood_party"), ("🧠 Focused", "mood_focused")
    ]
    markup.add(*(types.InlineKeyboardButton(text, callback_data=data) for text, data in moods))
    markup.add(types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu"))
    return markup

def charts_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    charts = [
        ("Spotify Charts", "chart_spotify"), ("Apple Charts", "chart_apple"),
        ("Deezer Charts", "chart_deezer"), ("Shazam Charts", "chart_shazam")
    ]
    markup.add(*(types.InlineKeyboardButton(text, callback_data=data) for text, data in charts))
    markup.add(types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu"))
    return markup