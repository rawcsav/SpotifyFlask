"""artgen_style updated for dalle

Revision ID: 2ea82ee9ac53
Revises: 83f946d8f775
Create Date: 2023-11-07 16:31:29.388013

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2ea82ee9ac53'
down_revision = '83f946d8f775'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artgenstyle_sql', schema=None) as batch_op:
        batch_op.add_column(sa.Column('gen_style', sa.String(length=255), nullable=True))

    with op.batch_alter_table('playlist_sql', schema=None) as batch_op:
        batch_op.drop_column('weekly_graph')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('playlist_sql', schema=None) as batch_op:
        batch_op.add_column(sa.Column('weekly_graph', mysql.JSON(), nullable=True))

    with op.batch_alter_table('artgenstyle_sql', schema=None) as batch_op:
        batch_op.drop_column('gen_style')

    # ### end Alembic commands ###
