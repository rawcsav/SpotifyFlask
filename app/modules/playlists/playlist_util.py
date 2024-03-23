from collections import Counter
from datetime import datetime
from app import db
from app.models.artgen_models import GenreStat
from app.models.playlist_models import Playlist
from util.database_util import (
    fetch_playlist_tracks,
    add_playlist_temporal_stats,
    add_playlist_yearly_stats,
    fetch_features,
    add_playlist_feature_stats,
    add_playlist_top_artists,
    add_playlist,
    add_playlist_genre_stats,
)


def fetch_playlists(sp, user_id):
    playlists_info = []
    playlists = sp.user_playlists(user_id)

    for playlist in playlists["items"]:
        playlist_info = {
            "id": playlist["id"],
            "name": playlist["name"],
            "owner": playlist["owner"]["id"],
            "public": playlist["public"],
            "collaborative": playlist["collaborative"],
            "cover_art": playlist["images"][0]["url"] if playlist["images"] else None,
            "followers": playlist["followers"]["total"],
            "total_tracks": playlist["tracks"]["total"],
            "snapshot_id": playlist["snapshot_id"],
        }
        playlists_info.append(playlist_info)
        Playlist.from_spotify_playlist(playlist, user_id)
        db.session_commit()
    return playlists_info


def find_newest_track(tracks):
    return max(tracks, key=lambda track: track.album.release_date if track.album else datetime.min)


def find_oldest_track(tracks):
    return min(tracks, key=lambda track: track.album.release_date if track.album else datetime.max)


