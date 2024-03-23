from datetime import timezone, timedelta

from flask import session

from app.models.track_models import Track, TrackArtistAssociation
from app.models.user_models import UserTrackStats, UserArtistStats, UserGenreStats, RecentlyPlayedTracks
from modules.auth.auth import fetch_user_id
from util.api_util import process_artists
from util.database_util import (
    add_recent_tracks,
    add_top_tracks,
    add_top_artists,
    add_top_genres,
    conditional_update,
    get_artist_genres_from_db,
    transform_to_expected_format,
)


@conditional_update(RecentlyPlayedTracks)
def fetch_recent_tracks(sp):
    user_id = fetch_user_id(session)
    recently_played_tracks = []
    tracks = []
    results = sp.current_user_recently_played(limit=50)
    for item in results["items"]:
        track = item["track"]
        tracks.append(track)
        track_info = {"track_id": track["id"], "played_at": item["played_at"]}
        recently_played_tracks.append(track_info)
    artist_ids = set()
    for track in tracks:
        for artist in track["artists"]:
            artist_ids.add(artist["id"])
    process_artists(sp, list(artist_ids))
    Track.from_spotify_tracks(tracks)
    add_recent_tracks(user_id, recently_played_tracks)
    return recently_played_tracks


def convert_utc_to_est(utc_time):
    return utc_time.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=-4)))


def check_and_refresh_user_data(sp, user_data_entry):
    if user_data_entry:
        fetch_user_stats(sp, force_update=True)
        return True
    else:
        return False


def calculate_averages_for_period(period_tracks, audio_features):
    averages = {}
    for feature in audio_features:
        feature_values = [track[feature] for track in period_tracks if feature in track]
        if feature_values:
            averages[feature] = sum(feature_values) / len(feature_values)
    return averages


@conditional_update(UserTrackStats, periods=True)
def fetch_top_tracks(sp, force_update=False):
    user_top_tracks = {}
    user_id = fetch_user_id(session)
    print("Fetch top tracks setting artists")
    for period in ["long_term", "medium_term", "short_term"]:
        try:
            results = sp.current_user_top_tracks(time_range=period, limit=50)
            artists = [artist["id"] for track in results["items"] for artist in track["artists"]]
            process_artists(sp, artists)
            user_top_tracks[period] = results["items"]
        except Exception as e:
            user_top_tracks[period] = []
        add_top_tracks(user_top_tracks, user_id)
    return user_top_tracks


@conditional_update(UserArtistStats, periods=True)
def fetch_top_artists(sp, force_update=False):
    user_top_artists = {}
    user_id = fetch_user_id(session)
    for period in ["long_term", "medium_term", "short_term"]:
        try:
            results = sp.current_user_top_artists(time_range=period, limit=50)  # Adjust limit as needed
            process_artists(sp, [artist["id"] for artist in results["items"]])
            user_top_artists[period] = results["items"]
        except Exception as e:
            print(f"Failed to fetch top artists for {period}: {e}")
            user_top_artists[period] = []  # Keep the structure, even if the fetch fails
        add_top_artists(user_top_artists, user_id)
    return user_top_artists


@conditional_update(UserGenreStats, periods=True)
def fetch_top_genres_by_period(sp, tracks_by_period, artists_by_period):
    genres_by_period = {}
    user_id = fetch_user_id(session)

    for period in tracks_by_period.keys():
        print(f"Fetching genres for {period}")
        genre_counts = {}

        # Extract track IDs from tracks_by_period for the current period
        track_ids = [track["id"] for track in tracks_by_period[period]]

        # Query the TrackArtistAssociation table to get associations for these track IDs
        associations = TrackArtistAssociation.query.filter(TrackArtistAssociation.track_id.in_(track_ids)).all()

        # Extract artist IDs from the associations
        artist_ids_from_tracks = {association.artist_id for association in associations}
        artist_ids_direct = {artist["id"] for artist in artists_by_period.get(period, [])}
        combined_artist_ids = artist_ids_from_tracks.union(artist_ids_direct)
        genres = get_artist_genres_from_db(combined_artist_ids)
        for genre_name in genres:
            genre_counts[genre_name] = genre_counts.get(genre_name, 0) + 1
        sorted_genres = sorted(genre_counts.items(), key=lambda item: item[1], reverse=True)
        genres_by_period[period] = dict(sorted_genres)
    add_top_genres(user_id, genres_by_period)
    return genres_by_period


def calc_genre_stat(tracks_by_period, artists_by_period, genres_by_period, TrackArtistAssociation):
    genre_contributions_by_period = {}
    for period in tracks_by_period.keys():
        genre_contributions = {}
        all_tracks = tracks_by_period[period]
        all_artists = artists_by_period[period]
        top_genres = {entry["genre_id"]: entry["popularity_score"] for entry in genres_by_period[period]}

        for genre in top_genres.keys():
            genre_contributions[genre] = {"tracks": [], "artists": []}

            for track in all_tracks:
                track_artists = TrackArtistAssociation.query.filter(
                    TrackArtistAssociation.track_id == track["id"]
                ).all()
                for track_artist in track_artists:
                    artist = next((artist for artist in all_artists if artist["id"] == track_artist.artist_id), None)
                    if artist and genre in artist["genres"]:
                        genre_contributions[genre]["tracks"].append((track["id"], track["ranking"]))

            for artist in all_artists:
                if genre in artist["genres"]:
                    genre_contributions[genre]["artists"].append((artist["id"], artist["ranking"]))

            genre_contributions[genre]["tracks"] = sorted(genre_contributions[genre]["tracks"], key=lambda x: x[1])
            genre_contributions[genre]["artists"] = sorted(genre_contributions[genre]["artists"], key=lambda x: x[1])

        genre_contributions_by_period[period] = genre_contributions

    return genre_contributions_by_period


def fetch_user_stats(sp, force_update=False):
    user_id = fetch_user_id(session)
    fetch_top_tracks(sp, force_update=force_update)
    fetch_top_artists(sp, force_update=force_update)
    fetch_recent_tracks(sp)

    top_tracks = UserTrackStats.query.filter_by(user_id=user_id).all()
    top_tracks_by_period = transform_to_expected_format(top_tracks)
    top_artists = UserArtistStats.query.filter_by(user_id=user_id).all()
    top_artists_by_period = transform_to_expected_format(top_artists)
    recently_played_tracks = RecentlyPlayedTracks.query.filter_by(user_id=user_id).all()
    recently_played_tracks_list = [track.to_dict() for track in recently_played_tracks]
    print("1")
    fetch_top_genres_by_period(sp, top_tracks_by_period, top_artists_by_period, force_update=force_update)
    print("2")
    top_genres = UserGenreStats.query.filter_by(user_id=user_id).all()
    print("3")
    top_genres_by_period = transform_to_expected_format(top_genres)
    print("4")
    genre_contributions_by_period = calc_genre_stat(top_tracks_by_period, top_artists_by_period, top_genres_by_period)

    return {
        "top_tracks": top_tracks_by_period,
        "top_artists": top_artists_by_period,
        "recent_tracks": recently_played_tracks_list,
        "top_genres": top_genres_by_period,
        "genre_contributions": genre_contributions_by_period,
    }
