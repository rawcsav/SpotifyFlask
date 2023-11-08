from datetime import datetime
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, validates

db = SQLAlchemy()


class UserData(db.Model):
    spotify_user_id = db.Column(db.VARCHAR(255), primary_key=True, index=True)
    top_tracks = db.Column(db.JSON, nullable=True)
    top_artists = db.Column(db.JSON, nullable=True)
    all_artists_info = db.Column(db.JSON, nullable=True)
    audio_features = db.Column(db.JSON, nullable=True)
    genre_specific_data = db.Column(db.JSON, nullable=True)
    sorted_genres_by_period = db.Column(db.JSON, nullable=True)
    recent_tracks = db.Column(db.JSON, nullable=True)
    playlist_info = db.Column(db.JSON, nullable=True)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    api_key_encrypted = db.Column(db.VARCHAR(255), nullable=True)
    isDarkMode = db.Column(db.Boolean, nullable=True)


class artist_sql(db.Model):
    id = db.Column(db.String(100), primary_key=True, index=True)
    name = db.Column(db.VARCHAR(255))
    external_url = db.Column(db.VARCHAR(255))
    followers = db.Column(db.Integer)
    genres = db.Column(db.VARCHAR(255))
    images = db.Column(db.JSON)
    popularity = db.Column(db.Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class features_sql(db.Model):
    id = db.Column(db.VARCHAR(255), primary_key=True, index=True)
    danceability = db.Column(db.Float)
    energy = db.Column(db.Float)
    key = db.Column(db.Integer)
    loudness = db.Column(db.Float)
    mode = db.Column(db.Integer)
    speechiness = db.Column(db.Float)
    acousticness = db.Column(db.Float)
    instrumentalness = db.Column(db.Float)
    liveness = db.Column(db.Float)
    valence = db.Column(db.Float)
    tempo = db.Column(db.Float)
    time_signature = db.Column(db.Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class playlist_sql(db.Model):
    id = db.Column(db.VARCHAR(255), primary_key=True, index=True)
    name = db.Column(db.VARCHAR(255))
    owner = db.Column(db.VARCHAR(255))
    cover_art = db.Column(db.VARCHAR(255))
    public = db.Column(db.Boolean)
    collaborative = db.Column(db.Boolean)
    total_tracks = db.Column(db.Integer)
    snapshot_id = db.Column(db.VARCHAR(255))
    tracks = db.Column(db.JSON)
    genre_counts = db.Column(db.JSON)
    top_artists = db.Column(db.JSON)
    feature_stats = db.Column(db.JSON)
    temporal_stats = db.Column(db.JSON)


class artgen_sql(db.Model):
    genre_name = db.Column(db.VARCHAR(50), db.ForeignKey('genre_sql.genre'), primary_key=True)
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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


class Songfull(db.Model):
    name = db.Column(db.String(150), nullable=False)
    artist = db.Column(db.String(150), nullable=False)
    id = db.Column(db.String(150), primary_key=True)
    artist_id = db.Column(db.String(150), nullable=False)
    album = db.Column(db.String(150))  # added
    release = db.Column(db.String(4))  # added
    image_url = db.Column(db.String(250))
    external_url = db.Column(db.String(250))
    spotify_preview_url = db.Column(db.String(250), nullable=False)
    popularity = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(50), nullable=False, index=True)
    current = db.Column(db.SmallInteger, default=0)
    played = db.Column(db.SmallInteger, default=0)

    def __repr__(self):
        return f"<Song {self.name} by {self.artist}>"


class Archive(db.Model):
    date_played = db.Column(db.Date, primary_key=True, nullable=False, index=True)
    general_track = db.Column(db.String(150), db.ForeignKey('songfull.id'))  # Added
    rock_track = db.Column(db.String(150), db.ForeignKey('songfull.id'))  # Added
    hiphop_track = db.Column(db.String(150), db.ForeignKey('songfull.id'))  # Added
    past_games = db.relationship('PastGame', backref='archive', lazy=True)

    general_song = db.relationship('Songfull', foreign_keys=[general_track])
    rock_song = db.relationship('Songfull', foreign_keys=[rock_track])
    hiphop_song = db.relationship('Songfull', foreign_keys=[hiphop_track])

    def __repr__(self):
        return f"<Archive on {self.date_played}>"


class PastGame(db.Model):
    user_id_or_session = db.Column(db.String(100), primary_key=True, nullable=False)
    date = db.Column(db.Date, primary_key=True, nullable=False, index=True)
    attempts_made_general = db.Column(db.Integer, default=0)
    attempts_made_rock = db.Column(db.Integer, default=0)
    attempts_made_hiphop = db.Column(db.Integer, default=0)
    correct_guess_general = db.Column(db.Boolean, default=False)
    correct_guess_rock = db.Column(db.Boolean, default=False)
    correct_guess_hiphop = db.Column(db.Boolean, default=False)
    archive_date = db.Column(db.Date, db.ForeignKey('archive.date_played'), nullable=False)

    def __repr__(self):
        return f"<PastGame on {self.date} for user/session {self.user_id_or_session}>"

    @validates('attempts_made_general', 'attempts_made_rock', 'attempts_made_hiphop')
    def validate_attempts(self, key, value):
        if value < 0 or value > 6:
            raise ValueError(f"{key} should be between 0 and 6 inclusive.")
        return value


class CurrentGame(db.Model):
    user_id_or_session = db.Column(db.String(100), primary_key=True, nullable=False)
    current_genre = db.Column(db.String(50), default='General')
    guesses_left = db.Column(db.Integer, default=6)
    date = db.Column(db.Date, nullable=False, default=func.current_date())
    archive_date = db.Column(db.Date, db.ForeignKey('archive.date_played'), nullable=False)
    archive = db.relationship('Archive', backref='games')

    def __repr__(self):
        return f"<CurrentGame on {self.date} for user/session {self.user_id_or_session}>"

    @validates('guesses_left')
    def validate_guesses_left(self, key, value):
        if value < 0:
            raise ValueError(f"{key} should not be less than 0.")
        return value


artgen_dicts = [{
                    "art_style": "Abstract Expressionist painting; Spontaneous brushwork; bold colors; and large canvases; as seen in Jackson Pollock's drip paintings",
                    "gen_style": "vivid"},
                {
                    "art_style": "Abstract Minimalism; Geometric shapes and monochromatic color schemes focusing on form and space; as in the works of Donald Judd",
                    "gen_style": "natural"},
                {
                    "art_style": "Aesthetic Movement; Emphasis on beauty and form with intricate designs and often a sense of romantic escapism",
                    "gen_style": "natural"},
                {
                    "art_style": "Agitprop Art; Striking images and slogans designed to inspire and motivate political action or solidarity",
                    "gen_style": "vivid"},
                {
                    "art_style": "Alexander Rodchenko; Bold geometric shapes and photomontage in Constructivist propaganda; using sharp angles and strong contrasts",
                    "gen_style": "vivid"},
                {
                    "art_style": "Alfred Sisley; Impressionist landscapes with a focus on light and atmosphere; often depicting the French countryside",
                    "gen_style": "natural"},
                {
                    "art_style": "Amedeo Modigliani; Stylized portraits with elongated faces and figures; characterized by a sense of elegance and simplicity",
                    "gen_style": "natural"},
                {
                    "art_style": "American Pop Art; Bold colors and imagery from popular culture; often with a satirical or critical edge; as seen in Andy Warhol's 'Campbell's Soup Cans'",
                    "gen_style": "vivid"},
                {
                    "art_style": "American Transcendentalism; Art inspired by nature and the connection between the spiritual and the material; often with a serene quality",
                    "gen_style": "natural"},
                {
                    "art_style": "American War Posters; Bold and patriotic designs encouraging support and unity; often with strong calls to action",
                    "gen_style": "vivid"},
                {
                    "art_style": "Ancient Egyptian mural; Wall paintings in tombs and temples with a flat and stylized look; depicting gods; pharaohs; and daily life",
                    "gen_style": "natural"},
                {
                    "art_style": "Ancient Egyptian papyrus; Manuscripts with hieroglyphics and illustrations; often depicting religious or funerary scenes",
                    "gen_style": "natural"},
                {
                    "art_style": "Ancient Greek Pottery; Black-figure and red-figure ceramics with mythological and everyday scenes; characterized by precise line work and figures in profile",
                    "gen_style": "natural"},
                {
                    "art_style": "Ancient Roman mosaic; Tesserae arranged to create detailed scenes; often with intricate patterns and a sense of depth",
                    "gen_style": "natural"},
                {
                    "art_style": "Ancient Roman painting; Wall paintings with architectural motifs and vibrant colors; creating an illusionistic sense of space",
                    "gen_style": "natural"},
                {
                    "art_style": "Andy Warhol; Pop Art with silkscreen prints of celebrities and consumer goods; using repetition and bright; flat colors",
                    "gen_style": "vivid"},
                {
                    "art_style": "Art Deco; Bold symmetry; streamlined shapes; and luxurious materials; visible in architecture and decorative objects",
                    "gen_style": "vivid"},
                {
                    "art_style": "Art Informel; Abstract works with an emphasis on texture and materiality; often appearing spontaneous and unstructured",
                    "gen_style": "vivid"},
                {
                    "art_style": "Art Nouveau; Flowing lines and natural forms; often incorporating floral motifs and elegant; sinuous curves",
                    "gen_style": "vivid"},
                {
                    "art_style": "Artemisia Gentileschi; Baroque paintings with dramatic use of light and shadow; often depicting powerful women from history and mythology",
                    "gen_style": "vivid"},
                {
                    "art_style": "Arts and Crafts Movement; Emphasis on handcrafted quality and natural motifs; with a focus on the beauty of materials and workmanship",
                    "gen_style": "natural"},
                {
                    "art_style": "Ashcan School; Realistic scenes of urban life; with gritty depictions of the streets and inhabitants of New York",
                    "gen_style": "natural"},
                {
                    "art_style": "Auguste Rodin; Sculptures with a sense of movement and emotional intensity; as seen in 'The Thinker' and 'The Kiss'",
                    "gen_style": "vivid"},
                {
                    "art_style": "Autochrome; Early color photographs with a distinct grain and a somewhat muted but still vibrant color palette",
                    "gen_style": "natural"},
                {
                    "art_style": "Barbara Kruger; Conceptual Art with bold text and imagery; often in black; white; and red; critiquing culture and power structures",
                    "gen_style": "vivid"},
                {
                    "art_style": "Baroque painting; Intense contrasts between light and dark; dynamic compositions; and a sense of drama; as in Caravaggio's works",
                    "gen_style": "vivid"},
                {
                    "art_style": "Bayeux Tapestry; Embroidered narrative featuring the Battle of Hastings with figures in motion and detailed storytelling",
                    "gen_style": "natural"},
                {
                    "art_style": "Black Panther Posters; Powerful graphics and slogans promoting civil rights; often with a strong; militant aesthetic",
                    "gen_style": "vivid"},
                {
                    "art_style": "Bridget Riley; Op Art with optical patterns creating visual effects of movement and vibration",
                    "gen_style": "vivid"},
                {
                    "art_style": "British Empire War Art; Recruitment and motivational posters with bold lettering and patriotic imagery",
                    "gen_style": "vivid"},
                {
                    "art_style": "Brutalist Art; Raw concrete structures and a focus on geometric forms; emphasizing function and material",
                    "gen_style": "vivid"},
                {
                    "art_style": "Byzantine Mosaics; Religious scenes with gold backgrounds and a flat; iconic style; often in churches and basilicas",
                    "gen_style": "natural"},
                {
                    "art_style": "Caravaggio; Dramatic use of chiaroscuro and realistic depictions of human figures in religious and mythological paintings",
                    "gen_style": "vivid"},
                {
                    "art_style": "Cave painting; Prehistoric art featuring animals and human figures; often in silhouette; using earthy pigments",
                    "gen_style": "natural"},
                {
                    "art_style": "Chinese Cultural Revolution Art; Propaganda posters with strong; graphic designs promoting Maoist ideology",
                    "gen_style": "vivid"},
                {
                    "art_style": "Christian icon painting; Religious art with a focus on sacred figures; characterized by a stylized and non-naturalistic portrayal; often with gold backgrounds",
                    "gen_style": "natural"},
                {
                    "art_style": "Claude Monet; Impressionism with a focus on capturing the fleeting effects of light and color; as seen in his 'Water Lilies' series",
                    "gen_style": "natural"},
                {
                    "art_style": "Collage Art; Assembling various forms and mediums such as paper; photographs; and fabric; creating layered and textured compositions",
                    "gen_style": "vivid"},
                {
                    "art_style": "Color Field Painting; Large expanses of color with little to no texture or form; emphasizing the flatness and the emotional power of color",
                    "gen_style": "natural"},
                {
                    "art_style": "Constructivism; Artistic and architectural philosophy with a focus on materials; geometric forms; and a sense of functionalism",
                    "gen_style": "vivid"},
                {
                    "art_style": "Constructivist Propaganda; Utilizing geometric shapes and bold typography to convey political messages and values in a clear; striking manner",
                    "gen_style": "vivid"},
                {
                    "art_style": "Cuban Revolution Art; Propaganda art with bold imagery and colors; promoting revolutionary messages and celebrating leaders like Che Guevara",
                    "gen_style": "vivid"},
                {
                    "art_style": "Cubist painting; Fragmenting subjects into geometric shapes and presenting multiple viewpoints simultaneously; as in Picasso's 'Les Demoiselles d'Avignon'",
                    "gen_style": "vivid"},
                {
                    "art_style": "Dada artwork; Challenging traditional art conventions with absurdity and irony; often through collage; readymades; and performance",
                    "gen_style": "natural"},
                {
                    "art_style": "Daguerreotype; First publicly available photographic process producing a single; highly detailed image on a silvered copper plate",
                    "gen_style": "natural"},
                {
                    "art_style": "Damien Hirst; Contemporary Art with installations often exploring themes of life and death; as seen in his work 'The Physical Impossibility of Death in the Mind of Someone Living'",
                    "gen_style": "vivid"},
                {
                    "art_style": "De Stijl; Pure abstraction with primary colors; black and white; and straight lines; seeking universal harmony; as in Mondrian's compositions",
                    "gen_style": "natural"},
                {
                    "art_style": "Decorative Minoan mural; Frescoes with vibrant colors and naturalistic shapes; depicting scenes of nature; sport; and ritual",
                    "gen_style": "natural"},
                {
                    "art_style": "Diego Velázquez; Baroque master with a focus on realistic depiction of human figures and a masterful use of light and shadow",
                    "gen_style": "natural"},
                {
                    "art_style": "Disposable camera; Photography with a simple; often grainy aesthetic due to the use of basic cameras with fixed settings",
                    "gen_style": "natural"},
                {
                    "art_style": "Donatello; Italian Renaissance sculpture with a focus on naturalism and expression in works such as the bronze 'David'",
                    "gen_style": "natural"},
                {
                    "art_style": "Double exposure; Photography technique combining two different images into a single frame; creating an ethereal and dreamlike effect",
                    "gen_style": "vivid"},
                {
                    "art_style": "Drone photography; Capturing landscapes and scenes from an aerial perspective; often with a high level of detail and sweeping views",
                    "gen_style": "natural"},
                {
                    "art_style": "Dutch Realism; Precise detail and everyday subjects; focusing on the beauty and dignity of ordinary life; as seen in Vermeer's domestic interiors",
                    "gen_style": "natural"},
                {
                    "art_style": "Ed Ruscha; Pop Art with a strong emphasis on typography and the urban landscape; often with a deadpan and conceptual approach",
                    "gen_style": "vivid"},
                {
                    "art_style": "Edvard Munch; Symbolism and Expressionism with emotionally charged works such as 'The Scream;' featuring intense color and dramatic composition",
                    "gen_style": "vivid"},
                {
                    "art_style": "Edward Burne-Jones; Pre-Raphaelite Brotherhood with paintings featuring romantic and mythological themes; characterized by their dreamlike quality",
                    "gen_style": "natural"},
                {
                    "art_style": "Edward Hopper; American Realism with paintings capturing the solitude of modern life; as seen in 'Nighthawks;' with a focus on light and composition",
                    "gen_style": "natural"},
                {
                    "art_style": "Egon Schiele; Expressionism with a focus on the human body in distorted and emotional poses; often with a raw and graphic line quality",
                    "gen_style": "vivid"},
                {
                    "art_style": "Egyptian Hieroglyphics; Symbolic writing system featuring pictographs used in art and architecture; often accompanying depictions of gods and pharaohs",
                    "gen_style": "natural"},
                {
                    "art_style": "El Greco; Spanish Renaissance and Mannerism with elongated figures and intense emotion; as seen in his religious paintings",
                    "gen_style": "vivid"},
                {
                    "art_style": "El Lissitzky; Russian artist with a focus on geometric abstraction and bold use of color in propaganda posters and Suprematist compositions",
                    "gen_style": "vivid"},
                {
                    "art_style": "Elizabethan portrait; Opulence and symbolism with richly adorned figures; often with emblematic objects indicating status or character",
                    "gen_style": "vivid"},
                {
                    "art_style": "English Landscape Painting; Pastoral scenes with a focus on the harmony between nature and man; often imbued with a sense of tranquility",
                    "gen_style": "natural"},
                {
                    "art_style": "Expressionist painting; Conveying emotional experience through distorted forms and vivid colors; as seen in works by artists like Munch and Kirchner",
                    "gen_style": "vivid"},
                {
                    "art_style": "Fashion photography; Often high-contrast and stylized images that emphasize the design and aesthetic of clothing and models",
                    "gen_style": "vivid"},
                {
                    "art_style": "Fauvist painting; Bold and non-naturalistic use of color to convey emotion; as seen in Matisse's 'Woman with a Hat'",
                    "gen_style": "vivid"},
                {
                    "art_style": "Fish-eye lens; Photography with an extremely wide-angle lens; creating a hemispherical image and a distinctive convex appearance",
                    "gen_style": "vivid"},
                {
                    "art_style": "Flash photography; Often creating stark lighting with sharp shadows; highlighting details and textures",
                    "gen_style": "vivid"},
                {
                    "art_style": "Francisco Goya; Romanticism with a range of works from royal portraits to dark and dramatic scenes like 'The Third of May 1808'",
                    "gen_style": "vivid"},
                {
                    "art_style": "Frida Kahlo; Surrealism and Mexican Art with self-portraits that incorporate symbolism and vivid colors to explore identity and suffering",
                    "gen_style": "vivid"},
                {
                    "art_style": "Futurism; Emphasizing themes of speed; technology; and industrial progress with dynamic compositions and a sense of movement",
                    "gen_style": "vivid"},
                {
                    "art_style": "Georgia O'Keeffe; American Modernism with large-scale flowers; skyscrapers; and Southwestern landscapes; focusing on the essential forms and colors",
                    "gen_style": "natural"},
                {
                    "art_style": "Gilded Codex; Manuscripts embellished with gold leaf; often accompanied by elaborate illustrations and ornate lettering",
                    "gen_style": "natural"},
                {
                    "art_style": "Giotto di Bondone; Italian Gothic with a move towards naturalism and three-dimensionality in frescoes; as seen in the Scrovegni Chapel",
                    "gen_style": "natural"},
                {
                    "art_style": "Graffiti Art; Street art with free-hand styles; often with vibrant colors and bold lines; reflecting urban culture and sometimes carrying social messages",
                    "gen_style": "vivid"},
                {
                    "art_style": "Grant Wood; Regionalism with paintings that depict rural American life with a sense of nostalgia and idealism; as in 'American Gothic'",
                    "gen_style": "natural"},
                {
                    "art_style": "Gustav Klimt; Symbolism and Vienna Secession with ornamental and sensual paintings; often using gold leaf; as in 'The Kiss'",
                    "gen_style": "vivid"},
                {
                    "art_style": "Gustave Courbet; Realism focusing on depicting subjects truthfully without idealization; as seen in works like 'The Stone Breakers'",
                    "gen_style": "natural"},
                {
                    "art_style": "Hans Holbein the Younger; German Renaissance artist known for his highly detailed and realistic portraits of figures such as Henry VIII",
                    "gen_style": "natural"},
                {
                    "art_style": "Henri Matisse; Fauvism and Modernism with bold colors and simple forms; as seen in works like 'The Dance'",
                    "gen_style": "vivid"},
                {
                    "art_style": "Henri de Toulouse-Lautrec; Post-Impressionism with a focus on the colorful and theatrical life of Paris; including posters and illustrations of the Moulin Rouge",
                    "gen_style": "vivid"},
                {
                    "art_style": "Hieronymus Bosch; Early Netherlandish painter with surreal imagery in triptychs; depicting heaven and hell with intricate detail and fantastical creatures",
                    "gen_style": "vivid"},
                {
                    "art_style": "High Renaissance painting; Characterized by idealized beauty; balanced composition; and a focus on classical subject matter; as seen in the works of Michelangelo and Raphael",
                    "gen_style": "natural"},
                {
                    "art_style": "Humanist manuscript; Renaissance illumination with detailed and decorative designs; often incorporating classical and biblical motifs",
                    "gen_style": "natural"},
                {
                    "art_style": "Illuminated Manuscripts; Medieval European texts hand-decorated with intricate designs; often using gold leaf and vivid colors",
                    "gen_style": "natural"},
                {
                    "art_style": "Impressionist painting; Capturing the impression of light and color with loose; visible brushstrokes and a focus on everyday scenes; as in Monet's water lilies",
                    "gen_style": "natural"},
                {
                    "art_style": "International Gothic painting; Late 14th-century art with elegant figures; vibrant colors; and intricate detail; often with religious themes",
                    "gen_style": "natural"},
                {
                    "art_style": "J.M.W. Turner; English Romantic painter known for his expressive use of color and light in landscapes and seascapes; creating atmospheric effects",
                    "gen_style": "vivid"},
                {
                    "art_style": "Jackson Pollock; Abstract Expressionism with his drip paintings; creating energetic and intricate webs of color and line",
                    "gen_style": "vivid"},
                {
                    "art_style": "James Whistler; American art with a subtle and tonal approach; as seen in 'Whistler's Mother;' focusing on composition and color over subject",
                    "gen_style": "natural"},
                {
                    "art_style": "Jan Van Eyck; Flemish Renaissance artist known for his detailed and naturalistic oil paintings with rich textures; as in 'The Arnolfini Portrait'",
                    "gen_style": "natural"},
                {
                    "art_style": "Jan Vermeer; Dutch Golden Age painter with a focus on domestic interior scenes; characterized by a masterful use of light and detail",
                    "gen_style": "natural"},
                {
                    "art_style": "Jasper Johns; Abstract Expressionism and Pop Art with works that incorporate symbols like flags and targets; questioning the nature of art",
                    "gen_style": "vivid"},
                {
                    "art_style": "Jean-Michel Basquiat; Neo-Expressionism and Primitivism with raw; graffiti-like works often commenting on race and society",
                    "gen_style": "vivid"},
                {
                    "art_style": "Jeff Koons; Neo-pop with his polished sculptures that play with themes of consumerism and kitsch; such as the 'Balloon Dog' series",
                    "gen_style": "vivid"},
                {
                    "art_style": "Joan Miró; Surrealism and Dada with his playful abstract compositions featuring biomorphic shapes and bold colors",
                    "gen_style": "vivid"},
                {
                    "art_style": "Johannes Vermeer; Dutch Golden Age artist known for his tranquil scenes of domestic life and exquisite use of light; as in 'Girl with a Pearl Earring'",
                    "gen_style": "natural"},
                {
                    "art_style": "John Singer Sargent; Realism and portrait painting with his elegant and sophisticated depictions of high society; characterized by fluid brushwork",
                    "gen_style": "natural"},
                {
                    "art_style": "Josef Albers; Abstract Art with his 'Homage to the Square' series exploring color theory and geometric abstraction",
                    "gen_style": "natural"},
                {
                    "art_style": "Katsushika Hokusai; Ukiyo-e and Japanese art with his 'Thirty-Six Views of Mount Fuji' series; including the famous 'The Great Wave off Kanagawa'",
                    "gen_style": "natural"},
                {
                    "art_style": "Kazimir Malevich; Suprematism with his focus on basic geometric forms and a limited color palette; as in 'Black Square'",
                    "gen_style": "natural"},
                {
                    "art_style": "Keith Haring; Pop Art and graffiti with his instantly recognizable bold lines and active figures; often with social activism messages",
                    "gen_style": "vivid"},
                {
                    "art_style": "Leonardo da Vinci; Italian Renaissance master with works like 'The Last Supper' and 'Mona Lisa;' showcasing his mastery of anatomy and perspective",
                    "gen_style": "natural"},
                {
                    "art_style": "Lomography; Photography characterized by its dreamy; vibrant; and sometimes lo-fi aesthetic; often associated with the Lomo LC-A camera",
                    "gen_style": "natural"},
                {
                    "art_style": "Long exposure; Photography technique that captures extended periods of time; often resulting in blurred motion and unique lighting effects",
                    "gen_style": "natural"},
                {
                    "art_style": "Lucian Freud; Expressionism and portraiture with a focus on the texture of skin and the human form; creating intense and psychological works",
                    "gen_style": "vivid"},
                {
                    "art_style": "Luminism; American landscape painting style characterized by attention to detail and the effects of light on the environment; creating a tranquil and luminous quality",
                    "gen_style": "natural"},
                {
                    "art_style": "M. C. Escher; Graphic Artist known for his mathematically inspired woodcuts; lithographs; and mezzotints with impossible constructions and explorations of infinity",
                    "gen_style": "vivid"},
                {
                    "art_style": "Macro photography; Close-up photography that captures small subjects in great detail; often revealing textures and patterns not visible to the naked eye",
                    "gen_style": "natural"},
                {
                    "art_style": "Mannerist painting; Elongated forms and complex compositions with an artificial elegance and exaggerated proportions; as in the works of El Greco",
                    "gen_style": "vivid"},
                {
                    "art_style": "Marc Chagall; Combining Cubism and Expressionism with his whimsical and dreamlike scenes; often incorporating elements of folklore and religion",
                    "gen_style": "vivid"},
                {
                    "art_style": "Rococo painting; Light colors; playful themes; and ornate detail with subjects often from the aristocracy; depicted in leisurely scenes with soft; pastel tones and curvaceous lines",
                    "gen_style": "natural"},
                {
                    "art_style": "Romanesque painting; 12th-century frescoes characterized by their religious themes; flat figures; and bold colors; often found in the interiors of churches",
                    "gen_style": "natural"},
                {
                    "art_style": "Romantic painting; Focused on emotion and individualism with dramatic contrasts; expressive brushwork; and a preference for grandiose landscapes and historical or mythological scenes",
                    "gen_style": "vivid"},
                {
                    "art_style": "Rosalba Carriera; Known for her soft and delicate pastel portraits; often of women; with light; feathery strokes capturing the ephemeral beauty of her subjects",
                    "gen_style": "natural"},
                {
                    "art_style": "Roy Lichtenstein; Bold pop art works with primary colors; Ben-Day dots; and comic strip influences that often incorporate a sense of irony",
                    "gen_style": "vivid"},
                {
                    "art_style": "Russian Constructivism; Utilized geometric shapes and industrial materials to reflect modernity; with artworks that often had a three-dimensional aspect and were intertwined with political ideology",
                    "gen_style": "vivid"},
                {
                    "art_style": "Salvador Dalí; Surrealist works with bizarre dreamscapes; melting clocks; and distorted figures; using precise; realistic detail in a fantastical context",
                    "gen_style": "vivid"},
                {
                    "art_style": "Sandro Botticelli; Italian Renaissance paintings with flowing lines; ethereal figures; and mythological as well as religious subjects; like The Birth of Venus",
                    "gen_style": "natural"},
                {
                    "art_style": "Shepard Fairey; Graphic works with a strong; clear visual impact; using bold colors and a style that nods to propaganda art; with a mix of street art aesthetic",
                    "gen_style": "vivid"},
                {
                    "art_style": "Silk Road Textiles; Richly decorated fabrics that reflect the cultural exchange between East and West; with intricate patterns and vibrant colors",
                    "gen_style": "natural"},
                {
                    "art_style": "Social Realism; Artworks depicting everyday life and social issues with a focus on the working class; often with a gritty; realistic aesthetic",
                    "gen_style": "natural"},
                {
                    "art_style": "Soviet Socialist Realism; Idealized depictions of communist values; glorifying workers and peasants in a realistic yet staged manner",
                    "gen_style": "natural"},
                {
                    "art_style": "Spanish Mannerism; Characterized by elongated figures; exaggerated poses; and heightened emotion; often with a strong use of chiaroscuro",
                    "gen_style": "vivid"},
                {
                    "art_style": "Suprematism; Focused on basic geometric forms like squares and circles in a limited range of colors; emphasizing the purity of shape",
                    "gen_style": "natural"},
                {
                    "art_style": "Surrealist painting; Dreamlike scenes with unexpected juxtapositions and fantastical elements; often with a high level of detail in a realistic rendering",
                    "gen_style": "vivid"},
                {
                    "art_style": "Surveillance & CCTV; Often manifests in art as a commentary on privacy and society; with depictures that can range from stark and realistic to abstract interpretations",
                    "gen_style": "natural"},
                {
                    "art_style": "Symbolism; Art that uses symbolic imagery and mythological references to express ideas and emotions; with a mystical or dreamlike quality",
                    "gen_style": "natural"},
                {
                    "art_style": "Takashi Murakami; Superflat style combining traditional Japanese art with contemporary pop culture; often featuring bold colors and flattened graphic imagery",
                    "gen_style": "vivid"},
                {
                    "art_style": "Telephoto lens; Photography that brings distant subjects closer; often used to compress space and isolate subjects with a shallow depth of field",
                    "gen_style": "vivid"},
                {
                    "art_style": "Thomas Cole; American Romantic landscapes that are grand and expressive; often with dramatic lighting and a sense of the sublime in nature",
                    "gen_style": "natural"},
                {
                    "art_style": "Tintoretto; Dynamic compositions with dramatic lighting and vigorous brushwork; blending Venetian color with the energetic movement of Mannerism",
                    "gen_style": "vivid"},
                {
                    "art_style": "Titian; Italian Renaissance paintings known for their rich color palettes and masterful use of chiaroscuro; often depicting religious and mythological themes",
                    "gen_style": "natural"},
                {
                    "art_style": "Tonalism; Landscapes with a muted color palette; emphasizing mood and atmosphere over detailed representation; often with an overall tone of colored atmosphere or mist",
                    "gen_style": "natural"},
                {
                    "art_style": "Traditional Chinese Calligraphy; The art of writing Chinese characters with brush and ink; emphasizing the flow; energy; and rhythm of the lines",
                    "gen_style": "natural"},
                {
                    "art_style": "Trench Art; Objects made from war materials; like shell casings; with engraved or embossed designs; often reflecting the soldiers' experiences or commemorating battles",
                    "gen_style": "natural"},
                {
                    "art_style": "Utagawa Hiroshige; Ukiyo-e prints with a focus on landscapes; characterized by a masterful use of perspective and color; often depicting the changing seasons and famous places in Japan",
                    "gen_style": "natural"},
                {
                    "art_style": "Utopian and Art; Art connected with idealistic social visions; often depicting peaceful; harmonious communities and idyllic landscapes",
                    "gen_style": "natural"},
                {
                    "art_style": "Victorian Era Paintings; Reflecting the values and aesthetics of 19th-century Britain with detailed; often moralizing scenes from history; literature; and everyday life",
                    "gen_style": "natural"},
                {
                    "art_style": "Vincent van Gogh; Post-Impressionist works with bold; swirling brushstrokes and vibrant colors; expressing intense emotions through landscapes; still lifes; and portraits",
                    "gen_style": "vivid"},
                {
                    "art_style": "WPA Posters; Bold and stylized promotional posters created by the Works Progress Administration; often with strong; simple graphics and messages",
                    "gen_style": "vivid"},
                {
                    "art_style": "Wassily Kandinsky; Abstract compositions with vibrant colors and geometric forms; aiming to evoke emotion and spirituality through non-representational art",
                    "gen_style": "vivid"},
                {
                    "art_style": "Willem de Kooning; Abstract Expressionist works with energetic brushwork and abstracted figures; often with a sense of movement and emotional intensity",
                    "gen_style": "vivid"},
                {
                    "art_style": "William Blake; Romantic prints and paintings with mystical and visionary themes; often combining text and image with a unique hand-colored technique",
                    "gen_style": "natural"},
                {
                    "art_style": "Yayoi Kusama; Known for her polka dots and mirrored rooms; creating immersive environments and sculptures that play with the concept of infinite space",
                    "gen_style": "vivid"},
                {
                    "art_style": "Yves Klein; Nouveau réalisme works featuring monochrome paintings; especially in his signature International Klein Blue; and performance art pieces",
                    "gen_style": "vivid"},
                {
                    "art_style": "Zaha Hadid; Deconstructivist architecture with flowing lines and futuristic shapes; pushing the boundaries of form and space in her designs",
                    "gen_style": "vivid"},
                {
                    "art_style": "Édgar Degas; Impressionist and Realist works focusing on the movement and form of the human body; particularly dancers; with a candid; snapshot quality",
                    "gen_style": "natural"},
                {
                    "art_style": "Édouard Manet; Paintings that bridged Realism and Impressionism with a modern approach to subject matter and technique; often challenging traditional composition",
                    "gen_style": "natural"},
                {
                    "art_style": "Élisabeth Vigée Le Brun; Portraits blending Rococo softness with Neoclassical structure; capturing the elegance and sophistication of her sitters",
                    "gen_style": "natural"},
                {
                    "art_style": "Marcel Duchamp; Dada and Conceptual Art with works like 'Fountain' that challenge the conventional understanding of art; often incorporating readymade objects",
                    "gen_style": "natural"},
                {
                    "art_style": "Mark Rothko; Abstract Expressionism and Color Field paintings with large; soft-edged blocks of color; evoking emotional responses",
                    "gen_style": "natural"},
                {
                    "art_style": "Marlene Dumas; Expressionistic portraiture with loose; fluid brushwork; often exploring themes of race; sexuality; and social identity",
                    "gen_style": "natural"},
                {
                    "art_style": "Mary Cassatt; Impressionism focusing on the intimate moments of women and children; with soft brushstrokes and a light palette",
                    "gen_style": "natural"},
                {
                    "art_style": "Max Ernst; Dadaism and Surrealism with fantastical imagery; often using techniques like frottage and decalcomania to create dreamlike scenes",
                    "gen_style": "vivid"},
                {
                    "art_style": "Medieval Tapestry; Woven narratives with intricate detail and rich colors; depicting historical and mythological scenes",
                    "gen_style": "natural"},
                {
                    "art_style": "Michelangelo Buonarroti; Italian Renaissance masterpieces like the Sistine Chapel ceiling; with highly detailed; muscular human forms",
                    "gen_style": "vivid"},
                {
                    "art_style": "Minimalist painting; Emphasizing simplicity and purity of form and color; often with geometric shapes and monochromatic palettes",
                    "gen_style": "natural"},
                {
                    "art_style": "Mozarabic art; 10th-century Leon with a mixture of Christian and Islamic artistic influences; featuring intricate patterns and calligraphy",
                    "gen_style": "natural"},
                {
                    "art_style": "Mughal Paintings; Indian Subcontinent art with detailed court scenes and nature; rich in color and intricate patterns",
                    "gen_style": "natural"},
                {
                    "art_style": "Neo-Expressionism; Intense; raw imagery with vigorous brushwork and a return to figurative painting in the late 20th century",
                    "gen_style": "vivid"},
                {
                    "art_style": "Neoclassical painting; Strong lines; formal composition; and often classical themes; with a focus on harmony and restraint",
                    "gen_style": "natural"},
                {
                    "art_style": "New Objectivity; German art movement with sharp; precise lines and a sober view of the modern world; often with a social critique",
                    "gen_style": "natural"},
                {
                    "art_style": "Norman Rockwell; American Realism and Illustration with heartwarming and idealized visions of everyday life; often in Saturday Evening Post covers",
                    "gen_style": "natural"},
                {
                    "art_style": "North Korean Propaganda Art; State-commissioned artworks with a bold style; promoting the regime's ideology and leaders with often exaggerated heroism",
                    "gen_style": "vivid"},
                {
                    "art_style": "Northern Renaissance; Detailed religious and secular works with attention to surface detail and texture; like those by Jan van Eyck",
                    "gen_style": "natural"},
                {
                    "art_style": "Nuremberg Chronicle; 1493 illustrations with woodcuts depicting biblical and historical scenes in a detailed and narrative style",
                    "gen_style": "natural"},
                {
                    "art_style": "Op Art; Optical illusions created with abstract patterns and contrasting colors that play with visual perception",
                    "gen_style": "vivid"},
                {
                    "art_style": "Pablo Picasso; Cubism and Surrealism with fragmented forms and unusual perspectives; as in 'Les Demoiselles d'Avignon'",
                    "gen_style": "vivid"},
                {
                    "art_style": "Paul Cézanne; Post-Impressionism with a focus on geometric simplification of nature and still lifes; often seen as a bridge to Cubism",
                    "gen_style": "natural"},
                {
                    "art_style": "Paul Gauguin; Post-Impressionism and Primitivism with bold colors and simplified forms; often depicting Tahitian life",
                    "gen_style": "natural"},
                {
                    "art_style": "Persian Miniatures; Detailed narrative scenes with vibrant colors and intricate designs; often illustrating literature and poetry",
                    "gen_style": "natural"},
                {
                    "art_style": "Peter Paul Rubens; Baroque paintings with dynamic compositions; rich color; and a sense of movement; often with mythological or historical themes",
                    "gen_style": "vivid"},
                {
                    "art_style": "Photorealism; Paintings that mimic high-resolution photography with incredible detail and a focus on light and reflection",
                    "gen_style": "vivid"},
                {
                    "art_style": "Piet Mondrian; De Stijl and Abstract Art with grid-based paintings using primary colors and black lines; emphasizing pure abstraction",
                    "gen_style": "natural"},
                {
                    "art_style": "Pinhole photography; Camera obscura technique producing soft-focus images with a dreamy quality due to the lack of a lens",
                    "gen_style": "natural"},
                {
                    "art_style": "Pixel Art; Early digital design with a blocky; grid-like aesthetic reminiscent of early video games",
                    "gen_style": "natural"},
                {
                    "art_style": "Polaroid; Instant photography known for its distinct color palette and border; often with a candid; snapshot feel",
                    "gen_style": "natural"},
                {
                    "art_style": "Pop Art; Mid to late 20th-century art with bold colors and imagery from popular culture and mass media; as seen in works by Andy Warhol",
                    "gen_style": "vivid"},
                {
                    "art_style": "Post-Impressionist painting; Exploring color and form with a personal expression that goes beyond Impressionist observation; as in works by Vincent van Gogh",
                    "gen_style": "vivid"},
                {
                    "art_style": "Postmodern artwork; Diverse styles and mediums that question traditional art concepts; often with irony or pastiche",
                    "gen_style": "vivid"},
                {
                    "art_style": "Precisionism; American 20th-century art with clean lines and smooth surfaces; focusing on industrial forms and geometric structures",
                    "gen_style": "natural"},
                {
                    "art_style": "Rachel Whiteread; Minimalism and Sculpture with casts of negative spaces and everyday objects; exploring themes of presence and absence",
                    "gen_style": "natural"},
                {
                    "art_style": "Raphael Sanzio; Italian Renaissance paintings with balanced composition and serene figures; as seen in 'The School of Athens'",
                    "gen_style": "natural"},
                {
                    "art_style": "Rayonism; Russian avant-garde art with dynamic abstract forms meant to express the sensation of rays of light",
                    "gen_style": "vivid"},
                {
                    "art_style": "Realist painting; Everyday life depicted with precise detail and a focus on the honest representation of the common people",
                    "gen_style": "natural"},
                {
                    "art_style": "Regionalism; American art depicting rural scenes of the Midwest during the Great Depression; with a focus on everyday life and the working class",
                    "gen_style": "natural"},
                {
                    "art_style": "Rembrandt van Rijn; Dutch Golden Age paintings with a mastery of light and shadow; creating depth and emotion in portraits and biblical scenes",
                    "gen_style": "natural"},
                {
                    "art_style": "Renaissance Humanism Art; Emphasis on classical learning and human achievement; with a focus on proportion; perspective; and human anatomy",
                    "gen_style": "natural"},
                {
                    "art_style": "René Magritte; Surrealism with witty and thought-provoking images that challenge observers' preconditioned perceptions of reality",
                    "gen_style": "vivid"},
                ]
