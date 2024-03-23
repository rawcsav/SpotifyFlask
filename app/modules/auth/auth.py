import re
from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import urlencode
import cloudinary
import requests
from flask import Blueprint, abort, redirect, render_template, request, session, url_for, jsonify, current_app
from flask import make_response
from openai import OpenAI

from app import db
from app.models.user_models import User
from modules.auth.auth_util import (
    verify_session,
    generate_state,
    prepare_auth_payload,
    request_tokens,
    encrypt_api_key,
    test_gpt4,
    create_openai_client,
)

auth_bp = Blueprint("auth", __name__, template_folder="templates", static_folder="static")


@auth_bp.route("/")
def index():
    return render_template("landing.html")


def require_spotify_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tokens = session.get("tokens")
        expiry_time = datetime.fromisoformat(tokens.get("expiry_time")) if tokens else None

        if not tokens:
            return redirect(url_for("auth.index"))

        if expiry_time and expiry_time < datetime.now():
            session["original_request_url"] = request.url
            return redirect(url_for("auth.refresh"))

        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route("/<loginout>")
def login(loginout):
    if loginout == "logout":
        session.clear()
        session["show_dialog"] = True
        response = make_response(redirect(url_for("auth.index")))
        response.set_cookie("spotify_auth_state", "", expires=0, path="/")
        return response

    state = generate_state()
    scope = " ".join(
        [
            "user-read-private",
            "user-top-read",
            "user-read-recently-played",
            "user-follow-modify",
            "playlist-read-private",
            "playlist-read-collaborative",
            "playlist-modify-private",
            "playlist-modify-public",
            "user-library-modify",
            "user-library-read",
            "ugc-image-upload",
        ]
    )
    show_dialog = session.pop("show_dialog", False)
    payload = prepare_auth_payload(state, scope, show_dialog=show_dialog)
    res = make_response(redirect(f'{current_app.config["AUTH_URL"]}/?{urlencode(payload)}'))
    res.set_cookie("spotify_auth_state", state)

    return res


@auth_bp.route("/callback")
def callback():
    state = request.args.get("state")
    stored_state = request.cookies.get("spotify_auth_state")

    # Add print statements to debug the values of state and stored_state
    print(f"State from request: {state}")
    print(f"Stored state from cookies: {stored_state}")

    if state is None or state != stored_state:
        abort(400, description="State mismatch")

    code = request.args.get("code")
    payload = {"grant_type": "authorization_code", "code": code, "redirect_uri": current_app.config["REDIRECT_URI"]}

    res_data, error = request_tokens(payload, current_app.config["CLIENT_ID"], current_app.config["CLIENT_SECRET"])
    if error:
        abort(400, description="Error obtaining tokens from Spotify")

    access_token = res_data.get("access_token")
    expires_in = res_data.get("expires_in")
    expiry_time = datetime.now() + timedelta(seconds=expires_in)

    session["tokens"] = {
        "access_token": access_token,
        "refresh_token": res_data.get("refresh_token"),
        "expiry_time": expiry_time.isoformat(),
    }

    return redirect(url_for("user.profile"))


@auth_bp.route("/refresh")
def refresh():
    payload = {"grant_type": "refresh_token", "refresh_token": session.get("tokens").get("refresh_token")}

    res_data, error = request_tokens(payload, current_app.config["CLIENT_ID"], current_app.config["CLIENT_SECRET"])
    if error:
        return redirect(url_for("auth.index"))

    new_access_token = res_data.get("access_token")
    new_refresh_token = res_data.get("refresh_token", session["tokens"]["refresh_token"])
    expires_in = res_data.get("expires_in")
    new_expiry_time = datetime.now() + timedelta(seconds=expires_in)

    session["tokens"].update(
        {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "expiry_time": new_expiry_time.isoformat(),
        }
    )

    return redirect(session.pop("original_request_url", url_for("user.profile")))


