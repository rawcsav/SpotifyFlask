import os

from flask import Flask, session, g
from flask_session import Session
import logging
from logging.handlers import RotatingFileHandler

from app import config
from app.util.database_utils import db, UserData, load_data_into_artgen, load_data_into_artgenstyle, genre_sql, \
    artgen_sql


def create_app():
    app = Flask(__name__)

    app.app_context().push()

    app.secret_key = config.SECRET_KEY
    app.config["SESSION_TYPE"] = config.SESSION_TYPE
    app.config["SESSION_PERMANENT"] = config.SESSION_PERMANENT
    app.config["PERMANENT_SESSION_LIFETIME"] = config.PERMANENT_SESSION_LIFETIME

    app.config["SESSION_COOKIE_SECURE"] = config.SESSION_COOKIE_SECURE
    app.config["SESSION_COOKIE_HTTPONLY"] = config.SESSION_COOKIE_HTTPONLY

    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQL_ALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_ECHO'] = config.SQLALCHEMY_ECHO

    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/webstats.log', maxBytes=1024000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.DEBUG)
        app.logger.info('Your Flask application startup')

    Session(app)

    from .routes import home, auth, user, stats, search, recommendations, playlist, art_gen

    app.register_blueprint(home.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(recommendations.bp)
    app.register_blueprint(playlist.bp)
    app.register_blueprint(art_gen.bp)
    #app.register_blueprint(songfull.bp)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    # load_data_into_artgen()
    # load_data_into_artgenstyle()

    @app.before_request
    def apply_user_preference():
        if 'USER_ID' in session:
            user = UserData.query.filter_by(spotify_user_id=session['USER_ID']).first()
            if user and user.isDarkMode:
                g.is_dark_mode = True
            else:
                g.is_dark_mode = False
        else:
            g.is_dark_mode = False

    return app
