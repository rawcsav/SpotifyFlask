"""Got rid of archive table, moved to Songfull

Revision ID: 6ac20db6fea2
Revises: d98f3d17cee4
Create Date: 2023-10-22 23:57:36.256745

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6ac20db6fea2'
down_revision = 'd98f3d17cee4'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('past_game_ibfk_1', 'past_game', type_='foreignkey')
    op.drop_table('archive')
    with op.batch_alter_table('songfull', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_played', sa.Date(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    op.create_table('archive')
    with op.batch_alter_table('songfull', schema=None) as batch_op:
        batch_op.drop_column('date_played')

    op.create_foreign_key('past_game_ibfk_1', 'past_game', 'archive', ['song_id'], ['song_id'])
