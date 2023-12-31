"""songfull currentgame archivde rel

Revision ID: 2fb2a9f4c582
Revises: c37951747800
Create Date: 2023-10-24 13:35:30.230700

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2fb2a9f4c582'
down_revision = 'c37951747800'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('current_game', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'archive', ['archive_date'], ['date_played'])
        batch_op.drop_column('selected_songs')
        batch_op.drop_column('hiphop_track')
        batch_op.drop_column('general_track')
        batch_op.drop_column('rock_track')

    with op.batch_alter_table('songfull', schema=None) as batch_op:
        batch_op.add_column(sa.Column('played', sa.SmallInteger(), nullable=True))
        batch_op.drop_column('date_played')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('songfull', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_played', sa.DATE(), nullable=True))
        batch_op.create_foreign_key('songfull_ibfk_1', 'past_game', ['date_played'], ['date'])
        batch_op.drop_column('played')

    with op.batch_alter_table('current_game', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rock_track', mysql.VARCHAR(length=150), nullable=True))
        batch_op.add_column(sa.Column('general_track', mysql.VARCHAR(length=150), nullable=True))
        batch_op.add_column(sa.Column('hiphop_track', mysql.VARCHAR(length=150), nullable=True))
        batch_op.add_column(sa.Column('selected_songs', mysql.JSON(), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
