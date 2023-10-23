"""Added album and release to Songfull

Revision ID: 74e8b1b52a95
Revises: e72d9b80cd3e
Create Date: 2023-10-21 19:25:08.201041

"""
import csv

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '74e8b1b52a95'
down_revision = 'e72d9b80cd3e'
branch_labels = None
depends_on = None

from datetime import datetime
from app.database import Songfull  # Adjust the import path to your actual app structure


def convert_to_year(date_str):
    if len(date_str) == 4 and date_str.isdigit():  # If the string is already a year
        return date_str
    else:
        formats = ['%Y-%m-%d', '%Y-%m']  # The formats to try
        for fmt in formats:
            try:
                date = datetime.strptime(date_str, fmt)
                return date.strftime('%Y')
            except ValueError:
                pass
        raise ValueError(f"No known format to parse {date_str}")


def upgrade():
    op.execute(Songfull.__table__.delete())

    # Import data from CSV into Songfull
    with open('/Users/gavinmason/PycharmProjects/BotifyStats/app/data/top_tracks.csv', 'r') as csv_file:
        rows_to_insert = []
        reader = csv.DictReader(csv_file)
        for row in reader:
            rows_to_insert.append({
                'name': row['track'],
                'artist': row['artist'],
                'album': row['album'],
                'release': convert_to_year(row['release']),
                'id': row['track_id'],
                'artist_id': row['artist_id'],
                'image_url': row['cover_art'],
                'external_url': row['external_url'],
                'spotify_preview_url': row['preview_link'],
                'popularity': int(row['popularity']),
                'genre': row['genre'],
                'current': row['current'].lower() == 'false'
            })
        op.bulk_insert(Songfull.__table__, rows_to_insert)


def downgrade():
    with op.batch_alter_table('songfull', schema=None) as batch_op:
        batch_op.drop_column('release')
        batch_op.drop_column('album')
