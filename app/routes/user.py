import json
from pytz import timezone

from flask import Blueprint, render_template, session, request, jsonify

from app.routes.auth import require_spotify_auth
from app.util.database_utils import db, UserData
from app.util.session_utils import verify_session, fetch_user_data, convert_utc_to_est

from app.util.spotify_utils import fetch_and_process_data, init_session_client, update_user_data, \
    check_and_refresh_user_data, delete_old_user_data
from datetime import datetime

bp = Blueprint("user", __name__)

eastern = timezone('US/Eastern')


@bp.route("/profile")
@require_spotify_auth
def profile():
    try:
        access_token = verify_session(session)
        res_data = fetch_user_data(access_token)
        spotify_user_id = res_data.get("id")
        spotify_user_display_name = res_data.get("display_name")

        session["DISPLAY_NAME"] = spotify_user_display_name
        session["USER_ID"] = spotify_user_id
        sp, error = init_session_client(session)
        if error:
            return json.dumps(error), 401

        user_data_entry = UserData.query.filter_by(spotify_user_id=spotify_user_id).first()

        if check_and_refresh_user_data(user_data_entry):
            user_data = {
                "top_tracks": user_data_entry.top_tracks,
                "top_artists": user_data_entry.top_artists,
                "all_artists_info": user_data_entry.all_artists_info,
                "audio_features": user_data_entry.audio_features,
                "sorted_genres": user_data_entry.sorted_genres_by_period,
                "genre_specific_data": user_data_entry.genre_specific_data,
                "recent_tracks": user_data_entry.recent_tracks,
                "playlists": user_data_entry.playlist_info,
                "last_active": user_data_entry.last_active
            }
            last_active = user_data_entry.last_active

        else:
            last_active = datetime.utcnow()

            time_periods = ["short_term", "medium_term", "long_term"]
            top_tracks, top_artists, all_artists_info, audio_features, genre_specific_data, sorted_genres_by_period, recent_tracks, playlist_info = fetch_and_process_data(
                sp, time_periods)

            user_data = {
                "top_tracks": top_tracks,
                "top_artists": top_artists,
                "all_artists_info": all_artists_info,
                "audio_features": audio_features,
                "sorted_genres": sorted_genres_by_period,
                "genre_specific_data": genre_specific_data,
                "recent_tracks": recent_tracks,
                "playlists": playlist_info,
            }

            new_entry = UserData(
                spotify_user_id=spotify_user_id,
                top_tracks=top_tracks,
                top_artists=top_artists,
                all_artists_info=all_artists_info,
                audio_features=audio_features,
                genre_specific_data=genre_specific_data,
                sorted_genres_by_period=sorted_genres_by_period,
                recent_tracks=recent_tracks,
                playlist_info=playlist_info,
                last_active=last_active  # Set the last_active timestamp for the new user
            )
            db.session.merge(new_entry)
            db.session.commit()

        delete_old_user_data()

        est_time = convert_utc_to_est(last_active)
        return render_template("profile.html", data=res_data, tokens=session.get("tokens"), user_data=user_data,
                               last_active=est_time)

    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e), 500


@bp.route('/refresh-data', methods=['POST'])
def refresh_data():
    try:
        access_token = verify_session(session)
        res_data = fetch_user_data(access_token)
        spotify_user_id = res_data.get("id")
        session["USER_ID"] = spotify_user_id

        user_data_entry = UserData.query.filter_by(spotify_user_id=spotify_user_id).first()
        if user_data_entry:
            update_user_data(user_data_entry)
            return "User Refreshed Successfully!", 200
        else:
            return "User data not found", 404

    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e), 500


@bp.route('/update_mode', methods=['POST'])
def update_mode():
    # Get the user ID and mode from the request
    access_token = verify_session(session)
    res_data = fetch_user_data(access_token)
    spotify_user_id = res_data.get("id")
    mode = request.json.get('mode')

    # Update the user's mode in the database
    # Assuming you're using SQLalchemy for ORM
    user = UserData.query.filter_by(spotify_user_id=spotify_user_id).first()
    user.isDarkMode = True if mode == "dark" else False
    db.session.commit()

    return jsonify({'message': 'Mode updated successfully!'}), 200
