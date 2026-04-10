from fastapi import APIRouter
from sqlalchemy import text
from src.database.connection import get_engine

router = APIRouter()

@router.get("")
def get_forex():
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT currency_code, currency_name, rate_vs_usd, rate_date
            FROM dim_exchange_rate
            ORDER BY currency_code
        """))
        rows = result.fetchall()

    rates = [
        {
            "currency_code": row[0],
            "currency_name": row[1],
            "rate_vs_usd":   float(row[2]),
            "rate_date":     str(row[3])
        }
        for row in rows
    ]
    return {"total": len(rates), "rates": rates}
