from app import db
from app.models.mixins import TimestampMixin, generate_uuid


class ArtGen(db.Model):
    __tablename__ = "art_gen"
    genre_name = db.Column(db.String(50), db.ForeignKey("genre_stats.genre"), primary_key=True)
    place_1 = db.Column(db.Text)
    place_2 = db.Column(db.Text)
    place_3 = db.Column(db.Text)
    place_4 = db.Column(db.Text)
    place_5 = db.Column(db.Text)
    role_1 = db.Column(db.Text)
    role_2 = db.Column(db.Text)
    role_3 = db.Column(db.Text)
    role_4 = db.Column(db.Text)
    role_5 = db.Column(db.Text)
    item_1 = db.Column(db.Text)
    item_2 = db.Column(db.Text)
    item_3 = db.Column(db.Text)
    item_4 = db.Column(db.Text)
    item_5 = db.Column(db.Text)
    symbol_1 = db.Column(db.Text)
    symbol_2 = db.Column(db.Text)
    symbol_3 = db.Column(db.Text)
    symbol_4 = db.Column(db.Text)
    symbol_5 = db.Column(db.Text)
    event_1 = db.Column(db.Text)
    event_2 = db.Column(db.Text)
    event_3 = db.Column(db.Text)
    event_4 = db.Column(db.Text)
    event_5 = db.Column(db.Text)
    genre = db.relationship("GenreStat", back_populates="artgen")


class ArtGenStyle(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    art_style = db.Column(db.String(255), nullable=False)
    gen_style = db.Column(db.String(255), nullable=True)


class ArtGenUrl(db.Model, TimestampMixin):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    url = db.Column(db.String(255), nullable=False)
    genre_name = db.Column(db.String(255), nullable=True)
    art_style = db.Column(db.String(255), nullable=True)
    random_attribute = db.Column(db.String(255), nullable=True)
    prompt = db.Column(db.String(255), nullable=True)
    playlist_id = db.Column(db.String(255), nullable=False)


class GenreStat(db.Model):
    __tablename__ = "genre_stats"
    genre = db.Column(db.String(50), primary_key=True)
    sim_genres = db.Column(db.Text, nullable=True)
    sim_weights = db.Column(db.Text, nullable=True)
    opp_genres = db.Column(db.Text, nullable=True)
    opp_weights = db.Column(db.Text, nullable=True)
    spotify_url = db.Column(db.Text, nullable=True)
    color_hex = db.Column(db.Text, nullable=True)
    color_rgb = db.Column(db.Text, nullable=True)
    x = db.Column(db.Float, nullable=True)
    y = db.Column(db.Float, nullable=True)
    closest_stat_genres = db.Column(db.Text, nullable=True)
    artgen = db.relationship("ArtGen", back_populates="genre")
