from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Enum, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    asset_class = Column(String, nullable=False)  # liquidity, structured_product, equity, fixed_income, commodity, option
    product_subtype = Column(String, nullable=True)  # autocall_worst_of, phoenix_autocall, capital_protected_note, rate_autocall, call, put
    name = Column(String, nullable=False)
    isin = Column(String, nullable=True, unique=True)
    issuer = Column(String, nullable=True)
    currency = Column(String, nullable=False)  # USD, CHF, AED, JPY, EUR
    notional = Column(Float, nullable=True)
    quantity = Column(Float, nullable=True)
    lending_value_pct = Column(Float, nullable=True)
    lending_value_is_override = Column(Boolean, default=False)
    trade_date = Column(Date, nullable=True)
    maturity_date = Column(Date, nullable=True)
    strike_level_pct = Column(Float, nullable=True)  # e.g., 0.60 for 60% of reference level
    barrier_observation = Column(String, nullable=True)  # at_expiry, daily_close, continuous
    observation_basis = Column(String, default="ratio_to_initial_fixing")  # ratio_to_initial_fixing, absolute_level
    trigger_direction = Column(String, default="above")  # above, below
    coupon_condition = Column(String, nullable=True)  # guaranteed, conditional
    coupon_payment_mode = Column(String, nullable=True)  # periodic, at_redemption
    has_memory = Column(Boolean, nullable=True)
    capital_protection_pct = Column(Float, nullable=True)
    option_strike = Column(Float, nullable=True)
    option_expiry = Column(Date, nullable=True)
    lifecycle_status = Column(String, default="live")  # live, autocalled, matured, closed
    awaiting_termsheet = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    underlyings = relationship("Underlying", back_populates="product")
    observations = relationship("ObservationSchedule", back_populates="product")
    valuations = relationship("Valuation", back_populates="product")


class Underlying(Base):
    __tablename__ = "underlyings"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String, nullable=False)
    bloomberg_ticker = Column(String, nullable=True)
    yahoo_ticker = Column(String, nullable=True)
    reference_level = Column(Float, nullable=True)  # Initial fixing level
    strike_level_abs = Column(Float, nullable=True)  # Absolute strike (for physical settlement)
    reference_units_per_denomination = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="underlyings")
    observations = relationship("UnderlyingObservation", back_populates="underlying")


class ObservationSchedule(Base):
    __tablename__ = "observation_schedule"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    observation_date = Column(Date, nullable=False)
    payment_date = Column(Date, nullable=False)
    autocall_level = Column(Float, nullable=True)  # % of reference level
    coupon_level_low = Column(Float, nullable=True)
    coupon_level_high = Column(Float, nullable=True)
    coupon_rate_period = Column(Float, nullable=True)  # e.g., 0.02917 for 2.917%
    coupon_amount_period = Column(Float, nullable=True)  # e.g., 157 USD per period
    status = Column(String, default="pending")  # pending, coupon_paid, coupon_missed, autocalled
    coupon_amount_paid = Column(Float, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    product = relationship("Product", back_populates="observations")


class Valuation(Base):
    __tablename__ = "valuations"
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    as_of_date = Column(Date, nullable=False)
    market_value = Column(Float, nullable=False)  # in product currency, dirty price
    method = Column(String, default="manual")  # manual, monte_carlo, black_scholes
    source = Column(String, default="manual")  # manual, ibkr, internal
    is_primary = Column(Boolean, default=True)
    delta = Column(Float, nullable=True)
    vega = Column(Float, nullable=True)
    gamma = Column(Float, nullable=True)
    theta = Column(Float, nullable=True)
    inputs_json = Column(JSON, nullable=True)  # {spots: {...}, vol: {...}, rates: {...}}
    comment = Column(Text, nullable=True)
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    product = relationship("Product", back_populates="valuations")
    
    __table_args__ = (
        # Unique constraint on (product_id, as_of_date, method) to allow multiple methods per day
        {"sqlite_autoincrement": True},
    )


class UnderlyingObservation(Base):
    __tablename__ = "underlying_observations"
    
    id = Column(Integer, primary_key=True)
    underlying_id = Column(Integer, ForeignKey("underlyings.id"), nullable=False)
    observation_date = Column(Date, nullable=False)
    spot = Column(Float, nullable=False)
    source = Column(String)  # yahoo, manual, ibkr
    created_at = Column(DateTime, default=datetime.utcnow)
    
    underlying = relationship("Underlying", back_populates="observations")


class BarrierBreach(Base):
    __tablename__ = "barrier_breaches"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    underlying_id = Column(Integer, ForeignKey("underlyings.id"), nullable=False)
    breach_date = Column(Date, nullable=False)
    observed_level = Column(Float, nullable=False)
    source = Column(String)  # auto, manual
    acknowledged_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
