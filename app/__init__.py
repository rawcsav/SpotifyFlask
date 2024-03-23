import os
from flask import Flask
from flask_assets import Environment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

from config import ProductionConfig, DevelopmentConfig
from flask_cors import CORS

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)
    flask_env = os.getenv("FLASK_ENV", "production").lower()

    if flask_env == "development":
        app.config.from_object(DevelopmentConfig)
        DevelopmentConfig.init_app(app)
    else:
        app.config.from_object(ProductionConfig)
        ProductionConfig.init_app(app)

    assets = Environment(app)
    CORS(app)
    CSRFProtect(app)
    db.init_app(app)
    Migrate(app, db)
    bcrypt.init_app(app)
    assets.init_app(app)  # Initialize Flask-Assets

    with app.app_context():
        from modules.auth import auth
        from modules.user import user
        from modules.stats import stats
        from modules.art_gen import art_gen
        from modules.recs import recs
        from modules.playlists import playlist

        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(user.user_bp)
        app.register_blueprint(stats.stats_bp)
        app.register_blueprint(recs.recs_bp)
        app.register_blueprint(playlist.playlist_bp)
        app.register_blueprint(art_gen.art_gen_bp)

        from app.util.assets_util import compile_static_assets

        compile_static_assets(assets)

        @app.teardown_request
        def session_teardown(exception=None):
            if exception:
                db.session.rollback()
            db.session.remove()

        db.create_all()
        return app
