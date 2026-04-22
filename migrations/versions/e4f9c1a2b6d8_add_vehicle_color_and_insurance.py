"""add vehicle color and insurance fields

Revision ID: e4f9c1a2b6d8
Revises: d1a2b3c4d5e6
Create Date: 2026-04-17 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e4f9c1a2b6d8'
down_revision = 'd1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('vehicles', sa.Column('color', sa.String(), nullable=True))
    op.add_column('vehicles', sa.Column('policy_number', sa.String(), nullable=True))
    op.add_column('vehicles', sa.Column('insurance_expiration', sa.Date(), nullable=True))

    with op.batch_alter_table('vehicles') as batch_op:
        batch_op.alter_column('vehicle_img', existing_type=sa.String(), nullable=True)
        batch_op.alter_column('proof_insurance_img', existing_type=sa.String(), nullable=True)
        batch_op.alter_column('property_card', existing_type=sa.String(), nullable=True)


def downgrade():
    with op.batch_alter_table('vehicles') as batch_op:
        batch_op.alter_column('property_card', existing_type=sa.String(), nullable=False)
        batch_op.alter_column('proof_insurance_img', existing_type=sa.String(), nullable=False)
        batch_op.alter_column('vehicle_img', existing_type=sa.String(), nullable=False)

    op.drop_column('vehicles', 'insurance_expiration')
    op.drop_column('vehicles', 'policy_number')
    op.drop_column('vehicles', 'color')
