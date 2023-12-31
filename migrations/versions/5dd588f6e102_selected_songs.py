"""selected songs

Revision ID: 5dd588f6e102
Revises: 3ac41ce22b37
Create Date: 2023-10-24 01:19:31.247586

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5dd588f6e102'
down_revision = '3ac41ce22b37'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('current_game', schema=None) as batch_op:
        batch_op.add_column(sa.Column('selected_songs', sa.JSON(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('current_game', schema=None) as batch_op:
        batch_op.drop_column('selected_songs')

    # ### end Alembic commands ###
