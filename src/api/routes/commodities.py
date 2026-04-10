from fastapi import APIRouter
from sqlalchemy import text
from src.database.connection import get_engine

router = APIRouter()

@router.get("")
def get_commodities():
    """Returns all commodity prices including precious metals."""
    engine = get_engine()

    with engine.connect() as conn:
        # Regular commodities
        commodities = conn.execute(text("""
            SELECT symbol, commodity_name, price, unit, price_date
            FROM dim_commodity_price
            ORDER BY commodity_name
        """)).fetchall()

        # Precious metals
        metals = conn.execute(text("""
            SELECT symbol, name, price_usd, unit, price_date
            FROM dim_precious_metals
            ORDER BY name
        """)).fetchall()

    return {
        "commodities": [
            {"symbol": r[0], "commodity_name": r[1], "price": float(r[2]),
             "unit": r[3], "price_date": str(r[4]), "type": "commodity"}
            for r in commodities
        ],
        "precious_metals": [
            {"symbol": r[0], "commodity_name": r[1], "price": float(r[2]),
             "unit": r[3], "price_date": str(r[4]), "type": "metal"}
            for r in metals
        ]
    }
