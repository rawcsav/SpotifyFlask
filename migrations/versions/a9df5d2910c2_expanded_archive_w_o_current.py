"""Expanded Archive w/o current

Revision ID: a9df5d2910c2
Revises: d958e161a4d5
Create Date: 2023-10-21 20:14:47.647024

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a9df5d2910c2'
down_revision = 'd958e161a4d5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('archive', schema=None) as batch_op:
        batch_op.drop_column('current')


def downgrade():
    with op.batch_alter_table('archive', schema=None) as batch_op:
        batch_op.add_column(sa.Column('current', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
