from flask import Flask
from flask_caching import Cache

from app import config

# Create a global cache instance
cache = Cache(config={'CACHE_TYPE': 'simple'})  # Use 'redis' or 'memcached' for production environments


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    # Initialize caching for this app
    cache.init_app(app)

    # Register blueprints
    from .routes import auth, user, stats, search, recommendations, taste
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(recommendations.bp)
    app.register_blueprint(taste.bp)

    return app
