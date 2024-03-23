from datetime import datetime
from sqlalchemy.orm import relationship
from app import db


class artgen_sql(db.Model):
    genre_name = db.Column(db.VARCHAR(50), db.ForeignKey("genre_sql.genre"), primary_key=True)
    place_1 = db.Column(db.TEXT)
    place_2 = db.Column(db.TEXT)
    place_3 = db.Column(db.TEXT)
    place_4 = db.Column(db.TEXT)
    place_5 = db.Column(db.TEXT)
    role_1 = db.Column(db.TEXT)
    role_2 = db.Column(db.TEXT)
    role_3 = db.Column(db.TEXT)
    role_4 = db.Column(db.TEXT)
    role_5 = db.Column(db.TEXT)
    item_1 = db.Column(db.TEXT)
    item_2 = db.Column(db.TEXT)
    item_3 = db.Column(db.TEXT)
    item_4 = db.Column(db.TEXT)
    item_5 = db.Column(db.TEXT)
    symbol_1 = db.Column(db.TEXT)
    symbol_2 = db.Column(db.TEXT)
    symbol_3 = db.Column(db.TEXT)
    symbol_4 = db.Column(db.TEXT)
    symbol_5 = db.Column(db.TEXT)
    event_1 = db.Column(db.TEXT)
    event_2 = db.Column(db.TEXT)
    event_3 = db.Column(db.TEXT)
    event_4 = db.Column(db.TEXT)
    event_5 = db.Column(db.TEXT)
    genre = relationship("genre_sql", back_populates="artgen")


class artgenstyle_sql(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    art_style = db.Column(db.String(255), nullable=False)
    gen_style = db.Column(db.String(255), nullable=True)


class artgenurl_sql(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.VARCHAR(255), nullable=False)
    genre_name = db.Column(db.VARCHAR(255), nullable=True)
    art_style = db.Column(db.VARCHAR(255), nullable=True)
    random_attribute = db.Column(db.VARCHAR(255), nullable=True)
    prompt = db.Column(db.VARCHAR(255), nullable=True)
    playlist_id = db.Column(db.VARCHAR(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class genre_sql(db.Model):
    genre = db.Column(db.VARCHAR(50), primary_key=True)
    sim_genres = db.Column(db.TEXT, nullable=True)
    sim_weights = db.Column(db.TEXT, nullable=True)
    opp_genres = db.Column(db.TEXT, nullable=True)
    opp_weights = db.Column(db.TEXT, nullable=True)
    spotify_url = db.Column(db.TEXT, nullable=True)
    color_hex = db.Column(db.TEXT, nullable=True)
    color_rgb = db.Column(db.TEXT, nullable=True)
    x = db.Column(db.Float, nullable=True)
    y = db.Column(db.Float, nullable=True)
    closest_stat_genres = db.Column(db.TEXT, nullable=True)
    artgen = relationship("artgen_sql", back_populates="genre")
