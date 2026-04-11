import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

LOCAL_URL    = "postgresql://tradeuser:tradepass@localhost:5432/trade_intelligence"
SUPABASE_URL = os.getenv("SUPABASE_DB_URL")

TABLES = [
    "dim_indicator_data",
    "dim_commodity_price",
    "dim_exchange_rate",
    "dim_precious_metals",
    "dim_top_products",
]

def migrate():
    local    = create_engine(LOCAL_URL)
    supabase = create_engine(SUPABASE_URL)

    for table in TABLES:
        print(f"Migrating {table}...")
        with local.connect() as src:
            rows = src.execute(text(f"SELECT * FROM {table}")).fetchall()
            cols = src.execute(text(f"SELECT * FROM {table} LIMIT 0")).keys()
            col_list = list(cols)

        if not rows:
            print(f"  ⚠️ No data in {table}, skipping")
            continue

        with supabase.connect() as dst:
            dst.execute(text(f"TRUNCATE {table} RESTART IDENTITY CASCADE"))
            for row in rows:
                placeholders = ", ".join([f":{c}" for c in col_list])
                col_names    = ", ".join(col_list)
                dst.execute(
                    text(f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"),
                    dict(zip(col_list, row))
                )
            dst.commit()
        print(f"  ✅ {len(rows)} rows migrated")

    print("\n✅ Migration complete!")

if __name__ == "__main__":
    migrate()