from flask import Flask

from app import config


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    # Register blueprints
    from .routes import auth, user, stats, search, recommendations
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(recommendations.bp)

    return app
