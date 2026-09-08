from fastapi import FastAPI, Depends, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from datetime import date
import os
from pathlib import Path

from app.config import get_settings
from app.models import Base, Product, Underlying, UnderlyingObservation, ObservationSchedule, Valuation, BarrierBreach
from app.domain import portfolio

# Settings
settings = get_settings()

# Database
engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Portfolio Dashboard")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== Routes ====================

@app.get("/api/dashboard")
def get_dashboard(as_of_date: date = Query(default=None), db: Session = Depends(get_db)):
    """
    Returns fully calculated dashboard: products with distances, status, aggregates.
    """
    if not as_of_date:
        as_of_date = date.today()
    
    # Fetch products
    products_orm = db.query(Product).filter(Product.lifecycle_status == "live").all()
    
    products_data = []
    
    for prod in products_orm:
        # Fetch underlyings and their latest spots as of as_of_date
        underlyings_orm = db.query(Underlying).filter(Underlying.product_id == prod.id).all()
        
        underlyings_data = []
        for u in underlyings_orm:
            latest_spot_orm = db.query(UnderlyingObservation).filter(
                UnderlyingObservation.underlying_id == u.id,
                UnderlyingObservation.observation_date <= as_of_date
            ).order_by(UnderlyingObservation.observation_date.desc()).first()
            
            spot = latest_spot_orm.spot if latest_spot_orm else None
            
            underlyings_data.append({
                "id": u.id,
                "name": u.name,
                "reference_level": u.reference_level,
                "yahoo_ticker": u.yahoo_ticker,
                "spot": spot,
                "spot_date": latest_spot_orm.observation_date if latest_spot_orm else None,
                "spot_source": latest_spot_orm.source if latest_spot_orm else None,
            })
        
        # Fetch latest valuation
        latest_val_orm = db.query(Valuation).filter(
            Valuation.product_id == prod.id,
            Valuation.as_of_date <= as_of_date,
            Valuation.is_primary == True
        ).order_by(Valuation.as_of_date.desc()).first()
        
        market_value = latest_val_orm.market_value if latest_val_orm else None
        val_date = latest_val_orm.as_of_date if latest_val_orm else None
        
        # Fetch observation schedule
        obs_schedule = db.query(ObservationSchedule).filter(
            ObservationSchedule.product_id == prod.id
        ).order_by(ObservationSchedule.observation_date).all()
        
        obs_data = [{
            "observation_date": o.observation_date,
            "payment_date": o.payment_date,
            "autocall_level": o.autocall_level,
            "coupon_level_low": o.coupon_level_low,
            "coupon_level_high": o.coupon_level_high,
            "coupon_rate_period": o.coupon_rate_period,
            "status": o.status,
        } for o in obs_schedule]
        
        # Calculate metrics
        worst_perf, worst_underlying = portfolio.calculate_worst_performance(underlyings_data)
        
        distance_to_strike = None
        if worst_perf is not None and prod.strike_level_pct is not None:
            distance_to_strike = portfolio.calculate_distance_to_strike(worst_perf, prod.strike_level_pct)
        
        # Next autocall level
        next_obs_idx = None
        for i, o in enumerate(obs_data):
            if o["observation_date"] > as_of_date:
                next_obs_idx = i
                break
        
        next_autocall_level = None
        distance_to_autocall = None
        next_observation_date = None
        if next_obs_idx is not None and next_obs_idx < len(obs_data):
            next_autocall_level = obs_data[next_obs_idx]["autocall_level"]
            next_observation_date = obs_data[next_obs_idx]["observation_date"]
            if worst_perf is not None:
                distance_to_autocall = portfolio.calculate_distance_to_autocall(worst_perf, next_autocall_level)
        
        # Autocall projection
        autocall_proj = portfolio.project_autocall_date(worst_perf, obs_data, prod.trigger_direction)
        
        # Status
        status = portfolio.determine_status(
            worst_perf,
            prod.strike_level_pct,
            distance_to_strike,
            prod.capital_protection_pct
        )
        
        # Missing fields
        missing = portfolio.calculate_missing_fields(
            {
                "asset_class": prod.asset_class,
                "issuer": prod.issuer,
                "currency": prod.currency,
                "notional": prod.notional,
                "lending_value_pct": prod.lending_value_pct,
                "maturity_date": prod.maturity_date,
                "strike_level_pct": prod.strike_level_pct,
                "barrier_observation": prod.barrier_observation,
                "coupon_condition": prod.coupon_condition,
                "coupon_payment_mode": prod.coupon_payment_mode,
                "underlyings": underlyings_data,
            },
            obs_data
        )
        
        products_data.append({
            "id": prod.id,
            "name": prod.name,
            "isin": prod.isin,
            "issuer": prod.issuer,
            "currency": prod.currency,
            "asset_class": prod.asset_class,
            "market_value": market_value,
            "valuation_date": val_date,
            "notional": prod.notional,
            "strike_level_pct": prod.strike_level_pct,
            "barrier_observation": prod.barrier_observation,
            "worst_performance_pct": worst_perf,
            "worst_underlying": worst_underlying,
            "distance_to_strike_pts": distance_to_strike,
            "distance_to_autocall_pts": distance_to_autocall,
            "next_autocall_level": next_autocall_level,
            "next_observation_date": next_observation_date,
            "autocall_projected_date": autocall_proj["observation_date"] if autocall_proj else None,
            "autocall_projected_payment_date": autocall_proj["payment_date"] if autocall_proj else None,
            "status": status,
            "missing_fields": missing,
            "awaiting_termsheet": prod.awaiting_termsheet,
            "underlyings": underlyings_data,
            "observation_schedule": obs_data,
        })
    
    # Aggregates (simplified for V1)
    total_mv = sum(p.get("market_value") or 0 for p in products_data)
    
    return {
        "as_of_date": as_of_date,
        "products": products_data,
        "aggregates": {
            "total_market_value": total_mv,
            "product_count": len(products_data),
        }
    }


# Serve React frontend
@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    """Catch-all to serve React app."""
    if full_path.startswith("api/"):
        raise Exception("Not found")
    
    # Try to serve static file
    static_path = Path(__file__).parent.parent.parent / "frontend" / "dist" / full_path
    if static_path.is_file():
        return FileResponse(static_path)
    
    # Fallback to index.html
    index = Path(__file__).parent.parent.parent / "frontend" / "dist" / "index.html"
    if index.is_file():
        return FileResponse(index)
    
    return {"error": "Not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
