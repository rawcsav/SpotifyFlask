from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import Optional


class RecommendationsForm(FlaskForm):
    track_seeds = StringField("Track Seeds", validators=[Optional()])
    artist_seeds = StringField("Artist Seeds", validators=[Optional()])
    limit = IntegerField("Limit", default=5)
    popularity_slider = StringField("Popularity Slider")
    energy_slider = StringField("Energy Slider")
    instrumentalness_slider = StringField("Instrumentalness Slider")
    tempo_slider = StringField("Tempo Slider")
    danceability_slider = StringField("Danceability Slider")
    valence_slider = StringField("Valence Slider")
    submit = SubmitField("Submit")
