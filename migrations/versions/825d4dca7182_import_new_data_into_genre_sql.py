"""Import new data into genre_sql

Revision ID: 825d4dca7182
Revises: c557bac33c96
Create Date: 2023-10-20 21:33:45.979526

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '825d4dca7182'
down_revision = 'c557bac33c96'
branch_labels = None
depends_on = None

from app.database import genre_sql  # Adjust the import path to your actual app structure
import csv


def upgrade():
    # Import data from CSV into genre_sql
    with open('/Users/gavinmason/PycharmProjects/BotifyStats/app/data/updated_master_genres.csv', 'r') as csv_file:
        # Delete all existing rows from the genre_sql table
        op.execute(genre_sql.__table__.delete())

        rows_to_insert = []
        reader = csv.DictReader(csv_file)
        for row in reader:
            rows_to_insert.append({
                'genre': row['genre'],
                'sim_genres': row['sim_genres'],
                'sim_weights': row['sim_weights'],
                'opp_genres': row['opp_genres'],
                'opp_weights': row['opp_weights'],
                'spotify_url': row['spotify_url'],
                'color_hex': row['color_hex'],
                'color_rgb': row['color_rgb'],
                'x': float(row['x']),
                'y': float(row['y']),
                'closest_stat_genres': row['closest_stat_genres'],
            })

        # Use op.bulk_insert() to insert data
        op.bulk_insert(genre_sql.__table__, rows_to_insert)

        # Create foreign key constraint
        op.create_foreign_key('artgen_sql_ibfk_1', 'artgen_sql', 'genre_sql', ['genre_name'], ['genre'])


def downgrade():
    op.drop_constraint('artgen_sql_ibfk_1', 'artgen_sql', type_='foreignkey')
