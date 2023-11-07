"""minor tweaks

Revision ID: c3f0a594293f
Revises: 2fb2a9f4c582
Create Date: 2023-10-24 13:49:53.458303

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3f0a594293f'
down_revision = '2fb2a9f4c582'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('songfull', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_songfull_genre'), ['genre'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('songfull', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_songfull_genre'))

    # ### end Alembic commands ###