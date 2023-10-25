from datetime import datetime, timedelta
from urllib.parse import urlencode
import cloudinary
from flask import (Blueprint, abort, make_response, redirect, render_template,
                   request, session, url_for, jsonify)

from app import config
from app.database import UserData, db
from app.util.session_utils import generate_state, prepare_auth_payload, request_tokens, is_api_key_valid, encrypt_data, \
    verify_session, fetch_user_data, refresh_tokens

bp = Blueprint('auth', __name__)


@bp.route('/auth')
def index():
    return render_template('landing.html')


from flask import session, redirect, url_for, request
from functools import wraps
from datetime import datetime


def require_spotify_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tokens = session.get('tokens')
        expiry_time = datetime.fromisoformat(tokens.get('expiry_time')) if tokens else None

        if not tokens:
            return redirect(url_for('auth.index'))

        if expiry_time and expiry_time < datetime.now():
            session['original_request_url'] = request.url
            return redirect(url_for('auth.refresh'))

        access_token = verify_session(session)
        res_data = fetch_user_data(access_token)
        spotify_user_id = res_data.get("id")

        user_data_entry = UserData.query.filter_by(spotify_user_id=spotify_user_id).first()

        if not user_data_entry:
            return redirect(url_for('user.profile'))

        return f(*args, **kwargs)

    return decorated_function


@bp.route('/<loginout>/<next>')
def login(loginout, next):
    if loginout == 'logout':
        if 'songfull' in request.referrer:
            next = url_for('songfull.game')
        else:
            next = url_for('auth.index')  # replace 'explore' with your actual explore route
        session.clear()
        return redirect(next)

    state = generate_state()
    scope = ' '.join([
        'user-read-private', 'user-top-read', 'user-read-recently-played',
        'playlist-read-private', 'playlist-read-collaborative', 'playlist-modify-private',
        'playlist-modify-public', 'user-library-modify', 'user-library-read', 'ugc-image-upload'
    ])
    payload = prepare_auth_payload(state, scope, show_dialog=(loginout == 'logout'))

    res = make_response(redirect(f'{config.AUTH_URL}/?{urlencode(payload)}'))
    res.set_cookie('spotify_auth_state', state)
    res.set_cookie('next_url', next)
    return res


@bp.route('/callback')
def callback():
    state = request.args.get('state')
    stored_state = request.cookies.get('spotify_auth_state')

    if state is None or state != stored_state:
        abort(400, description="State mismatch")

    code = request.args.get('code')
    payload = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': config.REDIRECT_URI}

    res_data, error = request_tokens(payload, config.CLIENT_ID, config.CLIENT_SECRET)
    if error:
        abort(400, description="Error obtaining tokens from Spotify")

    access_token = res_data.get('access_token')
    expires_in = res_data.get('expires_in')
    expiry_time = datetime.now() + timedelta(seconds=expires_in)

    session['tokens'] = {
        'access_token': access_token,
        'refresh_token': res_data.get('refresh_token'),
        'expiry_time': expiry_time.isoformat()
    }

    next_url = request.cookies.get('next_url', url_for('user.profile'))
    return redirect(next_url)


@bp.route('/refresh')
def refresh():
    if not refresh_tokens():
        return redirect(url_for('auth.index'))

    return redirect(session.pop('original_request_url', url_for('user.profile')))


@bp.route('/save-api-key', methods=['POST'])
def save_api_key():
    access_token = verify_session(session)
    res_data = fetch_user_data(access_token)
    spotify_user_id = res_data.get("id")

    user_data = UserData.query.filter_by(spotify_user_id=spotify_user_id).first()

    api_key = request.json.get('api_key')

    if not is_api_key_valid(api_key):
        return jsonify({"message": "Invalid OpenAI API Key"}), 400

    encrypted_key = encrypt_data(api_key)
    try:
        user_data.api_key_encrypted = encrypted_key
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return jsonify({"message": "API Key saved successfully"}), 200


@bp.route('/check-api-key', methods=['GET'])
def check_api_key():
    access_token = verify_session(session)
    res_data = fetch_user_data(access_token)
    spotify_user_id = res_data.get("id")
    user = UserData.query.filter_by(spotify_user_id=spotify_user_id).first()
    if user and user.api_key_encrypted:
        return jsonify({"has_key": True})
    else:
        return jsonify({"has_key": False})


@bp.route('/secure_image')
def secure_image():
    # Get the Cloudinary public_id from the request
    public_id = request.args.get('public_id')
    if not public_id:
        return "Public ID not provided", 400

    # Get transformations from query parameters
    width = request.args.get('width', None)
    height = request.args.get('height', None)
    crop = request.args.get('crop', None)
    aspect_ratio = request.args.get('aspect_ratio', None)
    gravity = request.args.get('gravity', None)
    radius = request.args.get('radius', None)
    quality = request.args.get('quality', None)
    effect = request.args.get('effect', None)
    opacity = request.args.get('opacity', None)
    border = request.args.get('border', None)
    background = request.args.get('background', None)
    angle = request.args.get('angle', None)
    overlay = request.args.get('overlay', None)
    tint = request.args.get('tint', None)
    format = request.args.get('format', None)

    transformations = {
        'quality': 'auto',
        'fetch_format': 'auto'}

    if width:
        transformations['width'] = int(width)
    if height:
        transformations['height'] = int(height)
    if crop:
        transformations['crop'] = crop
    if aspect_ratio:
        transformations['aspect_ratio'] = aspect_ratio
    if gravity:
        transformations['gravity'] = gravity
    if radius:
        transformations['radius'] = radius
    if quality:
        transformations['quality'] = int(quality)
    if effect:
        transformations['effect'] = effect
    if opacity:
        transformations['opacity'] = int(opacity)
    if border:
        transformations['border'] = border
    if background:
        transformations['background'] = background
    if angle:
        transformations['angle'] = angle
    if overlay:
        transformations['overlay'] = overlay
    if tint:
        transformations['tint'] = tint
    if format:
        transformations['format'] = format

    signed_url = cloudinary.utils.cloudinary_url(public_id, **transformations, sign_url=True)[0]

    # Redirect to the signed URL
    return redirect(signed_url)
