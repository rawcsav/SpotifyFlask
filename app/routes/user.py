import logging

import requests
from flask import Blueprint, render_template, session, abort

from app import config

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

bp = Blueprint('user', __name__)


@bp.route('/profile')
def profile():
    if 'tokens' not in session:
        bp.logger.error('No tokens in session.')
        abort(400)

    headers = {'Authorization': f"Bearer {session['tokens'].get('access_token')}"}

    res = requests.get(config.ME_URL, headers=headers)
    res_data = res.json()

    if res.status_code != 200:
        bp.logger.error(
            'Failed to get profile info: %s',
            res_data.get('error', 'No error message returned.'),
        )
        abort(res.status_code)

    return render_template('profile.html', data=res_data, tokens=session.get('tokens'))
