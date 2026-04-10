import os
import time
import wbgapi as wb
import requests
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

TOP_25_COUNTRIES = {
    "USA": "United States",
    "CHN": "China",
    "DEU": "Germany",
    "JPN": "Japan",
    "GBR": "United Kingdom",
    "FRA": "France",
    "IND": "India",
    "ITA": "Italy",
    "KOR": "South Korea",
    "CAN": "Canada",
    "RUS": "Russia",
    "MEX": "Mexico",
    "AUS": "Australia",
    "ESP": "Spain",
    "IDN": "Indonesia",
    "NLD": "Netherlands",
    "SAU": "Saudi Arabia",
    "TUR": "Turkey",
    "CHE": "Switzerland",
    "POL": "Poland",
    "BEL": "Belgium",
    "SWE": "Sweden",
    "BRA": "Brazil",
    "ARG": "Argentina",
    "ZAF": "South Africa",
}

# World Bank indicator codes with friendly names
# These are all official World Bank indicators — fully free
WB_INDICATORS = {
    "NY.GDP.MKTP.CD":   "GDP (current US$)",
    "NE.EXP.GNFS.CD":   "Total Exports (US$)",
    "NE.IMP.GNFS.CD":   "Total Imports (US$)",
    "NE.RSB.GNFS.CD":   "Trade Balance (US$)",
    "FP.CPI.TOTL.ZG":   "Inflation Rate (%)",
    "SL.UEM.TOTL.ZS":   "Unemployment Rate (%)",
    "TG.VAL.TOTL.GD.ZS":"Trade as % of GDP",
    "NY.GDP.PCAP.CD":   "GDP Per Capita (US$)",
}


def get_world_bank_indicator(indicator_code, start_year=2015, end_year=2023):
    """
    Fetches a single World Bank indicator for all 25 countries.
    Returns a list of records in standard format.
    """
    country_codes = list(TOP_25_COUNTRIES.keys())

    try:
        df = wb.data.DataFrame(
            indicator_code,
            economy=country_codes,
            time=range(start_year, end_year + 1),
            labels=True
        )

        df = df.reset_index()
        df = df.melt(
            id_vars=["Country"],
            var_name="date",
            value_name="value"
        )

        df["date"] = df["date"].str.replace("YR", "")
        df = df.dropna(subset=["value"])
        df = df[df["date"] != "economy"]

        records = []
        for _, row in df.iterrows():
            records.append({
                "date":    row["date"],
                "value":   float(row["value"]),
                "country": {"value": row["Country"]}
            })

        return records

    except Exception as e:
        print(f"  ❌ Failed {indicator_code}: {e}")
        return []


def get_all_world_bank_data(start_year=2015, end_year=2023):
    """
    Fetches ALL indicators for all 25 countries.
    Returns a dict: { indicator_code: [records] }
    """
    print(f"Fetching {len(WB_INDICATORS)} indicators for {len(TOP_25_COUNTRIES)} countries...")
    all_data = {}

    for code, name in WB_INDICATORS.items():
        print(f"  Fetching: {name}...")
        records = get_world_bank_indicator(code, start_year, end_year)
        all_data[code] = records
        print(f"  ✅ {len(records)} records")
        time.sleep(0.5)  # be polite to the API

    return all_data


def get_commodity_prices():
    """
    Fetches commodity prices from Alpha Vantage.
    """
    print("Fetching commodity prices...")

    commodities = {
        "WTI":         "Crude Oil (WTI)",
        "BRENT":       "Crude Oil (Brent)",
        "NATURAL_GAS": "Natural Gas",
        "ALUMINUM":    "Aluminum",
        "WHEAT":       "Wheat",
        "CORN":        "Corn",
        "COTTON":      "Cotton",
        "SUGAR":       "Sugar",
        "COFFEE":      "Coffee",
    }

    results = []

    for symbol, name in commodities.items():
        try:
            url = "https://www.alphavantage.co/query"
            params = {
                "function": symbol,
                "interval": "monthly",
                "apikey":   ALPHA_VANTAGE_KEY
            }
            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            if "data" in data and len(data["data"]) > 0:
                latest = data["data"][0]
                results.append({
                    "symbol": symbol,
                    "name":   name,
                    "price":  float(latest["value"]),
                    "date":   latest["date"],
                    "unit":   data.get("unit", "USD")
                })
                print(f"  ✅ {name}: ${latest['value']}")

        except Exception as e:
            print(f"  ❌ {name}: {e}")

    return results


def get_precious_metals():
    """
    Fetches gold, silver, platinum prices.
    Uses exchangerate-api.com which supports XAU and XAG.
    Same API we already use for forex — no extra key needed.
    """
    print("Fetching precious metals...")

    try:
        # Fetch rates with gold (XAU) as the base currency
        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/XAU",
            timeout=15
        )
        data = response.json()
        rates = data.get("rates", {})

        results = []

        # If 1 XAU = X USD, then gold price = X USD
        if "USD" in rates:
            gold_price = rates["USD"]
            results.append({
                "symbol": "XAU",
                "name":   "Gold",
                "price":  round(gold_price, 2),
                "date":   data.get("date", ""),
                "unit":   "USD per troy oz"
            })
            print(f"  ✅ Gold: ${gold_price:,.2f}")

        # Fetch silver
        response2 = requests.get(
            "https://api.exchangerate-api.com/v4/latest/XAG",
            timeout=15
        )
        data2 = response2.json()
        rates2 = data2.get("rates", {})

        if "USD" in rates2:
            silver_price = rates2["USD"]
            results.append({
                "symbol": "XAG",
                "name":   "Silver",
                "price":  round(silver_price, 2),
                "date":   data2.get("date", ""),
                "unit":   "USD per troy oz"
            })
            print(f"  ✅ Silver: ${silver_price:,.2f}")

        return results

    except Exception as e:
        print(f"❌ Precious metals failed: {e}")
        return []


def get_exchange_rates():
    """
    Fetches live exchange rates vs USD.
    """
    print("Fetching exchange rates...")

    try:
        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD",
            timeout=15
        )
        data = response.json()

        currencies = {
            "EUR": "Euro",           "GBP": "British Pound",
            "JPY": "Japanese Yen",   "CNY": "Chinese Yuan",
            "INR": "Indian Rupee",   "KRW": "South Korean Won",
            "CAD": "Canadian Dollar","RUB": "Russian Ruble",
            "MXN": "Mexican Peso",   "AUD": "Australian Dollar",
            "CHF": "Swiss Franc",    "BRL": "Brazilian Real",
            "SAR": "Saudi Riyal",    "TRY": "Turkish Lira",
            "ZAR": "South African Rand",
        }

        results = []
        rates = data.get("rates", {})

        for code, name in currencies.items():
            if code in rates:
                results.append({
                    "currency_code": code,
                    "currency_name": name,
                    "rate_vs_usd":   rates[code],
                    "date":          data.get("date", "")
                })
                print(f"  ✅ {code}: {rates[code]}")

        return results

    except Exception as e:
        print(f"❌ Exchange rates failed: {e}")
        return []


if __name__ == "__main__":
    print("=== Testing all data sources ===\n")

    all_wb = get_all_world_bank_data(start_year=2020, end_year=2026)
    total = sum(len(v) for v in all_wb.values())
    print(f"\nTotal World Bank records: {total}\n")

    metals = get_precious_metals()
    print(f"\nPrecious metals: {len(metals)}\n")

    commodities = get_commodity_prices()
    print(f"\nCommodities: {len(commodities)}\n")

    rates = get_exchange_rates()
    print(f"\nExchange rates: {len(rates)}")