from datetime import datetime, timedelta
from functools import wraps

from flask import session
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models.artist_models import Artist, Genre, GenreArtistAssociation
from app.models.playlist_models import (
    Playlist,
    PlaylistTrack,
    PlaylistTemporalStats,
    PlaylistYearlyStats,
    PlaylistFeatureStats,
    PlaylistTopArtists,
    PlaylistGenreStats,
)
from app.models.track_models import Album, Track, TrackArtistAssociation, AudioFeature
from app.models.user_models import RecentlyPlayedTracks, UserTrackStats, UserArtistStats, UserGenreStats
from modules.auth.auth import fetch_user_id


def transform_to_expected_format(existing_entries):
    # Initialize a dictionary to hold data organized by period
    transformed_data = {"long_term": [], "medium_term": [], "short_term": []}

    for entry in existing_entries:
        entry_dict = entry.to_dict()
        if entry.period in transformed_data:
            # Check if the entry is a track or an artist
            if hasattr(entry, "track_id"):
                track = Track.query.get(entry.track_id)
                if track:
                    entry_dict.update(track.to_dict())
            elif hasattr(entry, "artist_id"):
                artist = Artist.query.get(entry.artist_id)
                if artist:
                    entry_dict.update(artist.to_dict())

            transformed_data[entry.period].append(entry_dict)
        else:
            print(f"Unexpected period '{entry.period}' encountered in existing entries.")

    return transformed_data


def get_user_music_profile(user_id):
    # Fetch top tracks by period and transform
    top_tracks = UserTrackStats.query.filter_by(user_id=user_id).all()
    top_tracks_by_period = transform_to_expected_format(top_tracks)

    # Fetch top artists by period and transform
    top_artists = UserArtistStats.query.filter_by(user_id=user_id).all()
    top_artists_by_period = transform_to_expected_format(top_artists)

    # Fetch top genres by period and transform
    top_genres = UserGenreStats.query.filter_by(user_id=user_id).all()
    top_genres_by_period = transform_to_expected_format(top_genres)

    # Fetch recently played tracks and convert to list of dictionaries
    recently_played_tracks = RecentlyPlayedTracks.query.filter_by(user_id=user_id).all()
    recently_played_tracks_list = [track.to_dict() for track in recently_played_tracks]

    return top_tracks_by_period, top_artists_by_period, top_genres_by_period, recently_played_tracks_list


def conditional_update(model, update_interval=timedelta(weeks=1), periods=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, force_update=False, **kwargs):
            user_id = fetch_user_id(session)
            existing_entries = model.query.filter_by(user_id=user_id).all()
            if existing_entries:
                latest_entry = max(existing_entries, key=lambda entry: entry.updated_at)
                if (datetime.utcnow() - latest_entry.updated_at) < update_interval and not force_update:
                    print(f"{model.__name__} entries for user {user_id} are up-to-date. Returning current values.")
                    if periods:
                        return transform_to_expected_format(existing_entries)
                    return None
                else:
                    print(
                        f"Data for {model.__name__} entries for user {user_id} is outdated or force update requested."
                    )
            else:
                print(f"No existing {model.__name__} entries found for user {user_id}. Treating as new user.")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def add_artist(artist_info):
    artist = Artist.query.get(artist_info["id"])
    if not artist:
        artist = Artist(id=artist_info["id"])
    artist.name = artist_info.get("name")
    artist.popularity = artist_info.get("popularity")
    artist.followers = artist_info.get("followers")
    artist.external_url = artist_info.get("external_url")
    artist.image_url = artist_info.get("image_url")
    db.session.add(artist)
    db.session.flush()  # Flush to ensure artist.id is available for genre association
    if "genres" in artist_info:
        add_genre(artist.id, artist_info["genres"])
    db.session.commit()
    return artist


def add_genre(artist_id, genre_names):
    artist = Artist.query.get(artist_id)
    if not artist:
        raise ValueError("Artist not found in the database.")

    for genre_name in genre_names:
        genre = Genre.query.get(genre_name)
        if not genre:
            genre = Genre(name=genre_name)
            db.session.add(genre)

        # Check if the association already exists
        association_exists = GenreArtistAssociation.query.filter_by(genre_id=genre_name, artist_id=artist_id).first()
        if not association_exists:
            artist.genres.append(genre)

    db.session.commit()


