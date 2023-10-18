from flask import Flask, session, g
from flask_session import Session
from app import config
from app.util.database_utils import UserData, load_data_into_artgen, load_data_into_artgenstyle, genre_sql, \
    artgen_sql, db
import sshtunnel
from app.util.session_utils import get_tunnel


def create_app():
    app = Flask(__name__)
    app.app_context().push()

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQL_ALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_ECHO'] = config.SQLALCHEMY_ECHO
    app.config["SQLALCHEMY_POOL_RECYCLE"] = config.SQLALCHEMY_POOL_RECYCLE

    if config.FLASK_ENV == 'development':
        sshtunnel.SSH_TIMEOUT = 5.0
        sshtunnel.TUNNEL_TIMEOUT = 5.0
        app.tunnel = get_tunnel()
        app.config[
            'SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{config.SQL_USERNAME}:{config.SQL_PASSWORD}@127.0.0.1:{app.tunnel.local_bind_port}/{config.SQL_DB_NAME}'

    else:
        app.tunnel = None
        app.config[
            'SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{config.SQL_USERNAME}:{config.SQL_PASSWORD}@{config.SQL_HOSTNAME}/{config.SQL_DB_NAME}'

    app.config["SESSION_TYPE"] = config.SESSION_TYPE
    app.config["SESSION_PERMANENT"] = config.SESSION_PERMANENT
    app.config["PERMANENT_SESSION_LIFETIME"] = config.PERMANENT_SESSION_LIFETIME
    app.config["SESSION_COOKIE_SECURE"] = config.SESSION_COOKIE_SECURE
    app.config["SESSION_COOKIE_HTTPONLY"] = config.SESSION_COOKIE_HTTPONLY
    app.config['SESSION_SQLALCHEMY'] = db
    app.config['SESSION_KEY_PREFIX'] = config.SESSION_KEY_PREFIX
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'pool_reset_on_return': 'rollback'
    }

    db.init_app(app)

    Session(app)

    db.create_all()
    app.secret_key = config.SECRET_KEY

    from .routes import home, auth, user, stats, search, recommendations, playlist, \
        art_gen  # songfull

    app.register_blueprint(home.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(stats.bp)
    app.register_blueprint(search.bp)
    app.register_blueprint(recommendations.bp)
    app.register_blueprint(playlist.bp)
    app.register_blueprint(art_gen.bp)

    # app.register_blueprint(songfull.bp)

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
