import telebot
import random
import pandas as pd
from data_loader import load_dataset
from song_formatter import format_song, generate_song_links
from keyboards import main_menu_keyboard, mood_menu_keyboard, charts_menu_keyboard
from mood_utils import find_songs_by_mood, mood_categories
from session_manager import session_manager
from telebot import types

songs_df = load_dataset()

def setup_handlers(bot):
    @bot.message_handler(commands=["start"])
    def start_command(message):
        bot.send_message(
            message.chat.id,
            "*Welcome to Spotify Music Explorer!*\nChoose an option:",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

    @bot.message_handler(commands=["random"])
    def random_song_command(message):
        show_random_song(bot, message.chat.id)

    @bot.message_handler(commands=["search"])
    def search_command(message):
        query = message.text[len("/search"):].strip()
        if query:
            perform_search(bot, message, query)
        else:
            bot.send_message(
                message.chat.id,
                "Enter a song or artist name:",
                reply_markup=types.ForceReply(selective=True)
            )
            bot.register_next_step_handler(message, lambda m: perform_search(bot, m, m.text.strip()))

    @bot.message_handler(commands=["mood"])
    def mood_command(message):
        bot.send_message(
            message.chat.id,
            "*Choose a Mood:*",
            parse_mode="Markdown",
            reply_markup=mood_menu_keyboard()
        )

    @bot.message_handler(commands=["charts"])
    def charts_command(message):
        bot.send_message(
            message.chat.id,
            "*Top Charts*\nSelect a platform:",
            parse_mode="Markdown",
            reply_markup=charts_menu_keyboard()
        )

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        session = session_manager.get_session(user_id)

        if call.data == "main_menu":
            bot.edit_message_text(
                "What would you like to do?",
                chat_id, call.message.message_id,
                reply_markup=main_menu_keyboard(), parse_mode="Markdown"
            )
        elif call.data == "random_song":
            show_random_song(bot, chat_id, call.message.message_id)
        elif call.data == "search_song":
            bot.edit_message_text(
                "Enter a song or artist name:",
                chat_id, call.message.message_id,
                reply_markup=types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("⬅️ Back", callback_data="main_menu")
                )
            )
            bot.register_next_step_handler(call.message, lambda m: perform_search(bot, m, m.text.strip()))
        elif call.data == "mood_menu":
            bot.edit_message_text(
                "*Choose a Mood:*",
                chat_id, call.message.message_id,
                reply_markup=mood_menu_keyboard(), parse_mode="Markdown"
            )
        elif call.data.startswith("mood_"):
            mood_name = call.data.split("_")[1].title()
            mood_songs = find_songs_by_mood(songs_df, mood_name)
            session["page"] = 0
            session["last_results"] = mood_songs
            if not mood_songs.empty:
                bot.edit_message_text(
                    f"🎵 Found {len(mood_songs)} *{mood_name}* songs\n{mood_categories[mood_name]['desc']}",
                    chat_id, call.message.message_id, parse_mode="Markdown"
                )
                display_songs_list(bot, chat_id, mood_songs, user_id, call.message.message_id)
            else:
                bot.edit_message_text(
                    f"No *{mood_name}* songs found.",
                    chat_id, call.message.message_id,
                    reply_markup=mood_menu_keyboard(), parse_mode="Markdown"
                )
        elif call.data == "top_charts":
            bot.edit_message_text(
                "*Top Charts*\nSelect a platform:",
                chat_id, call.message.message_id,
                reply_markup=charts_menu_keyboard(), parse_mode="Markdown"
            )
        elif call.data.startswith("chart_"):
            chart_type = call.data.split("_")[1]
            chart_songs = get_top_chart_songs(chart_type)
            session["page"] = 0
            session["last_results"] = chart_songs
            if not chart_songs.empty:
                bot.edit_message_text(
                    f"📊 Top *{chart_type.capitalize()} Charts*",
                    chat_id, call.message.message_id, parse_mode="Markdown"
                )
                display_songs_list(bot, chat_id, chart_songs, user_id, call.message.message_id)
            else:
                bot.edit_message_text(
                    f"No songs in *{chart_type.capitalize()} Charts*.",
                    chat_id, call.message.message_id,
                    reply_markup=charts_menu_keyboard(), parse_mode="Markdown"
                )
        elif call.data.startswith("song_"):
            song_idx = int(call.data.split("_")[1])
            song = session["last_results"].iloc[song_idx]
            markup = types.InlineKeyboardMarkup(row_width=2)
            if pd.notna(song.get("artist")):
                markup.add(types.InlineKeyboardButton("🎤 More by Artist", callback_data=f"more_artist_{song_idx}"))
            links = generate_song_links(song)
            markup.add(
                types.InlineKeyboardButton("🎥 YouTube", url=links["youtube"]),
                types.InlineKeyboardButton("🎵 SoundCloud", url=links["soundcloud"])
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back to Results", callback_data="back_to_results"),
                types.InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            )
            bot.edit_message_text(
                format_song(song), chat_id, call.message.message_id,
                reply_markup=markup, parse_mode="Markdown"
            )
        elif call.data == "back_to_results":
            if session["last_results"] is not None:
                display_songs_list(bot, chat_id, session["last_results"], user_id, call.message.message_id)
        elif call.data.startswith("more_artist_"):
            song_idx = int(call.data.split("_")[2])
            artist = session["last_results"].iloc[song_idx]["artist"]
            artist_songs = songs_df[songs_df["artist"].str.lower() == artist.lower()]
            session["page"] = 0
            session["last_results"] = artist_songs
            bot.edit_message_text(
                f"🎤 Found {len(artist_songs)} songs by *{artist.title()}*",
                chat_id, call.message.message_id, parse_mode="Markdown"
            )
            display_songs_list(bot, chat_id, artist_songs, user_id, call.message.message_id)
        elif call.data == "prev_page":
            if session["page"] > 0:
                session["page"] -= 1
                display_songs_list(bot, chat_id, session["last_results"], user_id, call.message.message_id)
        elif call.data == "next_page":
            session["page"] += 1
            display_songs_list(bot, chat_id, session["last_results"], user_id, call.message.message_id)
        
        bot.answer_callback_query(call.id)

