from pathlib import Path

import pytest

from src.recommender import Recommender, Song, UserProfile, load_songs, score_song


def make_song(
    song_id: int,
    title: str,
    genre: str,
    mood: str,
    energy: float,
    acousticness: float = 0.2,
) -> Song:
    return Song(
        id=song_id,
        title=title,
        artist="Test Artist",
        genre=genre,
        mood=mood,
        energy=energy,
        tempo_bpm=120,
        valence=0.7,
        danceability=0.8,
        acousticness=acousticness,
    )


def make_recommender() -> Recommender:
    songs = [
        make_song(1, "Best Match", "pop", "happy", 0.80),
        make_song(2, "Partial Match", "pop", "calm", 0.75),
        make_song(3, "Weak Match", "rock", "sad", 0.20),
    ]
    return Recommender(songs)


def test_load_songs_parses_csv_values(tmp_path: Path):
    csv_path = tmp_path / "songs.csv"
    csv_path.write_text(
        (
            "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness\n"
            "1,Sample Song,Sample Artist,pop,happy,0.81,124,0.90,0.77,0.12\n"
        ),
        encoding="utf-8",
    )

    songs = load_songs(str(csv_path))

    assert len(songs) == 1
    song = songs[0]
    assert song["id"] == 1
    assert isinstance(song["id"], int)
    assert song["title"] == "Sample Song"
    assert song["genre"] == "pop"
    assert song["mood"] == "happy"
    assert song["energy"] == pytest.approx(0.81)
    assert isinstance(song["tempo_bpm"], (int, float))
    assert song["tempo_bpm"] == pytest.approx(124)
    assert song["acousticness"] == pytest.approx(0.12)


def test_score_song_rewards_closer_energy_and_preferred_attributes():
    user = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
    }
    closer_match = {
        "id": 1,
        "title": "Closer Match",
        "artist": "Test Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.82,
        "tempo_bpm": 120,
        "valence": 0.7,
        "danceability": 0.8,
        "acousticness": 0.2,
    }
    farther_match = {
        "id": 2,
        "title": "Farther Match",
        "artist": "Test Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.35,
        "tempo_bpm": 120,
        "valence": 0.7,
        "danceability": 0.8,
        "acousticness": 0.2,
    }

    closer_score, closer_reasons = score_song(user, closer_match)
    farther_score, farther_reasons = score_song(user, farther_match)

    assert closer_score > farther_score
    assert isinstance(closer_reasons, list)
    assert closer_reasons
    assert any("genre" in reason.lower() or "mood" in reason.lower() for reason in closer_reasons)


def test_recommend_returns_descending_order_for_clear_match_ranking():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_recommender()

    results = rec.recommend(user, k=3)

    assert len(results) == 3
    assert [song.title for song in results] == [
        "Best Match",
        "Partial Match",
        "Weak Match",
    ]


def test_explain_recommendation_mentions_concrete_reasons():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)

    assert isinstance(explanation, str)
    assert explanation.strip()
    explanation_lower = explanation.lower()
    assert any(
        keyword in explanation_lower
        for keyword in ("genre", "mood", "energy", "pop", "happy")
    )
