import os

from flask import Flask
from flask_session import Session
import logging
from logging.handlers import RotatingFileHandler

from app import config
from app.util.database_utils import db, UserData


def create_app():
    app = Flask(__name__)

    app.secret_key = config.SECRET_KEY
    app.config["SESSION_TYPE"] = config.SESSION_TYPE
    app.config["SESSION_PERMANENT"] = config.SESSION_PERMANENT
    app.config["PERMANENT_SESSION_LIFETIME"] = config.PERMANENT_SESSION_LIFETIME

    app.config["SESSION_COOKIE_SECURE"] = config.SESSION_COOKIE_SECURE
    app.config["SESSION_COOKIE_HTTPONLY"] = config.SESSION_COOKIE_HTTPONLY

    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI

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

    from .routes import auth, user, stats, search, recommendations, playlist

    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(recommendations.bp)
    app.register_blueprint(playlist.bp)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app
