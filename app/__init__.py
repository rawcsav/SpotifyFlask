import os
from flask import Flask, session, g
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import Config, ProductionConfig, DevelopmentConfig
from flask_cors import CORS

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    flask_env = os.getenv('FLASK_ENV', 'production').lower()

    if flask_env == 'development':
        app.config.from_object(DevelopmentConfig)
        DevelopmentConfig.init_app(app)
    else:
        app.config.from_object(ProductionConfig)
        ProductionConfig.init_app(app)

    CORS(app)

    db.init_app(app)
    Migrate(app, db)

    with app.app_context():
        from .routes import auth, user, stats, search, recommendations, playlist, \
            art_gen
        from .database import UserData

        app.register_blueprint(auth.bp)
        app.register_blueprint(user.bp)
        app.register_blueprint(stats.bp)
        app.register_blueprint(search.bp)
        app.register_blueprint(recommendations.bp)
        app.register_blueprint(playlist.bp)
        app.register_blueprint(art_gen.bp)

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

        @app.teardown_request
        def session_teardown(exception=None):
            if exception:
                db.session.rollback()
            db.session.remove()

        db.create_all()
        return app