def add_album(album_info):
    album = Album.query.get(album_info["id"])
    if not album:
        album = Album(id=album_info["id"])

    album.name = album_info.get("name")
    album.release_date = (
        datetime.strptime(album_info.get("release_date"), "%Y-%m-%d") if album_info.get("release_date") else None
    )
    album.release_date_precision = album_info.get("release_date_precision")
    album.cover_art_url = album_info.get("cover_art_url")

    db.session.add(album)
    db.session.commit()

    return album


def add_recent_tracks(user_id, recently_played_tracks):
    RecentlyPlayedTracks.query.filter_by(user_id=user_id).delete()
    for track_info in recently_played_tracks:
        played_at_datetime = datetime.strptime(track_info["played_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        new_entry = RecentlyPlayedTracks(user_id=user_id, track_id=track_info["track_id"], played_at=played_at_datetime)
        db.session.add(new_entry)

    db.session.commit()


def add_track(track_info):
    album = add_album(track_info.get("album"))

    track = Track.query.get(track_info["id"])
    if not track:
        track = Track(id=track_info["id"])

    track.name = track_info.get("name")
    track.album_id = album.id
    track.explicit = track_info.get("explicit", False)
    track.is_local = track_info.get("is_local", False)
    track.duration_ms = track_info.get("duration_ms")
    track.external_url = track_info.get("external_url")
    track.popularity = track_info.get("popularity")

    db.session.add(track)
    db.session.commit()

    return track


def link_track_artist(track_id, artist_infos):
    for artist_info in artist_infos:
        artist = Artist.query.get(artist_info["id"])
        if not artist:
            artist = Artist(id=artist_info["id"], name=artist_info.get("name"))
            db.session.add(artist)
        association_exists = TrackArtistAssociation.query.filter_by(
            track_id=track_id, artist_id=artist_info["id"]
        ).first()
        if not association_exists:
            track_artist_association = TrackArtistAssociation(track_id=track_id, artist_id=artist_info["id"])
            db.session.add(track_artist_association)

    db.session.commit()


def add_features(track_id, features):
    audio_feature = AudioFeature.query.filter_by(track_id=track_id).first()

    if not audio_feature:
        audio_feature = AudioFeature(track_id=track_id)

    audio_feature.key = features.get("key")
    audio_feature.mode = features.get("mode")
    audio_feature.tempo = features.get("tempo")
    audio_feature.energy = features.get("energy")
    audio_feature.valence = features.get("valence")
    audio_feature.liveness = features.get("liveness")
    audio_feature.loudness = features.get("loudness")
    audio_feature.speechiness = features.get("speechiness")
    audio_feature.acousticness = features.get("acousticness")
    audio_feature.danceability = features.get("danceability")
    audio_feature.time_signature = features.get("time_signature")
    audio_feature.instrumentalness = features.get("instrumentalness")

    db.session.add(audio_feature)
    db.session.commit()


def add_playlist(playlist_info, user_id):
    playlist = Playlist.query.get(playlist_info["id"])

    if not playlist:
        playlist = Playlist(id=playlist_info["id"])

    playlist.name = playlist_info["name"]
    playlist.owner = playlist_info["owner"]
    playlist.user_id = user_id
    playlist.public = playlist_info["public"]
    playlist.collaborative = playlist_info["collaborative"]
    playlist.cover_art = playlist_info["cover_art"]
    playlist.followers = playlist_info["followers"]
    playlist.total_tracks = playlist_info["total_tracks"]
    playlist.snapshot_id = playlist_info["snapshot_id"]

    db.session.add(playlist)
    db.session.commit()


def add_playlist_track(playlist_id, track_id, track_order, added_at_str):
    added_at = datetime.strptime(added_at_str, "%Y-%m-%dT%H:%M:%SZ")

    playlist_track = PlaylistTrack.query.filter_by(playlist_id=playlist_id, track_id=track_id).first()
    if not playlist_track:
        playlist_track = PlaylistTrack(playlist_id=playlist_id, track_id=track_id)

    playlist_track.track_order = track_order
    playlist_track.added_at = added_at

    db.session.add(playlist_track)
    db.session.commit()


def fetch_playlist_tracks(playlist_id):
    playlist_tracks = PlaylistTrack.query.filter_by(playlist_id=playlist_id).all()
    tracks = [Track.query.get(playlist_track.track_id) for playlist_track in playlist_tracks if playlist_track.track_id]
    return tracks


def add_playlist_temporal_stats(playlist_id, newest_track, oldest_track):
    temporal_stats = PlaylistTemporalStats.query.get(playlist_id)
    if not temporal_stats:
        temporal_stats = PlaylistTemporalStats(playlist_id=playlist_id)

    temporal_stats.newest_track_id = newest_track.id if newest_track else None
    temporal_stats.oldest_track_id = oldest_track.id if oldest_track else None

    db.session.add(temporal_stats)
    db.session.commit()


def add_playlist_yearly_stats(playlist_id, decade_frequency):
    for decade, count in decade_frequency.items():
        decade_label = f"{decade}s"
        yearly_stats = PlaylistYearlyStats.query.filter_by(playlist_id=playlist_id, year_label=decade_label).first()
        if not yearly_stats:
            yearly_stats = PlaylistYearlyStats(playlist_id=playlist_id, year_label=decade_label, track_count=count)
        else:
            yearly_stats.track_count = count

        db.session.add(yearly_stats)
    db.session.commit()


def fetch_features(track_ids):
    features = []
    for track_id in track_ids:
        feature = AudioFeature.query.filter_by(track_id=track_id).first()
        if feature:
            features.append(feature.to_dict())
    return features


def add_playlist_feature_stats(playlist_id, feature_stats):
    for feature, stats in feature_stats.items():
        playlist_feature_stats = PlaylistFeatureStats.query.filter_by(playlist_id=playlist_id, feature=feature).first()
        if not playlist_feature_stats:
            playlist_feature_stats = PlaylistFeatureStats(playlist_id=playlist_id, feature=feature)
        playlist_feature_stats.avg_value = stats["avg_value"]
        playlist_feature_stats.max_value = stats["max_value"]
        playlist_feature_stats.min_value = stats["min_value"]
        playlist_feature_stats.total_value = stats["total_value"]

        db.session.add(playlist_feature_stats)
    db.session.commit()


def add_playlist_top_artists(playlist_id, artist_counts):
    for artist_id, count in artist_counts.items():
        top_artist_entry = PlaylistTopArtists.query.filter_by(playlist_id=playlist_id, artist_id=artist_id).first()
        if not top_artist_entry:
            top_artist_entry = PlaylistTopArtists(playlist_id=playlist_id, artist_id=artist_id, track_count=count)
        else:
            top_artist_entry.track_count = count

        db.session.add(top_artist_entry)
    db.session.commit()


def add_playlist_genre_stats(playlist_id, genre_counts):
    for genre_name, count in genre_counts.items():
        genre_stat_entry = PlaylistGenreStats.query.filter_by(playlist_id=playlist_id, genre_id=genre_name).first()
        if not genre_stat_entry:
            genre_stat_entry = PlaylistGenreStats(playlist_id=playlist_id, genre_id=genre_name, track_count=count)
        else:
            genre_stat_entry.track_count = count

        db.session.add(genre_stat_entry)
    db.session.commit()


def add_top_tracks(user_top_tracks, user_id):
    try:
        UserTrackStats.query.filter_by(user_id=user_id).delete()
        for period, tracks in user_top_tracks.items():
            Track.from_spotify_track(tracks)
            for rank, track in enumerate(tracks, start=1):
                new_entry = UserTrackStats(user_id=user_id, track_id=track["id"], period=period, popularity_score=rank)
                db.session.add(new_entry)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Failed to update top tracks for user {user_id}: {e}")


def add_top_artists(user_top_artists, user_id):
    try:
        UserArtistStats.query.filter_by(user_id=user_id).delete()
        for period, artists in user_top_artists.items():
            Artist.from_spotify_artists(artists)
            for rank, artist in enumerate(artists, start=1):
                new_entry = UserArtistStats(
                    user_id=user_id, artist_id=artist["id"], period=period, popularity_score=rank
                )
                db.session.add(new_entry)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Failed to update top artists for user {user_id}: {e}")


def add_top_genres(user_id, genre_contributions_by_period, force_update=False):
    try:
        print("1")
        UserGenreStats.query.filter_by(user_id=user_id).delete()
        print("2")
        for period, genres in genre_contributions_by_period.items():
            print("3")
            for genre_name, contributions in genres.items():
                print("4")
                genre = Genre.query.filter_by(name=genre_name).first()
                if not genre:
                    continue  # Skip if genre does not exist in the Genre table
                new_entry = UserGenreStats(
                    user_id=user_id, genre_id=genre_name, period=period, popularity_score=contributions
                )
                db.session.add(new_entry)

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Failed to update genre stats for user {user_id}: {e}")


def get_artist_genres_from_db(artist_ids):
    genres = (
        db.session.query(Genre.name).join(GenreArtistAssociation).join(Artist).filter(Artist.id.in_(artist_ids)).all()
    )
    return [genre_name for genre_name, in genres]
