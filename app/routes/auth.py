import json
from urllib.parse import urlencode

from flask import Blueprint, abort, make_response, redirect, render_template, request, session, url_for

from app import config
from app.util.session_utils import generate_state, prepare_auth_payload, request_tokens

bp = Blueprint('auth', __name__)


@bp.route('/')
def index():
    return render_template('landing.html')


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
        abort(400)

    code = request.args.get('code')
    payload = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': config.REDIRECT_URI}
    res_data, error = request_tokens(payload, config.CLIENT_ID, config.CLIENT_SECRET)
    if error:
        abort(error)

    session['tokens'] = {'access_token': res_data.get('access_token'), 'refresh_token': res_data.get('refresh_token')}
    return redirect(url_for('user.profile'))


@bp.route('/refresh')
def refresh():
    payload = {'grant_type': 'refresh_token', 'refresh_token': session.get('tokens').get('refresh_token')}
    res_data, error = request_tokens(payload, config.CLIENT_ID, config.CLIENT_SECRET)
    if error:
        abort(error)

    session['tokens']['access_token'] = res_data.get('access_token')
    return json.dumps(session['tokens'])
