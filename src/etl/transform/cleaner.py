import pandas as pd

def clean_gdp_data(raw_records):
    """
    Takes raw records from World Bank API and cleans them.
    
    Input:  list of dicts (messy, from API)
    Output: Pandas DataFrame (clean, ready for database)
    """

    if not raw_records:
        print("No records to clean")
        return pd.DataFrame()

    # Step 1: Turn the list into a DataFrame (like an Excel table in Python)
    df = pd.DataFrame(raw_records)

    # Step 2: Pull the country name out of the nested dict
    # Raw data looks like: {"country": {"value": "India"}, "date": "2023", "value": 123}
    # We want a flat column called "country_name"
    df["country_name"] = df["country"].apply(lambda x: x["value"])

    # Step 3: Keep only the columns we actually need
    df = df[["country_name", "date", "value"]]

    # Step 4: Rename columns to match our database column names
    df = df.rename(columns={
        "date":  "year",
        "value": "gdp_usd"
    })

    # Step 5: Drop rows where GDP value is missing
    df = df.dropna(subset=["gdp_usd"])

    # Step 6: Make sure year is an integer and GDP is a float
    df["year"]    = df["year"].astype(int)
    df["gdp_usd"] = df["gdp_usd"].astype(float)

    # Step 7: Sort by year, newest first
    df = df.sort_values("year", ascending=False).reset_index(drop=True)

    return df


def test_cleaner():
    """
    Test the cleaner using mock data.
    """
    # Import our API function from the previous file
    from src.utils.api_clients import get_world_bank_data

    print("Fetching raw data...")
    raw = get_world_bank_data("NY.GDP.MKTP.CD", country="IND")

    print("Cleaning data...")
    clean = clean_gdp_data(raw)

    print(f"\nClean DataFrame shape: {clean.shape[0]} rows, {clean.shape[1]} columns")
    print("\nFirst few rows:")
    print(clean.to_string(index=False))

    print("\nColumn data types:")
    print(clean.dtypes)


if __name__ == "__main__":
    test_cleaner()