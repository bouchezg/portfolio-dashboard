"""
Pure business logic for portfolio metrics.
No database calls; input is ORM objects or dicts, output is dicts.
"""
from datetime import date
from typing import Optional, List, Dict, Any


def calculate_performance(spot: float, reference_level: float) -> float:
    """Performance = spot / reference_level, as a percentage."""
    if not reference_level or reference_level == 0:
        return None
    return (spot / reference_level) * 100


def calculate_worst_performance(
    underlyings: List[Dict],
    observation_date: date = None
) -> tuple[Optional[float], Optional[str]]:
    """
    Returns (worst_perf_pct, worst_underlying_name).
    Requires each underlying to have: reference_level, spot (at observation_date).
    """
    perfs = []
    for u in underlyings:
        ref = u.get("reference_level")
        spot = u.get("spot")
        if ref and spot:
            perf = calculate_performance(spot, ref)
            perfs.append((perf, u.get("name")))
    
    if not perfs:
        return None, None
    
    worst_perf, worst_name = min(perfs, key=lambda x: x[0])
    return worst_perf, worst_name


def calculate_distance_to_strike(worst_perf_pct: float, strike_level_pct: float) -> Optional[float]:
    """Distance in percentage points. Negative = below strike (at risk)."""
    if worst_perf_pct is None or strike_level_pct is None:
        return None
    return worst_perf_pct - (strike_level_pct * 100)


def calculate_distance_to_autocall(worst_perf_pct: float, autocall_level_pct: float) -> Optional[float]:
    """Distance in percentage points to the next autocall level."""
    if worst_perf_pct is None or autocall_level_pct is None:
        return None
    return worst_perf_pct - (autocall_level_pct * 100)


def determine_status(
    worst_perf_pct: Optional[float],
    strike_level_pct: Optional[float],
    distance_to_strike: Optional[float],
    capital_protection_pct: Optional[float],
    orange_threshold_pts: float = 10.0
) -> str:
    """
    Returns: 'red', 'orange', 'green', 'gray', or 'neutral' (for capital protected).
    """
    # Capital protected products have no capital risk
    if capital_protection_pct and capital_protection_pct >= 1.0:
        return "neutral"
    
    # Missing data
    if worst_perf_pct is None or strike_level_pct is None or distance_to_strike is None:
        return "gray"
    
    # Check if below strike (capital at risk)
    strike_perf = strike_level_pct * 100
    if worst_perf_pct <= strike_perf:
        return "red"
    
    # Check if close to strike
    if distance_to_strike <= orange_threshold_pts:
        return "orange"
    
    return "green"


def project_autocall_date(
    worst_perf_pct: Optional[float],
    observation_schedule: List[Dict],
    trigger_direction: str = "above"
) -> Optional[Dict]:
    """
    Returns {observation_date, payment_date, autocall_level} or None if no autocall.
    Assumes observation_schedule is sorted by observation_date.
    Uses worst_perf_pct as frozen (spot today), iterates through schedule to find first match.
    """
    if worst_perf_pct is None or not observation_schedule:
        return None
    
    for obs in observation_schedule:
        autocall_level_pct = obs.get("autocall_level")
        if autocall_level_pct is None:
            continue
        
        autocall_perf = autocall_level_pct * 100
        
        # Standard: autocall if worst_perf >= autocall_level
        if trigger_direction == "above":
            if worst_perf_pct >= autocall_perf:
                return {
                    "observation_date": obs.get("observation_date"),
                    "payment_date": obs.get("payment_date"),
                    "autocall_level": autocall_level_pct,
                }
        else:  # trigger_direction == "below"
            if worst_perf_pct <= autocall_perf:
                return {
                    "observation_date": obs.get("observation_date"),
                    "payment_date": obs.get("payment_date"),
                    "autocall_level": autocall_level_pct,
                }
    
    return None


def aggregate_by_currency(valuations: List[Dict]) -> Dict[str, float]:
    """Sum market_value_usd by currency."""
    by_currency = {}
    for v in valuations:
        ccy = v.get("currency")
        mv_usd = v.get("market_value_usd", 0)
        if ccy:
            by_currency[ccy] = by_currency.get(ccy, 0) + mv_usd
    return by_currency


def calculate_missing_fields(product: Dict, observation_schedule: List[Dict]) -> List[str]:
    """List of required fields that are missing."""
    missing = []
    
    asset_class = product.get("asset_class")
    
    # All structured products need these
    if asset_class == "structured_product":
        if not product.get("issuer"):
            missing.append("issuer")
        if not product.get("currency"):
            missing.append("currency")
        if not product.get("notional"):
            missing.append("notional")
        if product.get("lending_value_pct") is None:
            missing.append("lending_value_pct")
        if not product.get("maturity_date"):
            missing.append("maturity_date")
        if product.get("strike_level_pct") is None:
            missing.append("strike_level_pct")
        if not product.get("barrier_observation"):
            missing.append("barrier_observation")
        if not product.get("coupon_condition"):
            missing.append("coupon_condition")
        if not product.get("coupon_payment_mode"):
            missing.append("coupon_payment_mode")
        if not product.get("underlyings") or len(product.get("underlyings", [])) == 0:
            missing.append("underlyings")
        else:
            for u in product.get("underlyings", []):
                if u.get("reference_level") is None:
                    missing.append(f"underlying {u.get('name')} reference_level")
        if not observation_schedule or len(observation_schedule) == 0:
            missing.append("observation_schedule")
    
    return missing
