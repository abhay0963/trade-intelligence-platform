import os
from dotenv import load_dotenv

load_dotenv()

def test_groq():
    """
    Sends a simple message to Groq and prints the response.
    If this works, our AI layer will work.
    """
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env")
        return False

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # fast free model on Groq
        messages=[
            {
                "role": "user",
                "content": "Say exactly this: Groq API working"
            }
        ]
    )

    result = response.choices[0].message.content
    print(f"✅ Groq response: {result}")
    return True


def test_alpha_vantage():
    """
    Fetches current crude oil price from Alpha Vantage.
    If this works, our commodity data pipeline will work.
    """
    import requests

    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("❌ ALPHA_VANTAGE_API_KEY not found in .env")
        return False

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "WTI",        # West Texas Intermediate crude oil
        "interval":  "monthly",
        "apikey":    api_key
    }

    response = requests.get(url, params=params, timeout=15)
    data = response.json()

    if "data" not in data:
        print(f"❌ Alpha Vantage error: {data}")
        return False

    # Get the most recent price
    latest = data["data"][0]
    print(f"✅ Crude oil price: ${latest['value']} on {latest['date']}")
    return True


if __name__ == "__main__":
    print("Testing API keys...\n")

    print("1. Testing Groq...")
    test_groq()

    print("\n2. Testing Alpha Vantage...")
    test_alpha_vantage()