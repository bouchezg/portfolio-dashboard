"""
Seed script: populate 3 real structured products for testing.
Run: python seed.py (from backend/ dir)
"""
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Product, Underlying, ObservationSchedule, Valuation, UnderlyingObservation
from app.config import get_settings
 
settings = get_settings()
engine = create_engine(settings.database_url, echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
db = Session()
 
# Clear existing data
db.query(Product).delete()
db.query(Underlying).delete()
db.query(ObservationSchedule).delete()
db.query(Valuation).delete()
db.query(UnderlyingObservation).delete()
db.commit()
 
# ========== Product 1: UBS IREN/Nebius 10M ==========
prod1 = Product(
    asset_class="structured_product",
    product_subtype="autocall_worst_of",
    name="37% on IREN, Nebius",
    isin="CH1566087354",
    issuer="UBS AG",
    currency="USD",
    notional=1000000.0,
    quantity=1.0,
    lending_value_pct=0.75,
    trade_date=date(2025, 9, 8),
    maturity_date=date(2026, 7, 28),
    strike_level_pct=0.60,
    barrier_observation="at_expiry",
    observation_basis="ratio_to_initial_fixing",
    trigger_direction="above",
    coupon_condition="guaranteed",
    coupon_payment_mode="periodic",
    has_memory=False,
    capital_protection_pct=None,
    lifecycle_status="live",
    awaiting_termsheet=False,
)
db.add(prod1)
db.flush()
 
# Underlyings for product 1
iren1 = Underlying(
    product_id=prod1.id,
    name="IREN Ltd",
    bloomberg_ticker="IREN UW Equity",
    yahoo_ticker="IREN",
    reference_level=61.78,
    strike_level_abs=37.068,
    reference_units_per_denomination=134.8872,
)
nebius1 = Underlying(
    product_id=prod1.id,
    name="Nebius Group N.V.",
    bloomberg_ticker="NBIS SJ Equity",
    yahoo_ticker="NBIS",
    reference_level=207.82,
    strike_level_abs=124.692,
    reference_units_per_denomination=40.0988,
)
db.add_all([iren1, nebius1])
db.flush()
 
# Observation schedule for product 1 (10 observations, monthly)
obs_dates_1 = [
    (date(2025, 10, 29), date(2025, 11, 13)),
    (date(2025, 11, 28), date(2025, 12, 13)),
    (date(2025, 12, 29), date(2026, 1, 13)),
    (date(2026, 1, 29), date(2026, 2, 13)),
    (date(2026, 2, 27), date(2026, 3, 13)),
    (date(2026, 3, 27), date(2026, 4, 13)),
    (date(2026, 4, 29), date(2026, 5, 13)),
    (date(2026, 5, 29), date(2026, 6, 13)),
    (date(2026, 6, 29), date(2026, 7, 13)),
    (date(2026, 7, 28), date(2026, 7, 28)),
]
 
autocall_levels = [0.98, 0.96, 0.94, 0.92, 0.90, 0.88, 0.86, 0.84, 0.82, 0.80]
 
for i, (obs_date, pay_date) in enumerate(obs_dates_1):
    sched = ObservationSchedule(
        product_id=prod1.id,
        observation_date=obs_date,
        payment_date=pay_date,
        autocall_level=autocall_levels[i],
        coupon_rate_period=0.037 / 12,
        status="pending" if obs_date > date.today() else ("coupon_paid" if i < 2 else "pending"),
        resolved_at=datetime.utcnow() if i < 2 else None,
    )
    db.add(sched)
db.commit()
 
# Valuations for product 1
val1 = Valuation(
    product_id=prod1.id,
    as_of_date=date.today(),
    market_value=984300.0,
    method="manual",
    source="manual",
    is_primary=True,
    created_by="PM",
)
db.add(val1)
db.commit()
 
# Spots for product 1
spot_iren_1 = UnderlyingObservation(
    underlying_id=iren1.id,
    observation_date=date.today(),
    spot=44.00,
    source="manual",
)
spot_nebius_1 = UnderlyingObservation(
    underlying_id=nebius1.id,
    observation_date=date.today(),
    spot=165.00,
    source="manual",
)
db.add_all([spot_iren_1, spot_nebius_1])
db.commit()
 
# ========== Product 2: SocGen Capital Protected ZC ==========
prod2 = Product(
    asset_class="structured_product",
    product_subtype="capital_protected_note",
    name="100% Capital Protected ZC Phoenix on 10Y USD CMS",
    isin="XS3048529252",
    issuer="Société Générale",
    currency="USD",
    notional=1000000.0,
    quantity=1.0,
    lending_value_pct=0.80,
    trade_date=date(2024, 9, 8),
    maturity_date=date(2034, 9, 8),
    strike_level_pct=None,
    barrier_observation=None,
    observation_basis="absolute_level",
    trigger_direction="above",
    coupon_condition="conditional",
    coupon_payment_mode="at_redemption",
    has_memory=True,
    capital_protection_pct=1.0,
    lifecycle_status="live",
    awaiting_termsheet=False,
)
db.add(prod2)
db.flush()
 
# Underlyings for product 2 (10Y USD CMS)
cms_10y = Underlying(
    product_id=prod2.id,
    name="10Y USD CMS",
    bloomberg_ticker="CMSW10 Index",
    yahoo_ticker=None,
    reference_level=3.41,
    strike_level_abs=None,
    reference_units_per_denomination=None,
)
db.add(cms_10y)
db.flush()
 
# Observation schedule for product 2 (annual, 10 years)
for year in range(1, 11):
    obs_date = date(2024 + year, 9, 8)
    sched2 = ObservationSchedule(
        product_id=prod2.id,
        observation_date=obs_date,
        payment_date=obs_date,
        autocall_level=None,
        coupon_level_low=2.85,
        coupon_level_high=4.40,
        coupon_rate_period=None,
        status="pending",
    )
    db.add(sched2)
db.commit()
 
# Valuation for product 2
val2 = Valuation(
    product_id=prod2.id,
    as_of_date=date.today(),
    market_value=994600.0,
    method="manual",
    source="manual",
    is_primary=True,
    created_by="PM",
)
db.add(val2)
db.commit()
 
# Spot for product 2 (current 10Y CMS)
spot_cms = UnderlyingObservation(
    underlying_id=cms_10y.id,
    observation_date=date.today(),
    spot=3.41,
    source="manual",
)
db.add(spot_cms)
db.commit()
 
# ========== Product 3: Deutsche Bank SOFR Note ==========
prod3 = Product(
    asset_class="structured_product",
    product_subtype="capital_protected_note",
    name="9.20% Capital Protected on SOFR",
    isin="XS3402789765",
    issuer="Deutsche Bank",
    currency="USD",
    notional=1000000.0,
    quantity=1.0,
    lending_value_pct=0.75,
    trade_date=date(2025, 7, 13),
    maturity_date=date(2026, 7, 13),
    strike_level_pct=None,
    barrier_observation=None,
    observation_basis="absolute_level",
    trigger_direction="above",
    coupon_condition="conditional",
    coupon_payment_mode="periodic",
    has_memory=False,
    capital_protection_pct=1.0,
    lifecycle_status="live",
    awaiting_termsheet=False,
)
db.add(prod3)
db.flush()
 
# Underlyings for product 3 (SOFR)
sofr = Underlying(
    product_id=prod3.id,
    name="USD SOFR",
    bloomberg_ticker="SOFR Index",
    yahoo_ticker=None,
    reference_level=4.85,
    strike_level_abs=None,
    reference_units_per_denomination=None,
)
db.add(sofr)
db.flush()
 
# Observation schedule for product 3 (quarterly)
sched_dates = [
    (date(2025, 10, 13), date(2025, 10, 18)),
    (date(2026, 1, 13), date(2026, 1, 18)),
    (date(2026, 4, 13), date(2026, 4, 18)),
    (date(2026, 7, 13), date(2026, 7, 13)),
]
 
for obs_date, pay_date in sched_dates:
    sched3 = ObservationSchedule(
        product_id=prod3.id,
        observation_date=obs_date,
        payment_date=pay_date,
        autocall_level=None,
        coupon_level_low=2.85,
        coupon_level_high=4.40,
        coupon_rate_period=0.092 / 4,
        status="pending",
    )
    db.add(sched3)
db.commit()
 
# Valuation for product 3
val3 = Valuation(
    product_id=prod3.id,
    as_of_date=date.today(),
    market_value=1000000.0,
    method="manual",
    source="manual",
    is_primary=True,
    created_by="PM",
)
db.add(val3)
db.commit()
 
# Spot for product 3 (current SOFR rate)
spot_sofr = UnderlyingObservation(
    underlying_id=sofr.id,
    observation_date=date.today(),
    spot=4.85,
    source="manual",
)
db.add(spot_sofr)
db.commit()
 
print("✓ Seeded 3 products successfully")
db.close()
