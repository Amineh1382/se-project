import pandas as pd

def load_dataset(file_path="Spotify.csv"):
    try:
        df = pd.read_csv(file_path)
        if "artist" in df.columns:
            df["artist"] = df["artist"].astype(str).str.lower()
        numeric_cols = [
            "streams", "in_spotify_charts", "in_apple_charts", "in_deezer_charts",
            "in_shazam_charts", "danceability_%", "valence_%", "energy_%",
            "acousticness_%", "instrumentalness_%", "liveness_%", "speechiness_%"
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        print(f"Dataset loaded with {len(df)} songs")
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return pd.DataFrame()