import pandas as pd

mood_categories = {
    "Happy": {"valence_%": [65, 100], "energy_%": [60, 100], "desc": "Upbeat, positive songs"},
    "Sad": {"valence_%": [0, 40], "energy_%": [0, 50], "desc": "Emotional, melancholic songs"},
    "Energetic": {"energy_%": [75, 100], "danceability_%": [60, 100], "desc": "High-energy songs"},
    "Calm": {"energy_%": [0, 40], "acousticness_%": [60, 100], "desc": "Relaxing, peaceful songs"},
    "Party": {"danceability_%": [75, 100], "energy_%": [70, 100], "desc": "Dance-worthy hits"},
    "Focused": {"instrumentalness_%": [50, 100], "speechiness_%": [0, 20], "desc": "Concentration-enhancing songs"}
}


def find_songs_by_mood(df, mood_name):
    mood = mood_categories.get(mood_name.title(), {})
    if not mood:
        return pd.DataFrame()

    filtered = df.copy()
    for feature, (min_val, max_val) in mood.get("criteria", {}).items():
        if feature in filtered.columns:
            filtered = filtered[(filtered[feature] >= min_val) & (filtered[feature] <= max_val)]

    if "streams" in filtered.columns:
        filtered = filtered.sort_values(by="streams", ascending=False)
    return filtered
