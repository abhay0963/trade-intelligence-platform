import pandas as pd
from sqlalchemy import text
from src.database.connection import get_engine

def load_countries(df):
    """
    Saves unique countries from the DataFrame into dim_country table.
    
    We use INSERT ... ON CONFLICT DO NOTHING
    This means: if the country already exists, skip it — don't crash.
    """

    engine = get_engine()

    # Get unique country names from the data
    countries = df["country_name"].unique()

    with engine.connect() as conn:
        for country_name in countries:

            # We don't have full country details yet (region, income group)
            # We'll enrich this data later — for now just save the name
            conn.execute(text("""
                INSERT INTO dim_country (country_name, country_code)
                VALUES (:name, :code)
                ON CONFLICT (country_code) DO NOTHING
            """), {
                "name": country_name,
                "code": country_name[:3].upper()  # temporary code e.g. 'IND'
            })

        conn.commit()
        print(f"✅ Saved {len(countries)} countries to dim_country")


def load_indicators(engine=None):
    """
    Saves the GDP indicator definition into dim_indicator table.
    This is metadata — what the indicator means, where it comes from.
    """

    if engine is None:
        engine = get_engine()

    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO dim_indicator (indicator_code, indicator_name, source, unit)
            VALUES (:code, :name, :source, :unit)
            ON CONFLICT (indicator_code) DO NOTHING
        """), {
            "code":   "NY.GDP.MKTP.CD",
            "name":   "GDP (current US$)",
            "source": "World Bank",
            "unit":   "USD"
        })

        conn.commit()
        print("✅ Saved GDP indicator to dim_indicator")


def load_gdp_facts(df):
    """
    Saves the actual GDP numbers into fact_economic_indicators table.
    
    For each row in our clean DataFrame:
    - Look up the country_id from dim_country
    - Look up the indicator_id from dim_indicator  
    - Look up or create the time_id from dim_time
    - Insert the actual GDP value
    """

    engine = get_engine()

    with engine.connect() as conn:
        rows_saved = 0

        for _, row in df.iterrows():
            # iterrows() goes through the DataFrame one row at a time
            # _ = row number (we don't need it)
            # row = the actual data for that row

            # Step 1: Find the country_id for this country name
            country = conn.execute(text("""
                SELECT country_id FROM dim_country
                WHERE country_name = :name
            """), {"name": row["country_name"]}).fetchone()

            if not country:
                print(f"Country not found: {row['country_name']}, skipping")
                continue

            # Step 2: Find the indicator_id for GDP
            indicator = conn.execute(text("""
                SELECT indicator_id FROM dim_indicator
                WHERE indicator_code = 'NY.GDP.MKTP.CD'
            """)).fetchone()

            if not indicator:
                print("GDP indicator not found, skipping")
                continue

            # Step 3: Make sure this year exists in dim_time, create if not
            conn.execute(text("""
                INSERT INTO dim_time (full_date, year, quarter, month, month_name)
                VALUES (
                    MAKE_DATE(:year, 1, 1),
                    :year, 1, 1, 'January'
                )
                ON CONFLICT (full_date) DO NOTHING
            """), {"year": int(row["year"])})

            # Get the time_id we just created or that already existed
            time_row = conn.execute(text("""
                SELECT time_id FROM dim_time WHERE year = :year AND month = 1
            """), {"year": int(row["year"])}).fetchone()

            # Step 4: Save the actual GDP value into the fact table
            conn.execute(text("""
                INSERT INTO fact_economic_indicators
                    (country_id, indicator_id, time_id, value)
                VALUES
                    (:country_id, :indicator_id, :time_id, :value)
            """), {
                "country_id":   country[0],
                "indicator_id": indicator[0],
                "time_id":      time_row[0],
                "value":        row["gdp_usd"]
            })

            rows_saved += 1

        conn.commit()
        print(f"✅ Saved {rows_saved} GDP records to fact_economic_indicators")


def test_loader():
    """
    Runs the full load: countries → indicator → facts
    Then reads back from DB to confirm data was saved.
    """
    from src.utils.api_clients import get_world_bank_data
    from src.etl.transform.cleaner import clean_gdp_data

    print("Step 1: Fetch and clean data...")
    raw  = get_world_bank_data("NY.GDP.MKTP.CD", country="IND")
    clean = clean_gdp_data(raw)

    print("\nStep 2: Load into database...")
    load_countries(clean)
    load_indicators()
    load_gdp_facts(clean)

    print("\nStep 3: Read back from database to confirm...")
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT c.country_name, t.year, f.value
            FROM fact_economic_indicators f
            JOIN dim_country   c ON f.country_id   = c.country_id
            JOIN dim_indicator i ON f.indicator_id = i.indicator_id
            JOIN dim_time      t ON f.time_id      = t.time_id
            ORDER BY t.year DESC
        """))

        rows = result.fetchall()
        print(f"\nFound {len(rows)} records in database:\n")
        for row in rows:
            print(f"{row[0]} | {row[1]} | GDP: ${row[2]:,.0f}")


if __name__ == "__main__":
    test_loader()