def tally_decades_from_tracks(tracks):
    decades = [
        (track.album.release_date.year // 10) * 10 for track in tracks if track.album and track.album.release_date
    ]
    decade_frequency = Counter(decades)
    return decade_frequency


def calculate_feature_stats(features):
    feature_stats = {}
    feature_keys = [
        "acousticness",
        "danceability",
        "energy",
        "instrumentalness",
        "liveness",
        "loudness",
        "speechiness",
        "valence",
        "tempo",
    ]
    for key in feature_keys:
        feature_stats[key] = {"avg_value": 0, "max_value": float("-inf"), "min_value": float("inf"), "total_value": 0}
    for feature in features:
        for key in feature_keys:
            value = feature.get(key, 0)
            feature_stats[key]["max_value"] = max(feature_stats[key]["max_value"], value)
            feature_stats[key]["min_value"] = min(feature_stats[key]["min_value"], value)
            feature_stats[key]["total_value"] += value
    for key in feature_keys:
        feature_stats[key]["avg_value"] = feature_stats[key]["total_value"] / len(features) if features else 0
    return feature_stats


def calc_artist_stats(tracks):
    artist_counts = {}
    for track in tracks:
        for artist in track.artists:
            if artist.id in artist_counts:
                artist_counts[artist.id] += 1
            else:
                artist_counts[artist.id] = 1
    return artist_counts


def calc_genre_stats(tracks):
    genre_counts = {}
    for track in tracks:
        for artist in track.artists:
            for genre in artist.genres:
                if genre.name in genre_counts:
                    genre_counts[genre.name] += 1
                else:
                    genre_counts[genre.name] = 1
    return genre_counts


def update_playlist_genre_stats(playlist_id):
    tracks = fetch_playlist_tracks(playlist_id)
    genre_counts = calc_genre_stats(tracks)
    update_playlist_genre_stats(playlist_id, genre_counts)
    return genre_counts


def compute_playlist_genres(genre_info):
    results = []
    genres = (
        db.session.query(GenreStat).filter(GenreStat.sim_genres.isnot(None), GenreStat.opp_genres.isnot(None)).all()
    )

    for genre_entry in genres:
        if genre_entry.genre in genre_info:
            continue

        sim_genres = genre_entry.sim_genres.split(", ")
        sim_weights = list(map(int, genre_entry.sim_weights.split(", ")))

        opp_genres = genre_entry.opp_genres.split(", ")
        opp_weights = list(map(int, genre_entry.opp_weights.split(", ")))

        sim_score = sum([genre_info.get(genre, 0) * weight for genre, weight in zip(sim_genres, sim_weights)])
        opp_score = sum([genre_info.get(genre, 0) * weight for genre, weight in zip(opp_genres, opp_weights)])

        results.append(
            {
                "genre": genre_entry.genre,
                "similarity_score": sim_score,
                "opposition_score": opp_score,
                "spotify_url": genre_entry.spotify_url,
            }
        )

    most_similar = sorted(results, key=lambda x: x["similarity_score"], reverse=True)[:10]
    most_opposite = sorted(results, key=lambda x: x["opposition_score"], reverse=True)[:10]

    return {"most_similar": most_similar, "most_opposite": most_opposite}


def calculate_playlist_weights(genre_counts):
    genre_info = {genre: data["count"] for genre, data in genre_counts.items()}
    genre_scores = compute_playlist_genres(genre_info)

    total_tracks = sum(genre_info.values())
    genre_prevalence = {genre: count / total_tracks for genre, count in genre_info.items()}

    sorted_genres = sorted(genre_prevalence.items(), key=lambda x: x[1], reverse=True)[:10]
    genre_to_stat_mapping = {}

    for genre, _ in sorted_genres:
        genre_entry = db.session.query(GenreStat).filter_by(genre=genre).first()
        if genre_entry:
            genre_to_stat_mapping[genre] = genre_entry.closest_stat_genres

    return genre_to_stat_mapping, genre_scores


def aggregate_playlist_statistics(playlist_id):
    # Fetch playlist tracks
    tracks = fetch_playlist_tracks(playlist_id)
    if not tracks:
        print("No tracks found for the playlist.")
        return

    # Temporal Stats
    newest_track = find_newest_track(tracks)
    oldest_track = find_oldest_track(tracks)
    temporal_stats = {"newest_track": newest_track, "oldest_track": oldest_track}

    # Feature Stats
    track_ids = [track.id for track in tracks if track]
    features = fetch_features(track_ids)
    feature_stats = calculate_feature_stats(features)

    # Top Artists
    artist_counts = calc_artist_stats(tracks)

    # Genre Stats
    genre_counts = calc_genre_stats(tracks)
    genre_scores = compute_playlist_genres(genre_counts)

    # Calculate Playlist Weights
    year_count = tally_decades_from_tracks(tracks)
    sorted_genre_data = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    top_10_genre_data = dict(sorted_genre_data[:10])
    artgen_ten, genre_scores = calculate_playlist_weights(genre_counts)

    # Aggregate Results
    playlist_data = {
        "temporal_stats": temporal_stats,
        "feature_stats": feature_stats,
        "top_artists": artist_counts,
        "genre_stats": genre_counts,
        "year_count": year_count,
        "top_10_genres": top_10_genre_data,
        "artgen_ten": artgen_ten,
        "genre_scores": genre_scores,
    }

    # Update the database with the aggregated statistics
    add_playlist_temporal_stats(playlist_id, newest_track, oldest_track)
    add_playlist_feature_stats(playlist_id, feature_stats)
    add_playlist_top_artists(playlist_id, artist_counts)
    add_playlist_genre_stats(playlist_id, genre_counts)

    return playlist_data


def get_playlist_details(sp, playlist_id):
    try:
        # Fetch playlist metadata
        playlist = sp.playlist(playlist_id)
        user_id = playlist["owner"]["id"]
        # Extract and return relevant details
        playlist_details = {
            "id": playlist["id"],
            "name": playlist["name"],
            "owner": playlist["owner"]["display_name"],
            "public": playlist["public"],
            "collaborative": playlist["collaborative"],
            "cover_art": playlist["images"][0]["url"] if playlist["images"] else None,
            "followers": playlist["followers"]["total"],
            "total_tracks": playlist["tracks"]["total"],
            "snapshot_id": playlist["snapshot_id"],
        }
        Playlist.from_spotify_playlist(playlist, user_id)
        return playlist_details
    except Exception as e:
        print(f"Error fetching playlist details: {e}")
        return None
