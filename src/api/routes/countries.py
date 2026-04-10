from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from src.database.connection import get_engine

router = APIRouter()

@router.get("")
def get_countries():
    """Returns list of all 25 countries."""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT country_code, country_name
            FROM dim_indicator_data
            ORDER BY country_name
        """))
        rows = result.fetchall()

    return {
        "total": len(rows),
        "countries": [{"code": r[0], "name": r[1]} for r in rows]
    }


@router.get("/{country_code}/profile")
def get_country_profile(country_code: str):
    """
    Returns full profile for one country.
    Includes latest values for all 8 indicators + top exports/imports.
    """
    engine = get_engine()
    code = country_code.upper()

    with engine.connect() as conn:

        # Get latest value for each indicator
        indicators = conn.execute(text("""
            SELECT indicator_code, indicator_name, year, value
            FROM dim_indicator_data
            WHERE country_code = :code
            AND year = (
                SELECT MAX(year) FROM dim_indicator_data
                WHERE country_code = :code
                AND indicator_code = dim_indicator_data.indicator_code
            )
            ORDER BY indicator_code
        """), {"code": code}).fetchall()

        if not indicators:
            raise HTTPException(status_code=404, detail=f"Country {code} not found")

        # Get GDP trend (all years)
        gdp_trend = conn.execute(text("""
            SELECT year, value
            FROM dim_indicator_data
            WHERE country_code = :code
            AND indicator_code = 'NY.GDP.MKTP.CD'
            ORDER BY year
        """), {"code": code}).fetchall()

        # Get exports trend
        exports_trend = conn.execute(text("""
            SELECT year, value
            FROM dim_indicator_data
            WHERE country_code = :code
            AND indicator_code = 'NE.EXP.GNFS.CD'
            ORDER BY year
        """), {"code": code}).fetchall()

        # Get imports trend
        imports_trend = conn.execute(text("""
            SELECT year, value
            FROM dim_indicator_data
            WHERE country_code = :code
            AND indicator_code = 'NE.IMP.GNFS.CD'
            ORDER BY year
        """), {"code": code}).fetchall()

        # Get top exports
        top_exports = conn.execute(text("""
            SELECT product_name, rank
            FROM dim_top_products
            WHERE country_code = :code
            AND trade_type = 'export'
            ORDER BY rank
        """), {"code": code}).fetchall()

        # Get top imports
        top_imports = conn.execute(text("""
            SELECT product_name, rank
            FROM dim_top_products
            WHERE country_code = :code
            AND trade_type = 'import'
            ORDER BY rank
        """), {"code": code}).fetchall()

    # Build indicator summary dict
    indicator_summary = {}
    for row in indicators:
        indicator_summary[row[1]] = {
            "value": float(row[3]) if row[3] else None,
            "year":  row[2]
        }

    return {
        "country_code": code,
        "indicators":   indicator_summary,
        "gdp_trend":    [{"year": r[0], "value": float(r[1])} for r in gdp_trend],
        "exports_trend":[{"year": r[0], "value": float(r[1])} for r in exports_trend],
        "imports_trend":[{"year": r[0], "value": float(r[1])} for r in imports_trend],
        "top_exports":  [r[0] for r in top_exports],
        "top_imports":  [r[0] for r in top_imports],
    }
