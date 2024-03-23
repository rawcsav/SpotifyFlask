import json
from datetime import datetime

from flask import Blueprint, render_template, session, request, jsonify
from pytz import timezone

from app import db
from modules.auth.auth import require_spotify_auth, fetch_user_data
from modules.user.user_util import convert_utc_to_est, check_and_refresh_user_data, fetch_user_stats
from modules.auth.auth_util import verify_session, init_session_client
from app.models.user_models import User

user_bp = Blueprint("user", __name__, template_folder="templates", static_folder="static")

eastern = timezone("US/Eastern")


@user_bp.route("/profile")
@require_spotify_auth
def profile():
    try:
        access_token = verify_session(session)
        res_data = fetch_user_data(access_token)
        spotify_user_id = res_data.get("id")
        spotify_user_display_name = res_data.get("display_name")
        spotify_profile_img_url = res_data.get("images")[0].get("url") if res_data.get("images") else None
        spotify_followers = res_data.get("followers").get("total")
        spotify_account_type = res_data.get("product")

        session["DISPLAY_NAME"] = spotify_user_display_name
        session["USER_ID"] = spotify_user_id

        sp, error = init_session_client(session)
        if error:
            return json.dumps(error), 401

        user_data_entry = User.query.filter_by(id=spotify_user_id).first()
        user_data = fetch_user_stats(sp)
        new_entry = User(
            id=spotify_user_id,
            user_name=spotify_user_display_name,
            profile_img_url=spotify_profile_img_url,
            followers=spotify_followers,
            account_type=spotify_account_type,
            api_key=None,
        )
        db.session.merge(new_entry)  # Efficiently handles both insert and update operations
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        est_time = convert_utc_to_est(datetime.utcnow())
        return render_template(
            "templates/profile.html",
            data=res_data,
            tokens=session.get("tokens"),
            user_data=user_data,
            last_active=est_time,
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e), 500


@user_bp.route("/refresh-data", methods=["POST"])
def refresh_data():
    try:
        sp = init_session_client(session)
        access_token = verify_session(session)
        res_data = fetch_user_data(access_token)
        spotify_user_id = res_data.get("id")
        session["USER_ID"] = spotify_user_id
        user_data_entry = User.query.filter_by(id=spotify_user_id).first()
        if user_data_entry:
            check_and_refresh_user_data(sp, user_data_entry)
            return "User Refreshed Successfully!", 200
        else:
            return "User data not found", 404

    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e), 500


@user_bp.route("/get_mode", methods=["GET"])
def get_mode():
    access_token = verify_session(session)
    res_data = fetch_user_data(access_token)
    spotify_user_id = res_data.get("id")

    user = User.query.filter_by(id=spotify_user_id).first()

    mode = "dark" if user.dark_mode else "light"

    return jsonify({"mode": mode})


@user_bp.route("/update_mode", methods=["POST"])
def update_mode():
    access_token = verify_session(session)
    res_data = fetch_user_data(access_token)
    spotify_user_id = res_data.get("id")
    mode = request.json.get("mode")

    # Assuming you're using SQLalchemy for ORM
    user = User.query.filter_by(id=spotify_user_id).first()
    user.dark_mode = True if mode == "dark" else False
    db.session.commit()

    return jsonify({"message": "Mode updated successfully!"}), 200
