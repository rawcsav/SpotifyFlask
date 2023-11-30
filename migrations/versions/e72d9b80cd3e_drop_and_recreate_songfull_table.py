"""Drop and recreate Songfull table

Revision ID: e72d9b80cd3e
Revises: 825d4dca7182
Create Date: 2023-10-21 18:58:56.535073

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e72d9b80cd3e'
down_revision = '825d4dca7182'
branch_labels = None
depends_on = None

import csv


def upgrade():
    # Delete all existing rows from the Songfull table

    # Import data from CSV into Songfull
    with open('/app/data/songfull.csv', 'r') as csv_file:
        rows_to_insert = []
        reader = csv.DictReader(csv_file)
        for row in reader:
            rows_to_insert.append({
                'name': row['Track Name'],
                'artist': row['Artist Name'],
                'id': row['Track ID'],
                'artist_id': row['Artist ID'],
                'image_url': row['Cover Art'],
                'external_url': row['External URL'],
                'spotify_preview_url': row['Preview Link'],
                'popularity': int(row['Popularity']),
                'genre': row['Genre'],
                'current': row['current'].lower() == 'false'
            })

        # Use op.bulk_insert() to insert data
