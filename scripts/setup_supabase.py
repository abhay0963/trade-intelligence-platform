import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

def setup_supabase():
    url = os.getenv("SUPABASE_DB_URL")
    if not url:
        print("❌ SUPABASE_DB_URL not found in .env")
        return

    print("Connecting to Supabase...")
    engine = create_engine(url)

    tables_sql = """
    CREATE TABLE IF NOT EXISTS dim_country (
        country_id   SERIAL PRIMARY KEY,
        country_code VARCHAR(3) UNIQUE NOT NULL,
        country_name VARCHAR(100) NOT NULL,
        region       VARCHAR(100),
        income_group VARCHAR(50),
        created_at   TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS dim_indicator (
        indicator_id   SERIAL PRIMARY KEY,
        indicator_code VARCHAR(50) UNIQUE NOT NULL,
        indicator_name VARCHAR(200) NOT NULL,
        source         VARCHAR(100),
        unit           VARCHAR(50)
    );
    CREATE TABLE IF NOT EXISTS dim_time (
        time_id      SERIAL PRIMARY KEY,
        full_date    DATE UNIQUE NOT NULL,
        year         INTEGER NOT NULL,
        quarter      INTEGER NOT NULL,
        month        INTEGER NOT NULL,
        month_name   VARCHAR(20) NOT NULL,
        week_number  INTEGER,
        is_year_end  BOOLEAN DEFAULT FALSE
    );
    CREATE TABLE IF NOT EXISTS fact_trade_flows (
        trade_id        SERIAL PRIMARY KEY,
        time_id         INTEGER REFERENCES dim_time(time_id),
        exporter_id     INTEGER REFERENCES dim_country(country_id),
        importer_id     INTEGER REFERENCES dim_country(country_id),
        commodity_id    INTEGER,
        trade_value_usd NUMERIC(20,2),
        quantity        NUMERIC(20,4),
        unit_price_usd  NUMERIC(15,4),
        data_source     VARCHAR(50),
        created_at      TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS fact_economic_indicators (
        indicator_data_id SERIAL PRIMARY KEY,
        country_id        INTEGER REFERENCES dim_country(country_id),
        indicator_id      INTEGER REFERENCES dim_indicator(indicator_id),
        time_id           INTEGER REFERENCES dim_time(time_id),
        value             NUMERIC(20,4),
        created_at        TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS dim_indicator_data (
        id             SERIAL PRIMARY KEY,
        country_code   VARCHAR(3) NOT NULL,
        country_name   VARCHAR(100) NOT NULL,
        indicator_code VARCHAR(50) NOT NULL,
        indicator_name VARCHAR(200) NOT NULL,
        year           INTEGER NOT NULL,
        value          NUMERIC(25,4),
        created_at     TIMESTAMP DEFAULT NOW(),
        UNIQUE(country_code, indicator_code, year)
    );
    CREATE TABLE IF NOT EXISTS dim_commodity_price (
        price_id       SERIAL PRIMARY KEY,
        symbol         VARCHAR(20) UNIQUE NOT NULL,
        commodity_name VARCHAR(100) NOT NULL,
        price          NUMERIC(15,4),
        unit           VARCHAR(50),
        price_date     DATE,
        updated_at     TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS dim_exchange_rate (
        rate_id       SERIAL PRIMARY KEY,
        currency_code VARCHAR(10) UNIQUE NOT NULL,
        currency_name VARCHAR(100),
        rate_vs_usd   NUMERIC(15,6),
        rate_date     DATE,
        updated_at    TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS dim_precious_metals (
        id         SERIAL PRIMARY KEY,
        symbol     VARCHAR(10) UNIQUE NOT NULL,
        name       VARCHAR(50) NOT NULL,
        price_usd  NUMERIC(12,2),
        unit       VARCHAR(50),
        price_date DATE,
        updated_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS dim_top_products (
        id           SERIAL PRIMARY KEY,
        country_code VARCHAR(3) NOT NULL,
        country_name VARCHAR(100) NOT NULL,
        trade_type   VARCHAR(10) NOT NULL,
        product_name VARCHAR(200) NOT NULL,
        rank         INTEGER NOT NULL,
        created_at   TIMESTAMP DEFAULT NOW(),
        UNIQUE(country_code, trade_type, rank)
    );
    CREATE INDEX IF NOT EXISTS idx_ind_data_country ON dim_indicator_data(country_code);
    CREATE INDEX IF NOT EXISTS idx_ind_data_code    ON dim_indicator_data(indicator_code);
    CREATE INDEX IF NOT EXISTS idx_ind_data_year    ON dim_indicator_data(year);
    """

    with engine.connect() as conn:
        conn.execute(text(tables_sql))
        conn.commit()

    print("✅ All tables created on Supabase successfully!")
    print("\nTables created:")
    tables = [
        "dim_country", "dim_indicator", "dim_time",
        "fact_trade_flows", "fact_economic_indicators",
        "dim_indicator_data", "dim_commodity_price",
        "dim_exchange_rate", "dim_precious_metals", "dim_top_products"
    ]
    for t in tables:
        print(f"  ✅ {t}")

if __name__ == "__main__":
    setup_supabase()