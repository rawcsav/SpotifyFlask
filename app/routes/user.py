import requests
from flask import Blueprint, render_template, session, abort

from app import config

bp = Blueprint('user', __name__)


@bp.route('/profile')
def profile():
    if 'tokens' not in session:
        abort(400)

    headers = {'Authorization': f"Bearer {session['tokens'].get('access_token')}"}

    res = requests.get(config.ME_URL, headers=headers)
    res_data = res.json()

    if res.status_code != 200:
        abort(res.status_code)

    return render_template('profile.html', data=res_data, tokens=session.get('tokens'))
