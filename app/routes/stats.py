from flask import Blueprint, render_template, session
from spotipy import Spotify

bp = Blueprint('stats', __name__)


@bp.route('/stats')
def stats():
    access_token = session['tokens'].get('access_token')
    sp = Spotify(auth=access_token)  # Fix the typo here

    time_periods = ['short_term', 'medium_term', 'long_term']

    top_tracks = {period: sp.current_user_top_tracks(time_range=period, limit=50) for period in time_periods}
    top_artists = {period: sp.current_user_top_artists(time_range=period, limit=50) for period in time_periods}

    return render_template('stats.html', top_tracks=top_tracks, top_artists=top_artists)
