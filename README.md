# Music Recommender Simulation

## Project Summary

This project builds a simple content-based music recommender that ranks songs from a small catalog using song attributes and a user taste profile. The system is intentionally lightweight and explainable: it favors songs that match the user’s preferred genre and mood, then refines the ranking using how close a song’s energy is to the target energy and whether the song fits the user’s acoustic preference.

The goal is not to mimic a production recommender with collaborative filtering or large-scale personalization. The goal is to demonstrate how recommendation systems can be built from features, how a scoring rule turns those features into a ranking, and where bias and weak assumptions can show up even in a small classroom project.

## How The System Works

The recommender uses a small song catalog in `data/songs.csv`. Each song includes:

- `genre`
- `mood`
- `energy`
- `tempo_bpm`
- `valence`
- `danceability`
- `acousticness`

The user profile is similarly compact. It stores:

- a favorite genre
- a favorite mood
- a target energy value
- whether the user likes acoustic music

The ranking logic is straightforward:

1. Start with a score of zero for each song.
2. Add points when the song matches the user’s preferred genre.
3. Add points when the song matches the user’s preferred mood.
4. Add a smaller amount based on how close the song’s `energy` is to the target energy.
5. Add a bonus when the song’s `acousticness` aligns with the user’s acoustic preference.

This makes the recommender easy to explain because every score has a readable reason behind it. The highest-scoring songs are returned first, and the explanation for each result lists the matches that contributed to its score.

The implementation is intentionally content-based rather than collaborative. It does not learn from behavior logs, other users, or implicit feedback. That keeps the system transparent for the assignment and makes it easier to evaluate by hand.

## Getting Started

### Setup

This project is designed to run with Python from a local virtual environment. The setup used for this submission was a `uv`-created `.venv`.

```bash
uv venv .venv
```

Then install the dependencies into that interpreter:

```bash
uv pip install --python .\.venv\Scripts\python.exe -r requirements.txt
```

All Python commands below assume you are using that environment directly:

```bash
.venv\Scripts\python -m src.main
```

### Run The App

```bash
.venv\Scripts\python -m src.main
```

Expected output should include a short summary of the loaded catalog and a ranked list of recommended songs with explanations:

```text
Loaded 10 songs from data\songs.csv
User profile: genre=pop, mood=happy, energy=0.8, likes_acoustic=False

Top recommendations:

1. Sunrise City by Neon Echo - Score: 5.58
   genre match on pop; mood match on happy; energy 0.82 is 0.02 away from your target 0.80; lower acousticness (0.18) fits your preference

2. Gym Hero by Max Pulse - Score: 4.02
   genre match on pop; energy 0.93 is 0.13 away from your target 0.80; lower acousticness (0.05) fits your preference

3. Rooftop Lights by Indigo Parade - Score: 3.43
   mood match on happy; energy 0.76 is 0.04 away from your target 0.80; lower acousticness (0.35) fits your preference

4. Night Drive Loop by Neon Echo - Score: 2.01
   energy 0.75 is 0.05 away from your target 0.80; lower acousticness (0.22) fits your preference

5. Storm Runner by Voltline - Score: 2.01
   energy 0.91 is 0.11 away from your target 0.80; lower acousticness (0.10) fits your preference
```

### Run Tests

```bash
.venv\Scripts\python -m pytest -q
```

If you add more scoring or explanation tests, keep them in `tests/test_recommender.py` and rerun the same command.

## Experiments You Tried

I evaluated the recommender by changing the user profile and observing how the top results shifted.

- When the profile strongly favored `pop`, `happy`, and higher energy, the recommender surfaced upbeat tracks first, especially songs with strong genre and mood matches.
- When the profile moved toward `lofi`, `chill`, and lower energy, songs with softer energy and higher acousticness rose in the ranking.
- When I changed the energy target while keeping the genre and mood fixed, the order changed in a predictable way, which confirmed that energy closeness was acting as a secondary tie-breaker rather than dominating the whole score.

I also ran a weight-shift experiment. Lowering the genre weight from `2.0` to `1.0` and doubling the energy multiplier from `1.5` to `3.0` made the ranking less label-dominated. Under the default weights, the top three songs for a high-energy pop profile were `Sunrise City`, `Gym Hero`, and `Rooftop Lights`. Under the experiment weights, the order became `Sunrise City`, `Rooftop Lights`, then `Gym Hero`, because `Rooftop Lights` was closer in energy even without a genre match.

Profile results from the final implementation:

- `High-Energy Pop` (`genre=pop`, `mood=happy`, `energy=0.85`, `likes_acoustic=False`) produced `Sunrise City` (5.57), `Gym Hero` (4.09), and `Rooftop Lights` (3.35). This matched expectations because the ranking favored upbeat pop tracks with low acousticness and close energy values.
- `Chill Lofi` (`genre=lofi`, `mood=chill`, `energy=0.35`, `likes_acoustic=True`) produced `Library Rain` (5.64), `Midnight Coding` (5.43), and `Focus Flow` (4.01). This was the cleanest profile because the dataset already contains several low-energy lofi tracks with high acousticness.
- `Intense Rock` (`genre=rock`, `mood=intense`, `energy=0.90`, `likes_acoustic=False`) produced `Storm Runner` (5.66), `Gym Hero` (3.67), and `Sunrise City` (2.00). The first recommendation felt correct, while the second showed that a strong mood and energy match can outrank genre when the catalog is small.
- `Conflicted Taste` (`genre=ambient`, `mood=chill`, `energy=0.90`, `likes_acoustic=True`) produced `Spacewalk Thoughts` (4.76), `Library Rain` (2.82), and `Midnight Coding` (2.81). This edge case exposed a limitation: categorical matches on ambient and chill still beat the high-energy preference, even though the energy target conflicted with the rest of the profile.

## Limitations and Risks

This recommender is easy to understand, but it has clear limitations.

- The catalog is tiny, so rankings are constrained by only a few examples of each style.
- The scoring rule reflects the features we chose, not a broad view of musical taste.
- Genre and mood labels are simplified and can flatten songs that feel different in practice.
- The system does not know about lyrics, artist history, cultural context, or playlist flow.
- The boolean acoustic preference is coarse; it cannot express nuanced taste such as “a little acoustic, but not fully acoustic.”

These limitations matter because a real music product could overfit to the strongest available features and repeatedly push users toward a narrow slice of the catalog. Even in this small simulation, the design can favor songs that happen to fit the chosen labels well rather than songs that a human listener would actually prefer after hearing them.

## Reflection

Reading recommendation data as features made it clear how much a recommender depends on the assumptions built into its scoring rule. A simple weighted system can feel surprisingly effective when the inputs are chosen well, but the same simplicity also makes the blind spots obvious: if a feature is missing, the model cannot recover it later. That is a useful lesson because it shows how “smart” recommendations often come from careful feature design, not just from automation.

This project also made bias easier to see in concrete terms. A recommender is never neutral when it only knows a few labels and a few numeric signals. It can still be useful, but its usefulness is bounded by the catalog, the labels, and the weights chosen by the developer. That makes human judgment important both when designing the system and when deciding whether the system is good enough for a real audience.

See the completed model card for the more formal summary of the system design and evaluation.
