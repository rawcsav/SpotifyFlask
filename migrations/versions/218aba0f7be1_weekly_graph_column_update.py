"""weekly graph column update

Revision ID: 218aba0f7be1
Revises: 83f946d8f775
Create Date: 2023-10-31 10:04:04.518555

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '218aba0f7be1'
down_revision = '83f946d8f775'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('current_game', schema=None) as batch_op:
        batch_op.drop_column('guess_1')
        batch_op.drop_column('guess_5')
        batch_op.drop_column('guess_6')
        batch_op.drop_column('guess_2')
        batch_op.drop_column('guess_3')
        batch_op.drop_column('guess_4')

    with op.batch_alter_table('playlist_sql', schema=None) as batch_op:
        batch_op.add_column(sa.Column('weekly_graph', sa.JSON(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('playlist_sql', schema=None) as batch_op:
        batch_op.drop_column('weekly_graph')

    with op.batch_alter_table('current_game', schema=None) as batch_op:
        batch_op.add_column(sa.Column('guess_4', mysql.VARCHAR(length=150), nullable=True))
        batch_op.add_column(sa.Column('guess_3', mysql.VARCHAR(length=150), nullable=True))
        batch_op.add_column(sa.Column('guess_2', mysql.VARCHAR(length=150), nullable=True))
        batch_op.add_column(sa.Column('guess_6', mysql.VARCHAR(length=150), nullable=True))
        batch_op.add_column(sa.Column('guess_5', mysql.VARCHAR(length=150), nullable=True))
        batch_op.add_column(sa.Column('guess_1', mysql.VARCHAR(length=150), nullable=True))

    # ### end Alembic commands ###
