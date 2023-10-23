"""Prepare to remove foreign key from artgen_sql

Revision ID: c557bac33c96
Revises: 
Create Date: 2023-10-20 21:18:59.532519

"""
from alembic import op

revision = 'c557bac33c96'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('artgen_sql_ibfk_1', 'artgen_sql', type_='foreignkey')
    op.drop_constraint('artgen_sql_ibfk_2', 'artgen_sql', type_='foreignkey')


def downgrade():
    op.create_foreign_key('artgen_sql_ibfk_1', 'artgen_sql', 'genre_sql', ['genre_name'], ['genre'])
    op.create_foreign_key('artgen_sql_ibfk_2', 'artgen_sql', 'genre_sql', ['genre_name'], ['genre'])
