"""add valet_code to users

Revision ID: b5e1d3f2a8c4
Revises: a3f8c2d1e9b7
Create Date: 2026-03-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'b5e1d3f2a8c4'
down_revision = 'a3f8c2d1e9b7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        # Codigo unico del valet, generado automaticamente al registrarse (ej: VAL-00123)
        batch_op.add_column(sa.Column('valet_code', sa.String(), nullable=True))
        batch_op.create_unique_constraint('uq_users_valet_code', ['valet_code'])


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_valet_code', type_='unique')
        batch_op.drop_column('valet_code')
