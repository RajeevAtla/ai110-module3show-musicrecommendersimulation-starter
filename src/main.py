"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from pathlib import Path

try:
    from .recommender import load_songs, recommend_songs
except ImportError:  # pragma: no cover - fallback for direct script execution
    from recommender import load_songs, recommend_songs


def main() -> None:
    csv_path = Path("data") / "songs.csv"
    songs = load_songs(str(csv_path))

    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "likes_acoustic": False,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"Loaded {len(songs)} songs from {csv_path}")
    print("User profile: genre=pop, mood=happy, energy=0.8, likes_acoustic=False")
    print("\nTop recommendations:\n")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']} - Score: {score:.2f}")
        print(f"   {explanation}")
        print()


if __name__ == "__main__":
    main()
