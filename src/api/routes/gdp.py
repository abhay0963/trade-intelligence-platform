from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from src.database.connection import get_engine

router = APIRouter()

@router.get("/top10")
def get_top10_gdp():
    """Returns top 10 countries by latest GDP."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT country_name, country_code, value, year
            FROM dim_indicator_data
            WHERE indicator_code = 'NY.GDP.MKTP.CD'
            AND year = (SELECT MAX(year) FROM dim_indicator_data WHERE indicator_code = 'NY.GDP.MKTP.CD')
            ORDER BY value DESC
            LIMIT 10
        """))
        rows = result.fetchall()

    return {
        "year": rows[0][3] if rows else None,
        "rankings": [
            {"rank": i+1, "country": r[0], "code": r[1], "gdp_usd": float(r[2])}
            for i, r in enumerate(rows)
        ]
    }


@router.get("/{country_code}")
def get_gdp_by_country(country_code: str):
    """Returns GDP trend for a specific country by 3-letter code."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT year, value, country_name
            FROM dim_indicator_data
            WHERE country_code = :code
            AND indicator_code = 'NY.GDP.MKTP.CD'
            ORDER BY year
        """), {"code": country_code.upper()})
        rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No data for {country_code}")

    return {
        "country":  rows[0][2],
        "code":     country_code.upper(),
        "data":     [{"year": r[0], "gdp_usd": float(r[1])} for r in rows]
    }
