import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load variables from .env file into Python
load_dotenv()

def get_connection_string():
    '''Build the database URL from environment variables'''
    host     = os.getenv('DB_HOST', 'localhost')
    port     = os.getenv('DB_PORT', '5432')
    dbname   = os.getenv('DB_NAME', 'trade_intelligence')
    user     = os.getenv('DB_USER', 'tradeuser')
    password = os.getenv('DB_PASSWORD', 'tradepass')

    # Format: postgresql://user:password@host:port/dbname
    return f'postgresql://{user}:{password}@{host}:{port}/{dbname}'

def get_engine():
    '''Create a SQLAlchemy engine - our main DB connection object'''
    connection_string = get_connection_string()
    engine = create_engine(
        connection_string,
        pool_size=5,        # keep 5 connections ready
        max_overflow=10,    # allow 10 extra if needed
        pool_timeout=30     # wait max 30s for a connection
    )
    return engine

def test_connection():
    '''Quick test to verify DB is reachable'''
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text('SELECT version()'))
            version = result.fetchone()[0]
            print(f'✅ Connected to: {version[:50]}')
            return True
    except Exception as e:
        print(f'Connection failed: {e}')
        return False

if __name__ == '__main__':
    test_connection()
