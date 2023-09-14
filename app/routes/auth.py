import json
import secrets
import string
from urllib.parse import urlencode

import requests
from flask import Blueprint, abort, make_response, redirect, render_template, request, session, url_for

from app import config

bp = Blueprint('auth', __name__)


@bp.route('/')
def index():
    return render_template('landing.html')


@bp.route('/<loginout>')
def login(loginout):
    state = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(16)
    )

    # Request authorization from user
    scope = 'user-read-private user-top-read user-read-recently-played playlist-read-private playlist-read-collaborative ' \
            'playlist-modify-private playlist-modify-public user-library-modify user-library-read'

    if loginout == 'logout':
        payload = {
            'client_id': config.CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': config.REDIRECT_URI,
            'state': state,
            'scope': scope,
            'show_dialog': True,
        }
    elif loginout == 'login':
        payload = {
            'client_id': config.CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': config.REDIRECT_URI,
            'state': state,
            'scope': scope,
        }
    else:
        abort(404)

    res = make_response(redirect(f'{config.AUTH_URL}/?{urlencode(payload)}'))
    res.set_cookie('spotify_auth_state', state)

    return res


@bp.route('/callback')
def callback():
    error = request.args.get('error')
    code = request.args.get('code')

    state = request.args.get('state')
    stored_state = request.cookies.get('spotify_auth_state')

    # Check state
    if state is None or state != stored_state:
        abort(400)

    # Request tokens with code we obtained
    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': config.REDIRECT_URI,
    }

    res = requests.post(config.TOKEN_URL, auth=(config.CLIENT_ID, config.CLIENT_SECRET), data=payload)
    res_data = res.json()

    if res_data.get('error') or res.status_code != 200:
        abort(res.status_code)

    # Load tokens into session
    session['tokens'] = {
        'access_token': res_data.get('access_token'),
        'refresh_token': res_data.get('refresh_token'),
    }

    return redirect(url_for('user.profile'))


@bp.route('/refresh')
def refresh():
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': session.get('tokens').get('refresh_token'),
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    res = requests.post(config.TOKEN_URL, auth=(config.CLIENT_ID, config.CLIENT_SECRET), data=payload, headers=headers)

    res_data = res.json()

    # Load new token into session
    session['tokens']['access_token'] = res_data.get('access_token')

    return json.dumps(session['tokens'])
