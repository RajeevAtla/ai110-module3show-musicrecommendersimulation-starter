# Music Recommender Simulation Model Card

## 1. Model Name

**VibeFinder 1.0**

## 2. Intended Use

This system suggests songs from a small classroom catalog based on a user’s preferred genre, mood, target energy, and whether they like acoustic music. It is designed for assignment use and explanation practice, not for production recommendations or real-world personalization at scale.

## 3. How the Model Works

The recommender is a simple content-based scorer. For each song, it compares the song’s genre and mood to the user’s preferences, checks how close the song’s energy is to the target energy, and adds a smaller bonus when the song’s acousticness matches the user’s acoustic preference.

The final score is a weighted sum of those matches. Genre and mood carry the largest influence because they are the clearest signals in the starter dataset. Energy closeness acts as a soft numeric adjustment rather than a hard cutoff, so songs can still rank well if they are close to the desired vibe even when they are not exact label matches. Acoustic preference adds a smaller amount of signal to capture users who want a more acoustic or less acoustic sound.

This is a transparent rule-based approach rather than a learned model. It does not infer patterns from user history or train parameters from data.

## 4. Data

The catalog contains 10 songs in `data/songs.csv`. It includes a small mix of pop, lofi, rock, ambient, jazz, synthwave, and indie pop tracks, with moods such as happy, chill, intense, relaxed, moody, and focused.

The dataset is enough to demonstrate ranking behavior, but it is not broad. It reflects only a tiny slice of musical taste, and it does not cover many genres, cultures, languages, or listening contexts. That means the recommender can only make sensible decisions inside the narrow world represented by the catalog.

## 5. Strengths

The system works well when the user profile is close to the labels already present in the dataset. For example, a user who prefers upbeat pop with higher energy will usually get intuitive results, and a user who prefers chill lofi with higher acousticness will also see songs that fit that vibe.

The scoring rule is easy to explain. Every recommendation can be traced back to a few concrete reasons, which makes the system useful for teaching and debugging. Because the model is simple, it is also easy to test whether changes to the score affect the ranking in the expected direction.

## 6. Limitations and Bias

The biggest limitation is that the recommender only knows the features we gave it. It cannot understand lyrics, artist identity, release context, or why a listener might want variety. It also does not model sequences, playlists, or the difference between “good match” and “pleasant surprise.”

The system can over-favor the strongest labels in the catalog, especially genre and mood, because those features are direct and categorical while energy is only one numeric dimension. If one type of song is overrepresented, the recommender may repeatedly surface that type even when the user’s taste is more subtle. The acoustic preference is also coarse because it is just a boolean signal, so it cannot express degrees of acoustic interest.

In a real product, that kind of simplification could reinforce narrow listening patterns or ignore users whose preferences do not fit the most common categories.

## 7. Evaluation

I checked the recommender by running multiple user profiles and comparing the top songs to the intended vibe of each profile. The main question was whether the ranking changed in a sensible way when the genre, mood, and target energy changed.

The expected pattern was that exact genre and mood matches should rise to the top, and that energy closeness should help break ties between otherwise similar songs. That pattern showed up clearly in the actual runs:

- `High-Energy Pop` returned `Sunrise City` (5.57), `Gym Hero` (4.09), and `Rooftop Lights` (3.35).
- `Chill Lofi` returned `Library Rain` (5.64), `Midnight Coding` (5.43), and `Focus Flow` (4.01).
- `Intense Rock` returned `Storm Runner` (5.66), `Gym Hero` (3.67), and `Sunrise City` (2.00).
- An edge-case `Conflicted Taste` profile with `genre=ambient`, `mood=chill`, `energy=0.90`, and `likes_acoustic=True` returned `Spacewalk Thoughts` (4.76), `Library Rain` (2.82), and `Midnight Coding` (2.81), which showed that genre and mood labels can overpower a contradictory energy target.

I also ran a weight-change experiment. With the default scoring, the top three songs for a high-energy pop profile were `Sunrise City`, `Gym Hero`, and `Rooftop Lights`. After reducing genre weight from `2.0` to `1.0` and doubling the energy multiplier from `1.5` to `3.0`, the order changed to `Sunrise City`, `Rooftop Lights`, then `Gym Hero`. That confirmed the model is sensitive to weight choices and can shift from label-first to energy-first behavior.

The automated verification also passed: `python -m pytest -q` reported `4 passed`.

## 8. Future Work

The next improvements would be to add more songs, more genres, and more nuanced preference signals. A stronger version of the recommender could include tempo range preferences, diversity-aware ranking, and better explanation text that distinguishes the different kinds of matches more clearly.

It would also help to support more realistic taste profiles, such as allowing the user to express ranges instead of single values. Another useful step would be to combine content-based scoring with collaborative signals once there is enough data to make that reliable.

## 9. Personal Reflection

Building this recommender made it clear that recommendation quality depends heavily on feature choice and scoring design. Even a small system can feel convincing if the features are meaningful, but it is also easy to see how a few missing features can limit what the model can recommend.

The most important lesson was that “smart” recommendations are not automatically fair or complete. Human judgment still matters when selecting features, setting weights, and deciding whether a system’s output is diverse enough and honest enough for the people using it.
