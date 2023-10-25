"""songfull currentgame archivde rel

Revision ID: 9544495cc85e
Revises: c37951747800
Create Date: 2023-10-24 13:32:11.546445

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9544495cc85e'
down_revision = 'c37951747800'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    # Drop tables
    op.drop_table('current_game')
    op.drop_table('past_game')
    op.drop_table('archive')

    # Recreate tables

    op.create_table(
        'past_game',
        sa.Column('user_id_or_session', sa.String(100), primary_key=True, nullable=False),
        sa.Column('date', sa.Date, nullable=False, index=True),
        sa.Column('attempts_made_general', sa.Integer, default=0),
        sa.Column('attempts_made_rock', sa.Integer, default=0),
        sa.Column('attempts_made_hiphop', sa.Integer, default=0),
        sa.Column('correct_guess_general', sa.Boolean, default=False),
        sa.Column('correct_guess_rock', sa.Boolean, default=False),
        sa.Column('correct_guess_hiphop', sa.Boolean, default=False)
    )

    op.create_table(
        'archive',
        sa.Column('date_played', sa.Date, primary_key=True, nullable=False, index=True),
        sa.Column('general_track', sa.String(150), sa.ForeignKey('songfull.id')),
        sa.Column('rock_track', sa.String(150), sa.ForeignKey('songfull.id')),
        sa.Column('hiphop_track', sa.String(150), sa.ForeignKey('songfull.id')),
        sa.Column('past_game_date', sa.Date, sa.ForeignKey('past_game.date'))
    )

    op.create_table(
        'current_game',
        sa.Column('user_id_or_session', sa.String(100), primary_key=True, nullable=False),
        sa.Column('current_genre', sa.String(50), default='General'),
        sa.Column('guesses_left', sa.Integer, default=6),
        sa.Column('date', sa.Date, nullable=False, default=sa.func.current_date()),
        sa.Column('archive_date', sa.Date, sa.ForeignKey('archive.date_played'), nullable=False)
    )


def downgrade():
    op.drop_table('current_game')
    op.drop_table('past_game')
    op.drop_table('archive')
