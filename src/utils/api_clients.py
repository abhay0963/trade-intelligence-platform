import time
import requests

WORLD_BANK_BASE_URL = "https://api.worldbank.org/v2"

# Switch this to False when World Bank API is back up
MOCK_MODE = True

# Realistic fake data — same structure as what World Bank actually returns
# This lets us build and test everything without needing the live API
MOCK_GDP_DATA = [
    {"date": "2023", "value": 3732224000000, "country": {"value": "India"}},
    {"date": "2022", "value": 3385090000000, "country": {"value": "India"}},
    {"date": "2021", "value": 2694800000000, "country": {"value": "India"}},
    {"date": "2020", "value": 2667690000000, "country": {"value": "India"}},
    {"date": "2019", "value": 2870500000000, "country": {"value": "India"}},
    {"date": "2018", "value": 2702930000000, "country": {"value": "India"}},
]


def get_world_bank_data(indicator, country="all", start_year=2015, end_year=2023):
    """
    Fetch data from World Bank API.
    If MOCK_MODE is True, returns realistic fake data instead.
    """

    # Return mock data if API is down or we're testing
    if MOCK_MODE:
        print("[MOCK MODE] Returning fake data — flip MOCK_MODE=False when API is back")
        return MOCK_GDP_DATA

    url = f"{WORLD_BANK_BASE_URL}/country/{country}/indicator/{indicator}"
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 1000
    }

    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if len(data) < 2 or data[1] is None:
                print("No data returned")
                return []

            return data[1]

        except requests.exceptions.HTTPError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                print("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("All 3 attempts failed. Try enabling MOCK_MODE=True")
                return []

        except requests.exceptions.ConnectionError:
            print("No internet connection or API unreachable.")
            return []


def test_world_bank():
    """
    Fetches India GDP and prints it.
    Works in both mock and live mode.
    """
    print("Fetching India GDP...\n")

    results = get_world_bank_data(
        indicator="NY.GDP.MKTP.CD",
        country="IND",
        start_year=2018,
        end_year=2023
    )

    print(f"Got {len(results)} records\n")

    for record in results:
        year  = record["date"]
        value = record["value"]
        name  = record["country"]["value"]
        if value:
            print(f"{name} | {year} | GDP: ${value:,.0f}")


if __name__ == "__main__":
    test_world_bank()