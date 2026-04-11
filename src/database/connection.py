import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def get_connection_string():
    use_supabase = os.getenv("USE_SUPABASE", "false").lower() == "true"
    if use_supabase:
        return os.getenv("SUPABASE_DB_URL")
    return f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

def get_engine():
    return create_engine(
        get_connection_string(),
        pool_size=5,
        max_overflow=10,
        pool_timeout=30
    )

def test_connection():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            print(f"✅ Connected: {result.fetchone()[0][:50]}")
            return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()