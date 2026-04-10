from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# These are default settings that apply to all tasks in this DAG
default_args = {
    'owner':            'trade-team',
    'retries':          2,                       # retry failed tasks 2 times
    'retry_delay':      timedelta(minutes=5),    # wait 5 mins between retries
    'email_on_failure': False,
}

# Create the DAG
# schedule_interval='0 6 * * *' means: run at 6:00 AM every day
# This is called a "cron expression" — standard way to define schedules
dag = DAG(
    dag_id='trade_intelligence_pipeline',
    default_args=default_args,
    description='Fetches trade data daily and loads into PostgreSQL',
    schedule_interval='0 6 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,        # don't run for past dates we missed
    tags=['trade', 'etl']
)


# --- Task functions ---
# Each function = one step in the pipeline

def task_fetch_world_bank():
    """Fetches all 8 World Bank indicators for 25 countries."""
    from src.utils.api_clients import get_all_world_bank_data
    from src.etl.load.loader import load_all_world_bank_indicators
    print("Fetching World Bank data...")
    data = get_all_world_bank_data(start_year=2015, end_year=2024)
    load_all_world_bank_indicators(data)
    print("World Bank data loaded successfully")


def task_fetch_commodities():
    """Fetches commodity prices from Alpha Vantage."""
    from src.utils.api_clients import get_commodity_prices
    from src.etl.load.loader import load_commodity_prices
    print("Fetching commodity prices...")
    commodities = get_commodity_prices()
    load_commodity_prices(commodities)
    print(f"Loaded {len(commodities)} commodities")


def task_fetch_precious_metals():
    """Fetches gold and silver prices."""
    from src.utils.api_clients import get_precious_metals
    from src.etl.load.loader import load_precious_metals
    print("Fetching precious metals...")
    metals = get_precious_metals()
    if metals:
        load_precious_metals(metals)
    print(f"Loaded {len(metals)} metals")


def task_fetch_forex():
    """Fetches live exchange rates."""
    from src.utils.api_clients import get_exchange_rates
    from src.etl.load.loader import load_exchange_rates
    print("Fetching exchange rates...")
    rates = get_exchange_rates()
    load_exchange_rates(rates)
    print(f"Loaded {len(rates)} exchange rates")


def task_load_top_products():
    """Loads curated top export/import products per country."""
    from src.etl.extract.scraper import get_top_products
    from src.etl.load.loader import load_top_products
    print("Loading top products...")
    products = get_top_products()
    load_top_products(products)
    print(f"Loaded {len(products)} product records")


# --- Create tasks ---
# PythonOperator runs a Python function as a task

t1 = PythonOperator(
    task_id='fetch_world_bank',
    python_callable=task_fetch_world_bank,
    dag=dag
)

t2 = PythonOperator(
    task_id='fetch_commodities',
    python_callable=task_fetch_commodities,
    dag=dag
)

t3 = PythonOperator(
    task_id='fetch_precious_metals',
    python_callable=task_fetch_precious_metals,
    dag=dag
)

t4 = PythonOperator(
    task_id='fetch_forex',
    python_callable=task_fetch_forex,
    dag=dag
)

t5 = PythonOperator(
    task_id='load_top_products',
    python_callable=task_load_top_products,
    dag=dag
)

# --- Define task order ---
# >> means "then run"
# t1 runs first, then t2, t3, t4 run in parallel, then t5
t1 >> [t2, t3, t4] >> t5