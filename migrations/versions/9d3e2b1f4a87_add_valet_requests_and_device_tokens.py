"""add valet_requests and device_tokens tables

Revision ID: 9d3e2b1f4a87
Revises: 8f8cb4d0da3c
Create Date: 2026-03-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '9d3e2b1f4a87'
down_revision = '8f8cb4d0da3c'
branch_labels = None
depends_on = None


def upgrade():
    # -------------------------------------------------------------------------
    # device_tokens — Expo push notification tokens per user
    # -------------------------------------------------------------------------
    op.create_table(
        'device_tokens',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token', sa.String, nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_device_tokens_user_id', 'device_tokens', ['user_id'])

    # -------------------------------------------------------------------------
    # valet_requests — lifecycle of a client's valet service request
    # -------------------------------------------------------------------------
    op.create_table(
        'valet_requests',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('client_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('latitude', sa.Float, nullable=False),
        sa.Column('longitude', sa.Float, nullable=False),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('accepted_by', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('service_id', sa.Integer, sa.ForeignKey('services.id'), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_valet_requests_client_id', 'valet_requests', ['client_id'])
    op.create_index('ix_valet_requests_status', 'valet_requests', ['status'])

    # -------------------------------------------------------------------------
    # services — relax location columns (filled progressively during service)
    # -------------------------------------------------------------------------
    op.alter_column('services', 'parking_location', nullable=True)
    op.alter_column('services', 'pickup_location', nullable=True)
    op.alter_column('services', 'keys_location', nullable=True)
    op.alter_column('services', 'is_finished', nullable=True)
    op.alter_column('services', 'is_deleted', nullable=True)


def downgrade():
    op.alter_column('services', 'is_deleted', nullable=False)
    op.alter_column('services', 'is_finished', nullable=False)
    op.alter_column('services', 'keys_location', nullable=False)
    op.alter_column('services', 'pickup_location', nullable=False)
    op.alter_column('services', 'parking_location', nullable=False)

    op.drop_index('ix_valet_requests_status', table_name='valet_requests')
    op.drop_index('ix_valet_requests_client_id', table_name='valet_requests')
    op.drop_table('valet_requests')

    op.drop_index('ix_device_tokens_user_id', table_name='device_tokens')
    op.drop_table('device_tokens')
