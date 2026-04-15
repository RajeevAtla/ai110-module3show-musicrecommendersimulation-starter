import csv
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Mapping, Tuple

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored_songs = [
            (song, _score_item(user, song)) for song in self.songs
        ]
        scored_songs.sort(key=lambda item: (-item[1][0], item[0].id))
        return [song for song, _ in scored_songs[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = _score_item(user, song)
        return _format_explanation(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs: List[Dict[str, Any]] = []
    with open(csv_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            songs.append(_parse_song_row(row))
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    return _score_item(user_prefs, song)

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, _format_explanation(reasons)))
    scored.sort(key=lambda item: (-item[1], _song_sort_key(item[0])))
    return scored[:k]


def _parse_song_row(row: Mapping[str, str]) -> Dict[str, Any]:
    return {
        "id": int(row["id"]),
        "title": row["title"].strip(),
        "artist": row["artist"].strip(),
        "genre": row["genre"].strip(),
        "mood": row["mood"].strip(),
        "energy": float(row["energy"]),
        "tempo_bpm": float(row["tempo_bpm"]),
        "valence": float(row["valence"]),
        "danceability": float(row["danceability"]),
        "acousticness": float(row["acousticness"]),
    }


def _canonical_song(song: Any) -> Dict[str, Any]:
    if isinstance(song, Song):
        return asdict(song)
    return dict(song)


def _canonical_user(user_prefs: Any) -> Dict[str, Any]:
    if isinstance(user_prefs, UserProfile):
        return {
            "genre": user_prefs.favorite_genre,
            "mood": user_prefs.favorite_mood,
            "energy": user_prefs.target_energy,
            "likes_acoustic": user_prefs.likes_acoustic,
        }

    genre = user_prefs.get("genre", user_prefs.get("favorite_genre", ""))
    mood = user_prefs.get("mood", user_prefs.get("favorite_mood", ""))
    energy = user_prefs.get("energy", user_prefs.get("target_energy", 0.0))
    likes_acoustic = user_prefs.get("likes_acoustic", False)
    return {
        "genre": genre,
        "mood": mood,
        "energy": float(energy),
        "likes_acoustic": bool(likes_acoustic),
    }


def _normalize(text: Any) -> str:
    return str(text).strip().lower()


def _score_item(user_prefs: Any, song: Any) -> Tuple[float, List[str]]:
    user = _canonical_user(user_prefs)
    track = _canonical_song(song)

    score = 0.0
    reasons: List[str] = []

    if user["genre"] and _normalize(user["genre"]) == _normalize(track["genre"]):
        score += 2.0
        reasons.append(f"genre match on {track['genre']}")

    if user["mood"] and _normalize(user["mood"]) == _normalize(track["mood"]):
        score += 1.5
        reasons.append(f"mood match on {track['mood']}")

    target_energy = float(user["energy"])
    song_energy = float(track["energy"])
    energy_gap = abs(target_energy - song_energy)
    energy_bonus = max(0.0, 1.0 - energy_gap) * 1.5
    score += energy_bonus
    reasons.append(
        f"energy {song_energy:.2f} is {energy_gap:.2f} away from your target {target_energy:.2f}"
    )

    acousticness = float(track["acousticness"])
    if user["likes_acoustic"]:
        acoustic_bonus = acousticness * 0.75
        score += acoustic_bonus
        reasons.append(f"higher acousticness ({acousticness:.2f}) fits your preference")
    else:
        acoustic_bonus = (1.0 - acousticness) * 0.75
        score += acoustic_bonus
        reasons.append(f"lower acousticness ({acousticness:.2f}) fits your preference")

    return round(score, 4), reasons


def _format_explanation(reasons: List[str]) -> str:
    return "; ".join(reasons) if reasons else "No strong preference matches, but the track still ranked well."


def _song_sort_key(song: Dict[str, Any]) -> Tuple[Any, ...]:
    return (song.get("title", ""), song.get("artist", ""), song.get("id", 0))
