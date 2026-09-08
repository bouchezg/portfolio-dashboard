"""Initial schema creation.

Revision ID: 001
Revises:
Create Date: 2025-09-08

"""
from alembic import op
import sqlalchemy as sa


revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset_class', sa.String(), nullable=False),
        sa.Column('product_subtype', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('isin', sa.String(), nullable=True, unique=True),
        sa.Column('issuer', sa.String(), nullable=True),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('notional', sa.Float(), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('lending_value_pct', sa.Float(), nullable=True),
        sa.Column('lending_value_is_override', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('trade_date', sa.Date(), nullable=True),
        sa.Column('maturity_date', sa.Date(), nullable=True),
        sa.Column('strike_level_pct', sa.Float(), nullable=True),
        sa.Column('barrier_observation', sa.String(), nullable=True),
        sa.Column('observation_basis', sa.String(), nullable=False, server_default='ratio_to_initial_fixing'),
        sa.Column('trigger_direction', sa.String(), nullable=False, server_default='above'),
        sa.Column('coupon_condition', sa.String(), nullable=True),
        sa.Column('coupon_payment_mode', sa.String(), nullable=True),
        sa.Column('has_memory', sa.Boolean(), nullable=True),
        sa.Column('capital_protection_pct', sa.Float(), nullable=True),
        sa.Column('option_strike', sa.Float(), nullable=True),
        sa.Column('option_expiry', sa.Date(), nullable=True),
        sa.Column('lifecycle_status', sa.String(), nullable=False, server_default='live'),
        sa.Column('awaiting_termsheet', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create underlyings table
    op.create_table(
        'underlyings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('bloomberg_ticker', sa.String(), nullable=True),
        sa.Column('yahoo_ticker', sa.String(), nullable=True),
        sa.Column('reference_level', sa.Float(), nullable=True),
        sa.Column('strike_level_abs', sa.Float(), nullable=True),
        sa.Column('reference_units_per_denomination', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create observation_schedule table
    op.create_table(
        'observation_schedule',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('observation_date', sa.Date(), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('autocall_level', sa.Float(), nullable=True),
        sa.Column('coupon_level_low', sa.Float(), nullable=True),
        sa.Column('coupon_level_high', sa.Float(), nullable=True),
        sa.Column('coupon_rate_period', sa.Float(), nullable=True),
        sa.Column('coupon_amount_period', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('coupon_amount_paid', sa.Float(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create valuations table
    op.create_table(
        'valuations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('as_of_date', sa.Date(), nullable=False),
        sa.Column('market_value', sa.Float(), nullable=False),
        sa.Column('method', sa.String(), nullable=False, server_default='manual'),
        sa.Column('source', sa.String(), nullable=False, server_default='manual'),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('delta', sa.Float(), nullable=True),
        sa.Column('vega', sa.Float(), nullable=True),
        sa.Column('gamma', sa.Float(), nullable=True),
        sa.Column('theta', sa.Float(), nullable=True),
        sa.Column('inputs_json', sa.JSON(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create underlying_observations table
    op.create_table(
        'underlying_observations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('underlying_id', sa.Integer(), nullable=False),
        sa.Column('observation_date', sa.Date(), nullable=False),
        sa.Column('spot', sa.Float(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['underlying_id'], ['underlyings.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create barrier_breaches table
    op.create_table(
        'barrier_breaches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('underlying_id', sa.Integer(), nullable=False),
        sa.Column('breach_date', sa.Date(), nullable=False),
        sa.Column('observed_level', sa.Float(), nullable=False),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('acknowledged_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['underlying_id'], ['underlyings.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('barrier_breaches')
    op.drop_table('underlying_observations')
    op.drop_table('valuations')
    op.drop_table('observation_schedule')
    op.drop_table('underlyings')
    op.drop_table('products')
