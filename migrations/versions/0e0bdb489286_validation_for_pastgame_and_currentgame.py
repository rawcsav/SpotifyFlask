"""validation for PastGame and CurrentGame

Revision ID: 0e0bdb489286
Revises: f68687f31f74
Create Date: 2023-10-30 19:34:21.313848

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0e0bdb489286'
down_revision = 'f68687f31f74'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('past_game', schema=None) as batch_op:
        # Drop the current primary key constraint
        batch_op.drop_constraint('PRIMARY', type_='primary')

        # Create the new composite primary key
        batch_op.create_primary_key('PRIMARY', ['user_id_or_session', 'date'])

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('past_game', schema=None) as batch_op:
        batch_op.drop_constraint('PRIMARY', type_='primary')

        batch_op.create_primary_key('PRIMARY', ['user_id_or_session'])

    # ### end Alembic commands ###