@auth_bp.route("/save-api-key", methods=["POST"])
def save_api_key():
    access_token = verify_session(session)
    res_data = fetch_user_data(access_token)
    spotify_user_id = res_data.get("id")

    user_data = User.query.filter_by(id=spotify_user_id).first()

    api_key = request.json.get("api_key")
    api_key_pattern = re.compile(r"sk-[A-Za-z0-9]{48}")
    if not api_key_pattern.match(api_key):
        return jsonify({"status": "error", "message": "Invalid API key format."}), 400
    client = OpenAI(api_key=api_key)
    if not test_gpt4(client):
        return jsonify({"message": "Invalid OpenAI API Key"}), 400
    encrypted_key = encrypt_api_key(api_key)
    try:
        user_data.api_key = encrypted_key
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return jsonify({"message": "API Key saved successfully"}), 200


@auth_bp.route("/check-api-key", methods=["GET"])
def check_api_key():
    access_token = verify_session(session)
    if not access_token:
        # Handle the case where session verification fails
        return jsonify({"error": "Access token verification failed"}), 401

    res_data = fetch_user_data(access_token)
    if not res_data:
        # Handle the case where fetching user data fails
        return jsonify({"error": "Failed to fetch user data"}), 500

    spotify_user_id = res_data.get("id")
    if not spotify_user_id:
        return jsonify({"error": "Spotify user ID not found"}), 500

    client = create_openai_client(spotify_user_id)
    if test_gpt4(client):
        return jsonify({"has_key": True})
    else:
        return jsonify({"has_key": False})


@auth_bp.route("/secure_image")
def secure_image():
    EXCLUDED_PUBLIC_IDS = ["image1", "image2", "image3"]  # Add public_ids of images you want to exclude

    public_id = request.args.get("public_id")
    if not public_id:
        return "Public ID not provided", 400

    # Get transformations from query parameters
    width = request.args.get("width", None)
    height = request.args.get("height", None)
    crop = request.args.get("crop", None)
    aspect_ratio = request.args.get("aspect_ratio", None)
    gravity = request.args.get("gravity", None)
    radius = request.args.get("radius", None)
    quality = request.args.get("quality", None)
    effect = request.args.get("effect", None)
    opacity = request.args.get("opacity", None)
    border = request.args.get("border", None)
    background = request.args.get("background", None)
    angle = request.args.get("angle", None)
    overlay = request.args.get("overlay", None)
    tint = request.args.get("tint", None)
    format = request.args.get("format", None)

    transformations = {"quality": "auto"}

    if public_id not in EXCLUDED_PUBLIC_IDS:
        transformations["fetch_format"] = "auto"

    if width:
        transformations["width"] = int(width)
    if height:
        transformations["height"] = int(height)
    if crop:
        transformations["crop"] = crop
    if aspect_ratio:
        transformations["aspect_ratio"] = aspect_ratio
    if gravity:
        transformations["gravity"] = gravity
    if radius:
        transformations["radius"] = radius
    if quality:
        transformations["quality"] = int(quality)
    if effect:
        transformations["effect"] = effect
    if opacity:
        transformations["opacity"] = int(opacity)
    if border:
        transformations["border"] = border
    if background:
        transformations["background"] = background
    if angle:
        transformations["angle"] = angle
    if overlay:
        transformations["overlay"] = overlay
    if tint:
        transformations["tint"] = tint
    if format:
        transformations["format"] = format

    signed_url = cloudinary.utils.cloudinary_url(public_id, **transformations, sign_url=True)[0]

    # Redirect to the signed URL
    return redirect(signed_url)


def fetch_user_data(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(current_app.config["ME_URL"], headers=headers)
    if res.status_code != 200:
        abort(res.status_code)

    return res.json()


def fetch_user_id(session):
    access_token = verify_session(session)
    res_data = fetch_user_data(access_token)
    user_id = res_data.get("id")
    return user_id
