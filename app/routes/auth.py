from datetime import datetime, timedelta
from functools import wraps
from urllib.parse import urlencode

from flask import (Blueprint, abort, make_response, redirect, render_template,
                   request, session, url_for, jsonify)
from app import config
from app.util.database_utils import UserData, db
from app.util.session_utils import generate_state, prepare_auth_payload, request_tokens, load_key_from_env, \
    is_api_key_valid, encrypt_data, verify_session, fetch_user_data

bp = Blueprint('auth', __name__)


@bp.route('/auth')
def index():
    return render_template('landing.html')


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

        return f(*args, **kwargs)

    return decorated_function


@bp.route('/<loginout>')
def login(loginout):
    if loginout == 'logout':
        session.clear()
        return redirect(url_for('auth.index'))

    state = generate_state()
    scope = ' '.join([
        'user-read-private', 'user-top-read', 'user-read-recently-played',
        'playlist-read-private', 'playlist-read-collaborative', 'playlist-modify-private',
        'playlist-modify-public', 'user-library-modify', 'user-library-read', 'ugc-image-upload'

    ])
    payload = prepare_auth_payload(state, scope, show_dialog=(loginout == 'logout'))

    res = make_response(redirect(f'{config.AUTH_URL}/?{urlencode(payload)}'))
    res.set_cookie('spotify_auth_state', state)
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

    return redirect(url_for('user.profile'))


@bp.route('/refresh')
def refresh():
    payload = {'grant_type': 'refresh_token', 'refresh_token': session.get('tokens').get('refresh_token')}

    res_data, error = request_tokens(payload, config.CLIENT_ID, config.CLIENT_SECRET)
    if error:
        return redirect(url_for('auth.index'))

    new_access_token = res_data.get('access_token')
    new_refresh_token = res_data.get('refresh_token', session['tokens']['refresh_token'])
    expires_in = res_data.get('expires_in')
    new_expiry_time = datetime.now() + timedelta(seconds=expires_in)

    session['tokens'].update({
        'access_token': new_access_token,
        'refresh_token': new_refresh_token,
        'expiry_time': new_expiry_time.isoformat()
    })

    return redirect(session.pop('original_request_url', url_for('user.profile')))


@bp.route('/save-api-key', methods=['POST'])
def save_api_key():
    access_token = verify_session(session)
    res_data = fetch_user_data(access_token)
    spotify_user_id = res_data.get("id")

    user_data = UserData.query.filter_by(spotify_user_id=spotify_user_id).first()

    api_key = request.json.get('api_key')

    # Validate the key by using is_api_key_valid function
    if not is_api_key_valid(api_key):
        return jsonify({"message": "Invalid OpenAI API Key"}), 400

    # If validation successful, encrypt and save the key
    encrypted_key = encrypt_data(api_key)
    try:
        user_data.api_key_encrypted = encrypted_key
        session.commit()
    except:
        session.rollback()
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
