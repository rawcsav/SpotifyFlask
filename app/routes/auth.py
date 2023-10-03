from urllib.parse import urlencode

from flask import Blueprint, abort, make_response, redirect, render_template, request, session, url_for, jsonify

from app import config
from datetime import datetime, timedelta
from app.util.session_utils import generate_state, prepare_auth_payload, request_tokens
from functools import wraps

bp = Blueprint('auth', __name__)


@bp.route('/')
def index():
    return render_template('landing.html')


def require_spotify_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'tokens' not in session:
            return redirect(url_for('auth.index'))  # Redirect to the landing page if 'tokens' not in session
        return f(*args, **kwargs)

    return decorated_function


@bp.route('/<loginout>')
def login(loginout):
    state = generate_state()
    scope = 'user-read-private user-top-read user-read-recently-played playlist-read-private playlist-read-collaborative ' \
            'playlist-modify-private playlist-modify-public user-library-modify user-library-read'
    payload = prepare_auth_payload(state, scope, show_dialog=(loginout == 'logout'))
    res = make_response(redirect(f'{config.AUTH_URL}/?{urlencode(payload)}'))
    res.set_cookie('spotify_auth_state', state)
    return res


@bp.route('/callback')
def callback():
    state = request.args.get('state')
    stored_state = request.cookies.get('spotify_auth_state')

    if state is None or state != stored_state:
        # Implement robust logging here
        abort(400, description="State mismatch")

    code = request.args.get('code')
    payload = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': config.REDIRECT_URI}
    res_data, error = request_tokens(payload, config.CLIENT_ID, config.CLIENT_SECRET)
    if error:
        abort(error)

    # Store tokens and expiration time
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
        abort(error)

    new_access_token = res_data.get('access_token')
    new_refresh_token = res_data.get('refresh_token', session['tokens']['refresh_token'])
    expires_in = res_data.get('expires_in')
    new_expiry_time = datetime.now() + timedelta(seconds=expires_in)

    session['tokens'].update({
        'access_token': new_access_token,
        'refresh_token': new_refresh_token,
        'expiry_time': new_expiry_time.isoformat()
    })
    return jsonify(session['tokens'])
