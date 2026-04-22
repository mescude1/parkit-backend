"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-03-04 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('cellphone', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('profile_img', sa.String(), nullable=False),
        sa.Column('id_img', sa.String(), nullable=False),
        sa.Column('driver_license_img', sa.String(), nullable=False),
        sa.Column('contract', sa.String(), nullable=False),
        sa.Column('vehicle_type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('_password_hash', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
    )

    op.create_table(
        'user_locations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'vehicles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model', sa.String(), nullable=False),
        sa.Column('brand', sa.String(), nullable=False),
        sa.Column('license_plate', sa.String(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('vehicle_img', sa.String(), nullable=False),
        sa.Column('proof_insurance_img', sa.String(), nullable=False),
        sa.Column('property_card', sa.String(), nullable=False),
        sa.Column('owner', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['owner'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'media_metadata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('image_name', sa.String(), nullable=False),
        sa.Column('owner', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['owner'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # services and contract_metadata have a circular nullable FK between them.
    # Create services first without the contract FK, then add it after contract_metadata exists.
    op.create_table(
        'services',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('driver_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('vehicle_id', sa.Integer(), nullable=True),
        sa.Column('contract_id', sa.Integer(), nullable=True),
        sa.Column('parking_location', sa.Integer(), nullable=False),
        sa.Column('pickup_location', sa.Integer(), nullable=False),
        sa.Column('keys_location', sa.Integer(), nullable=False),
        sa.Column('is_finished', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['driver_id'], ['users.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id']),
        sa.ForeignKeyConstraint(['parking_location'], ['user_locations.id']),
        sa.ForeignKeyConstraint(['pickup_location'], ['user_locations.id']),
        sa.ForeignKeyConstraint(['keys_location'], ['user_locations.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'contract_metadata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_url', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('signed_at', sa.DateTime(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['service_id'], ['services.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # Now add the FK from services.contract_id → contract_metadata.id
    op.create_foreign_key(
        'fk_services_contract_id',
        'services', 'contract_metadata',
        ['contract_id'], ['id'],
    )


def downgrade():
    op.drop_constraint('fk_services_contract_id', 'services', type_='foreignkey')
    op.drop_table('contract_metadata')
    op.drop_table('services')
    op.drop_table('media_metadata')
    op.drop_table('vehicles')
    op.drop_table('user_locations')
    op.drop_table('users')