"""songfull schema changes

Revision ID: c37951747800
Revises: 5dd588f6e102
Create Date: 2023-10-24 12:53:53.270508

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c37951747800'
down_revision = '5dd588f6e102'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('songfull_ibfk_1', 'songfull', type_='foreignkey')
    with op.batch_alter_table('current_game', schema=None) as batch_op:
        batch_op.add_column(sa.Column('general_track', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('rock_track', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('hiphop_track', sa.String(length=150), nullable=True))
        batch_op.create_foreign_key(None, 'songfull', ['general_track'], ['id'])
        batch_op.create_foreign_key(None, 'songfull', ['rock_track'], ['id'])
        batch_op.create_foreign_key(None, 'songfull', ['hiphop_track'], ['id'])
        batch_op.drop_column('selected_songs')

    with op.batch_alter_table('songfull', schema=None) as batch_op:
        batch_op.add_column(sa.Column('played', sa.SmallInteger(), nullable=True))
        batch_op.drop_column('date_played')

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('songfull', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_played', sa.DATE(), nullable=True))
        batch_op.create_foreign_key('songfull_ibfk_1', 'past_game', ['date_played'], ['date'])
        batch_op.drop_column('played')

    with op.batch_alter_table('current_game', schema=None) as batch_op:
        batch_op.add_column(sa.Column('selected_songs', mysql.JSON(), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('hiphop_track')
        batch_op.drop_column('rock_track')
        batch_op.drop_column('general_track')

    # ### end Alembic commands ###
