import requests
from bs4 import BeautifulSoup
import time

# Top exports and imports per country
# Source: CIA World Factbook + OEC public data
# This is curated data — accurate as of 2023
# We update this annually (same frequency as the underlying UN Comtrade data)

COUNTRY_TRADE_PRODUCTS = {
    "USA": {
        "exports": ["Refined Petroleum", "Crude Petroleum", "Cars", "Integrated Circuits", "Aircraft"],
        "imports": ["Cars", "Crude Petroleum", "Computers", "Broadcasting Equipment", "Pharmaceuticals"]
    },
    "CHN": {
        "exports": ["Broadcasting Equipment", "Computers", "Integrated Circuits", "Office Machine Parts", "Solar Panels"],
        "imports": ["Crude Petroleum", "Iron Ore", "Integrated Circuits", "Cars", "Soybeans"]
    },
    "DEU": {
        "exports": ["Cars", "Vehicle Parts", "Pharmaceuticals", "Aircraft", "Packaged Medicines"],
        "imports": ["Cars", "Crude Petroleum", "Vehicle Parts", "Computers", "Packaged Medicines"]
    },
    "JPN": {
        "exports": ["Cars", "Vehicle Parts", "Integrated Circuits", "Industrial Machinery", "Steel"],
        "imports": ["Crude Petroleum", "Coal", "Natural Gas", "Integrated Circuits", "Pharmaceuticals"]
    },
    "GBR": {
        "exports": ["Cars", "Crude Petroleum", "Packaged Medicines", "Gold", "Aircraft"],
        "imports": ["Cars", "Crude Petroleum", "Packaged Medicines", "Computers", "Broadcasting Equipment"]
    },
    "FRA": {
        "exports": ["Aircraft", "Packaged Medicines", "Cars", "Gas Turbines", "Wine"],
        "imports": ["Cars", "Crude Petroleum", "Packaged Medicines", "Aircraft", "Broadcasting Equipment"]
    },
    "IND": {
        "exports": ["Refined Petroleum", "Diamonds", "Packaged Medicines", "Rice", "Cars"],
        "imports": ["Crude Petroleum", "Gold", "Coal", "Diamonds", "Electronics"]
    },
    "ITA": {
        "exports": ["Cars", "Packaged Medicines", "Vehicle Parts", "Refined Petroleum", "Clothing"],
        "imports": ["Crude Petroleum", "Cars", "Packaged Medicines", "Natural Gas", "Vehicle Parts"]
    },
    "KOR": {
        "exports": ["Integrated Circuits", "Cars", "Refined Petroleum", "Steel", "Ships"],
        "imports": ["Crude Petroleum", "Integrated Circuits", "Coal", "Natural Gas", "Steel"]
    },
    "CAN": {
        "exports": ["Crude Petroleum", "Cars", "Gold", "Refined Petroleum", "Lumber"],
        "imports": ["Cars", "Vehicle Parts", "Computers", "Broadcasting Equipment", "Packaged Medicines"]
    },
    "RUS": {
        "exports": ["Crude Petroleum", "Refined Petroleum", "Natural Gas", "Coal", "Steel"],
        "imports": ["Cars", "Vehicle Parts", "Packaged Medicines", "Broadcasting Equipment", "Computers"]
    },
    "MEX": {
        "exports": ["Cars", "Vehicle Parts", "Computers", "Crude Petroleum", "Medical Instruments"],
        "imports": ["Refined Petroleum", "Vehicle Parts", "Broadcasting Equipment", "Cars", "Computers"]
    },
    "AUS": {
        "exports": ["Iron Ore", "Coal", "Gold", "Natural Gas", "Wheat"],
        "imports": ["Cars", "Crude Petroleum", "Refined Petroleum", "Computers", "Broadcasting Equipment"]
    },
    "ESP": {
        "exports": ["Cars", "Refined Petroleum", "Vehicle Parts", "Packaged Medicines", "Olive Oil"],
        "imports": ["Crude Petroleum", "Cars", "Vehicle Parts", "Packaged Medicines", "Computers"]
    },
    "IDN": {
        "exports": ["Coal", "Palm Oil", "Natural Gas", "Refined Petroleum", "Gold"],
        "imports": ["Crude Petroleum", "Refined Petroleum", "Machinery", "Steel", "Wheat"]
    },
    "NLD": {
        "exports": ["Refined Petroleum", "Broadcasting Equipment", "Computers", "Packaged Medicines", "Flowers"],
        "imports": ["Crude Petroleum", "Broadcasting Equipment", "Computers", "Refined Petroleum", "Cars"]
    },
    "SAU": {
        "exports": ["Crude Petroleum", "Refined Petroleum", "Ethylene Polymers", "Propylene Polymers", "Fertilizers"],
        "imports": ["Cars", "Broadcasting Equipment", "Packaged Medicines", "Gold", "Computers"]
    },
    "TUR": {
        "exports": ["Cars", "Vehicle Parts", "Steel", "Clothing", "Refined Petroleum"],
        "imports": ["Gold", "Crude Petroleum", "Steel", "Refined Petroleum", "Broadcasting Equipment"]
    },
    "CHE": {
        "exports": ["Gold", "Packaged Medicines", "Blood Fractions", "Watches", "Jewelry"],
        "imports": ["Gold", "Packaged Medicines", "Cars", "Jewelry", "Blood Fractions"]
    },
    "POL": {
        "exports": ["Cars", "Vehicle Parts", "Furniture", "Broadcasting Equipment", "Computers"],
        "imports": ["Cars", "Crude Petroleum", "Broadcasting Equipment", "Vehicle Parts", "Packaged Medicines"]
    },
    "BEL": {
        "exports": ["Cars", "Packaged Medicines", "Refined Petroleum", "Blood Fractions", "Diamonds"],
        "imports": ["Cars", "Crude Petroleum", "Packaged Medicines", "Refined Petroleum", "Diamonds"]
    },
    "SWE": {
        "exports": ["Cars", "Packaged Medicines", "Refined Petroleum", "Lumber", "Vehicle Parts"],
        "imports": ["Cars", "Crude Petroleum", "Broadcasting Equipment", "Packaged Medicines", "Computers"]
    },
    "BRA": {
        "exports": ["Soybeans", "Crude Petroleum", "Iron Ore", "Corn", "Sugar"],
        "imports": ["Refined Petroleum", "Cars", "Vehicle Parts", "Packaged Medicines", "Fertilizers"]
    },
    "ARG": {
        "exports": ["Soybeans", "Soybean Oil", "Corn", "Wheat", "Beef"],
        "imports": ["Refined Petroleum", "Cars", "Vehicle Parts", "Packaged Medicines", "Natural Gas"]
    },
    "ZAF": {
        "exports": ["Gold", "Platinum", "Iron Ore", "Coal", "Diamonds"],
        "imports": ["Crude Petroleum", "Refined Petroleum", "Cars", "Packaged Medicines", "Broadcasting Equipment"]
    },
}


def get_top_products():
    """
    Returns top exports and imports for all 25 countries.
    Data is curated from OEC/CIA World Factbook (2023).
    Same underlying source as TradeMap — UN Comtrade compiled data.
    
    Returns a list of records ready to insert into dim_top_products.
    """
    records = []

    for country_code, products in COUNTRY_TRADE_PRODUCTS.items():
        # Top exports
        for rank, product in enumerate(products["exports"], start=1):
            records.append({
                "country_code": country_code,
                "trade_type":   "export",
                "product_name": product,
                "rank":         rank
            })

        # Top imports
        for rank, product in enumerate(products["imports"], start=1):
            records.append({
                "country_code": country_code,
                "trade_type":   "import",
                "product_name": product,
                "rank":         rank
            })

    print(f"✅ Got top products for {len(COUNTRY_TRADE_PRODUCTS)} countries")
    print(f"   Total records: {len(records)}")
    return records


if __name__ == "__main__":
    results = get_top_products()
    # Show sample for India
    india = [r for r in results if r["country_code"] == "IND"]
    print("\nIndia sample:")
    for r in india:
        print(f"  {r['trade_type'].upper()} #{r['rank']}: {r['product_name']}")