from spotipy import SpotifyException
from app import db
from util.api_util import process_artists


def spotify_search(sp, query, type, limit=6):
    try:
        results = sp.search(q=query, type=type, limit=limit)
        if results.get("artists", {}).get("items"):
            for artist_data in results["artists"]["items"]:
                try:
                    process_artists(artist_data)
                    db.session.commit()
                except:
                    db.session.rollback()
                    raise
        return results
    except SpotifyException as e:
        return {"error": str(e)}


def get_recommendations(sp, limit, market, **kwargs):
    seed_tracks = kwargs.get("track", None)
    seed_artists = kwargs.get("artist", None)
    seed_genres = kwargs.get("genre", None)
    try:
        return sp.recommendations(
            seed_tracks=seed_tracks, seed_artists=seed_artists, seed_genres=seed_genres, limit=limit, **kwargs
        )
    except Exception as e:
        return {"error": str(e)}
