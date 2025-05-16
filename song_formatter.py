import pandas as pd

def format_song(song):
    details = [f"*{song.get('track_name', 'Unknown Track')}*"]
    if "artist" in song and pd.notna(song["artist"]):
        details.append(f"Artist: {song['artist'].title()}")
    if all(col in song for col in ["released_year", "released_month", "released_day"]):
        details.append(f"Released: {song['released_day']}/{song['released_month']}/{song['released_year']}")
    
    details.append(f"Streams: {int(song['streams']):,}" if pd.notna(song.get("streams")) else "Streams: N/A")
    for platform, col in [
        ("Spotify", "in_spotify_charts"), ("Apple", "in_apple_charts"),
        ("Deezer", "in_deezer_charts"), ("Shazam", "in_shazam_charts")
    ]:
        rank = int(song[col]) if pd.notna(song.get(col)) else 0
        details.append(f"{platform} Charts: {rank if rank > 0 else 'Not in charts'}")
    
    mood_features = []
    for feature, name in [
        ("danceability_%", "Danceability"), ("energy_%", "Energy"),
        ("valence_%", "Positivity"), ("acousticness_%", "Acousticness")
    ]:
        if pd.notna(song.get(feature)):
            mood_features.append(f"{name}: {int(song[feature])}%")
    if mood_features:
        details.append("\n*Mood Features:*")
        details.extend(mood_features)
    
    return "\n".join(details)

def generate_song_links(song):
    track = song.get("track_name", "").replace(" ", "+")
    artist = song.get("artist", "").replace(" ", "+")
    return {
        "youtube": f"https://www.youtube.com/results?search_query={track}+{artist}",
        "soundcloud": f"https://soundcloud.com/search?q={track.replace('+', '%20')}%20{artist.replace('+', '%20')}"
    }