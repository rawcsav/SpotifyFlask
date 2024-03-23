from app.models.artist_models import Artist
from app import db


def process_artists(sp, artist_ids):
    missing_artist_ids = [artist_id for artist_id in artist_ids if not Artist.query.get(artist_id)]
    if not missing_artist_ids:
        print("All artists are already in the database.")
        return
    for i in range(0, len(missing_artist_ids), 50):  # API limit is 50 IDs per request
        batch_ids = missing_artist_ids[i : i + 50]
        artists_info = sp.artists(batch_ids)["artists"]
        Artist.from_spotify_artists(artists_info)
        db.session.commit()
    print(f"Processed {len(missing_artist_ids)} artists.")


def get_playlist_tracks(sp, playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results["items"]
    next_page = results["next"]

    while next_page:
        results = sp.next(results)
        tracks.extend(results["items"])
        next_page = results["next"]

    return tracks


def get_sp_genre_seeds(sp):
    global genre_seeds
    if "genre_seeds" not in globals():
        genre_seeds = sp.recommendation_genre_seeds()  # Assuming sp is your Spotipy client
    return genre_seeds


def get_artists_seeds(artist_counts, artist_ids, top_n=5):
    sorted_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)
    return [artist_ids[artist[0]] for artist in sorted_artists[: min(top_n, len(sorted_artists))]]


def get_genres_seeds(sp, genre_info, top_n=10):
    genre_seeds_dict = get_sp_genre_seeds(sp)
    genre_seeds = genre_seeds_dict["genres"]

    valid_genres = []
    for genre, count in sorted(genre_info.items(), key=lambda x: x[1]["count"], reverse=True)[:top_n]:
        sanitized_genre = genre.strip().lower()

        # Check for direct match
        if sanitized_genre in genre_seeds:
            valid_genres.append(sanitized_genre)
            continue

        hyphenated_genre = sanitized_genre.replace(" ", "-")
        if hyphenated_genre in genre_seeds:
            valid_genres.append(hyphenated_genre)
            continue

        spaced_genre = sanitized_genre.replace("-", " ")
        if spaced_genre in genre_seeds:
            valid_genres.append(spaced_genre)

    print(valid_genres)
    return valid_genres[:2]


def format_track_info(track):
    return {
        "trackid": track["id"],
        "artistid": track["artists"][0]["id"] if track["artists"] else None,
        "preview": track["preview_url"],
        "cover_art": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
        "artist": track["artists"][0]["name"],
        "trackName": track["name"],
        "trackUrl": track["external_urls"]["spotify"],
        "albumName": track["album"]["name"],
    }