def show_random_song(bot, chat_id, message_id=None):
    song = songs_df.sample(1).iloc[0]
    markup = types.InlineKeyboardMarkup(row_width=2)
    links = generate_song_links(song)
    markup.add(
        types.InlineKeyboardButton("🎥 YouTube", url=links["youtube"]),
        types.InlineKeyboardButton("🎵 SoundCloud", url=links["soundcloud"])
    )
    markup.add(
        types.InlineKeyboardButton("🎵 Another Random", callback_data="random_song"),
        types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu")
    )
    if message_id:
        bot.edit_message_text(
            format_song(song), chat_id, message_id,
            reply_markup=markup, parse_mode="Markdown"
        )
    else:
        bot.send_message(
            chat_id, format_song(song),
            reply_markup=markup, parse_mode="Markdown"
        )

def perform_search(bot, message, query):
    user_id = message.from_user.id
    session = session_manager.get_session(user_id)
    session["page"] = 0
    results = songs_df[
        songs_df["track_name"].str.lower().str.contains(query.lower(), na=False) |
        songs_df["artist"].str.lower().str.contains(query.lower(), na=False)
    ]
    if not results.empty:
        session["last_results"] = results
        bot.send_message(
            message.chat.id, f"🎵 Found {len(results)} songs matching *{query}*",
            parse_mode="Markdown"
        )
        display_songs_list(bot, message.chat.id, results, user_id)
    else:
        bot.send_message(
            message.chat.id, f"No songs found for *{query}*.",
            parse_mode="Markdown", reply_markup=main_menu_keyboard()
        )

def display_songs_list(bot, chat_id, songs, user_id, message_id=None, items_per_page=5):
    session = session_manager.get_session(user_id)
    page = session["page"]
    start = page * items_per_page
    end = min(start + items_per_page, len(songs))
    
    if start >= len(songs):
        session["page"] = 0
        start = 0
        end = min(items_per_page, len(songs))
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, (idx, song) in enumerate(songs.iloc[start:end].iterrows(), 1):
        track = song.get("track_name", "Unknown")
        artist = song.get("artist", "Unknown").title()
        markup.add(types.InlineKeyboardButton(
            f"{i}. {track} - {artist}"[:40] + "..." if len(f"{track} - {artist}") > 40 else f"{i}. {track} - {artist}",
            callback_data=f"song_{start + i - 1}"
        ))
    
    if len(songs) > items_per_page:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(types.InlineKeyboardButton("⬅️ Previous", callback_data="prev_page"))
        if end < len(songs):
            nav_buttons.append(types.InlineKeyboardButton("Next ➡️", callback_data="next_page"))
        if nav_buttons:
            markup.row(*nav_buttons)
    
    markup.add(types.InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu"))
    message_text = f"*Results ({start + 1}-{end} of {len(songs)}):*"
    
    if message_id:
        bot.edit_message_text(
            message_text, chat_id, message_id,
            reply_markup=markup, parse_mode="Markdown"
        )
    else:
        bot.send_message(
            chat_id, message_text,
            reply_markup=markup, parse_mode="Markdown"
        )

def get_top_chart_songs(chart_type, limit=20):
    chart_columns = {
        "spotify": "in_spotify_charts", "apple": "in_apple_charts",
        "deezer": "in_deezer_charts", "shazam": "in_shazam_charts"
    }
    col = chart_columns.get(chart_type)
    if col and col in songs_df.columns:
        return songs_df[songs_df[col] > 0].sort_values(by=col).head(limit)
    return pd.DataFrame()