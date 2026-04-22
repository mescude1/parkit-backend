"""add institutional_email fields and drop student_card_img

Revision ID: c7a2e4b9d1f6
Revises: b5e1d3f2a8c4
Create Date: 2026-03-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'c7a2e4b9d1f6'
down_revision = 'b5e1d3f2a8c4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('institutional_email', sa.String(), nullable=True))
        batch_op.add_column(sa.Column(
            'institutional_email_verified', sa.Boolean(), nullable=True, server_default='false'
        ))
        batch_op.create_unique_constraint('uq_users_institutional_email', ['institutional_email'])
        batch_op.drop_column('student_card_img')


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_institutional_email', type_='unique')
        batch_op.drop_column('institutional_email_verified')
        batch_op.drop_column('institutional_email')
        batch_op.add_column(sa.Column('student_card_img', sa.String(), nullable=True))