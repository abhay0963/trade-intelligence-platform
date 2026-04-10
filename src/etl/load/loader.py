from sqlalchemy import text
from src.database.connection import get_engine
from src.utils.api_clients import WB_INDICATORS, TOP_25_COUNTRIES


def load_all_world_bank_indicators(all_data):
    """
    Saves all World Bank indicators into dim_indicator_data.
    
    all_data is a dict: { indicator_code: [records] }
    Each record has: date, value, country: {value: name}
    
    Uses UPSERT — if same country+indicator+year exists, updates it.
    This means running the pipeline twice never creates duplicates.
    """
    engine = get_engine()
    total_saved = 0

    # Build a reverse lookup: country name → country code
    # e.g. "India" → "IND"
    name_to_code = {v: k for k, v in TOP_25_COUNTRIES.items()}

    with engine.connect() as conn:
        for indicator_code, records in all_data.items():
            indicator_name = WB_INDICATORS.get(indicator_code, indicator_code)
            saved = 0

            for record in records:
                country_name = record["country"]["value"]
                country_code = name_to_code.get(country_name)

                if not country_code:
                    continue

                conn.execute(text("""
                    INSERT INTO dim_indicator_data
                        (country_code, country_name, indicator_code, indicator_name, year, value)
                    VALUES
                        (:code, :name, :ind_code, :ind_name, :year, :value)
                    ON CONFLICT (country_code, indicator_code, year)
                    DO UPDATE SET value = EXCLUDED.value
                """), {
                    "code":     country_code,
                    "name":     country_name,
                    "ind_code": indicator_code,
                    "ind_name": indicator_name,
                    "year":     int(record["date"]),
                    "value":    record["value"]
                })
                saved += 1

            total_saved += saved
            print(f"  ✅ {indicator_name}: {saved} records")

        conn.commit()

    print(f"\n✅ Total World Bank records saved: {total_saved}")


def load_precious_metals(metals):
    """
    Saves gold and silver prices into dim_precious_metals.
    Uses UPSERT — always keeps the latest price.
    """
    engine = get_engine()

    with engine.connect() as conn:
        for m in metals:
            conn.execute(text("""
                INSERT INTO dim_precious_metals
                    (symbol, name, price_usd, unit, price_date)
                VALUES
                    (:symbol, :name, :price, :unit, :date)
                ON CONFLICT (symbol)
                DO UPDATE SET
                    price_usd  = EXCLUDED.price_usd,
                    price_date = EXCLUDED.price_date,
                    updated_at = NOW()
            """), {
                "symbol": m["symbol"],
                "name":   m["name"],
                "price":  m["price"],
                "unit":   m["unit"],
                "date":   m["date"] if m["date"] else None
            })

        conn.commit()

    print(f"✅ Saved {len(metals)} precious metal prices")


def load_top_products(products):
    """
    Saves top traded products per country into dim_top_products.
    Uses UPSERT — updates if same country+trade_type+rank exists.
    """
    engine = get_engine()

    # Build country code → name lookup
    code_to_name = TOP_25_COUNTRIES

    with engine.connect() as conn:
        for p in products:
            conn.execute(text("""
                INSERT INTO dim_top_products
                    (country_code, country_name, trade_type, product_name, rank)
                VALUES
                    (:code, :name, :trade_type, :product, :rank)
                ON CONFLICT (country_code, trade_type, rank)
                DO UPDATE SET product_name = EXCLUDED.product_name
            """), {
                "code":       p["country_code"],
                "name":       code_to_name.get(p["country_code"], ""),
                "trade_type": p["trade_type"],
                "product":    p["product_name"],
                "rank":       p["rank"]
            })

        conn.commit()

    print(f"✅ Saved {len(products)} top product records")


def load_commodity_prices(commodities):
    """Saves commodity prices. Same as before."""
    engine = get_engine()

    with engine.connect() as conn:
        for item in commodities:
            conn.execute(text("""
                INSERT INTO dim_commodity_price
                    (symbol, commodity_name, price, unit, price_date)
                VALUES
                    (:symbol, :name, :price, :unit, :date)
                ON CONFLICT (symbol)
                DO UPDATE SET
                    price      = EXCLUDED.price,
                    price_date = EXCLUDED.price_date,
                    updated_at = NOW()
            """), {
                "symbol": item["symbol"],
                "name":   item["name"],
                "price":  item["price"],
                "unit":   item["unit"],
                "date":   item["date"]
            })
        conn.commit()

    print(f"✅ Saved {len(commodities)} commodity prices")


def load_exchange_rates(rates):
    """Saves exchange rates. Same as before."""
    engine = get_engine()

    with engine.connect() as conn:
        for item in rates:
            conn.execute(text("""
                INSERT INTO dim_exchange_rate
                    (currency_code, currency_name, rate_vs_usd, rate_date)
                VALUES
                    (:code, :name, :rate, :date)
                ON CONFLICT (currency_code)
                DO UPDATE SET
                    rate_vs_usd = EXCLUDED.rate_vs_usd,
                    rate_date   = EXCLUDED.rate_date,
                    updated_at  = NOW()
            """), {
                "code": item["currency_code"],
                "name": item["currency_name"],
                "rate": item["rate_vs_usd"],
                "date": item["date"]
            })
        conn.commit()

    print(f"✅ Saved {len(rates)} exchange rates")


def run_full_pipeline():
    """
    Master function — runs the complete ETL pipeline.
    
    Order matters:
    1. World Bank data (slow, most records)
    2. Precious metals (fast)
    3. Commodities (medium)
    4. Exchange rates (fast)
    5. Top products (instant — from curated data)
    """
    from src.utils.api_clients import (
        get_all_world_bank_data,
        get_precious_metals,
        get_commodity_prices,
        get_exchange_rates
    )
    from src.etl.extract.scraper import get_top_products

    print("=" * 50)
    print("FULL ETL PIPELINE STARTING")
    print("=" * 50)

    print("\n[1/5] Fetching World Bank indicators...")
    all_wb_data = get_all_world_bank_data(start_year=2015, end_year=2023)
    load_all_world_bank_indicators(all_wb_data)

    print("\n[2/5] Fetching precious metals...")
    metals = get_precious_metals()
    if metals:
        load_precious_metals(metals)

    print("\n[3/5] Fetching commodity prices...")
    commodities = get_commodity_prices()
    load_commodity_prices(commodities)

    print("\n[4/5] Fetching exchange rates...")
    rates = get_exchange_rates()
    load_exchange_rates(rates)

    print("\n[5/5] Loading top traded products...")
    products = get_top_products()
    load_top_products(products)

    print("\n" + "=" * 50)
    print("✅ PIPELINE COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    run_full_pipeline()