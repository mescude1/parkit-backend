"""add student_card_img and is_verified to users

Revision ID: a3f8c2d1e9b7
Revises: 0001_initial
Create Date: 2026-03-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a3f8c2d1e9b7'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        # Carnet de estudiante o empleado (requerido para valets)
        batch_op.add_column(sa.Column('student_card_img', sa.String(), nullable=True))

        # Indica si el valet ha sido verificado por el sistema antes de operar
        batch_op.add_column(sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_verified')
        batch_op.drop_column('student_card_img')