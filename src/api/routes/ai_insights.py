import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class InsightRequest(BaseModel):
    country:      str
    country_code: Optional[str] = None
    indicators:   Optional[dict] = None
    top_exports:  Optional[list] = None
    top_imports:  Optional[list] = None

@router.post("")
def get_insights(request: InsightRequest):
    """
    Sends real country data to Groq and gets business intelligence back.
    The more data we pass, the better the analysis.
    """

    # Format indicators for the prompt
    ind_text = ""
    if request.indicators:
        for name, data in request.indicators.items():
            if data and data.get("value"):
                ind_text += f"  - {name}: {data['value']:,.2f} (Year: {data['year']})\n"

    exports_text = ", ".join(request.top_exports or [])
    imports_text = ", ".join(request.top_imports or [])

    prompt = f"""You are a senior trade economist and business intelligence analyst.

Here is real economic data for {request.country} from the World Bank (2023):

KEY INDICATORS:
{ind_text}

TOP 5 EXPORTS: {exports_text}
TOP 5 IMPORTS: {imports_text}

Based on this real data, provide:

1. ECONOMIC SUMMARY (2-3 sentences): What does this data tell us about {request.country}'s economy right now?

2. TRADE STRENGTHS: What does {request.country} do well based on its export profile?

3. TRADE WEAKNESSES: What vulnerabilities does the import profile and trade balance reveal?

4. TOP 3 BUSINESS OPPORTUNITIES: Specific, actionable opportunities for companies looking to enter {request.country}'s market. Reference the actual data.

5. STARTUP IDEA: One specific startup idea that would thrive in {request.country} given its current economic conditions. Include: what the startup does, why this country specifically, what data point supports this.

6. RISK FACTORS: 2-3 key risks based on the economic indicators.

Be specific and reference the actual numbers. Avoid generic statements."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )

    return {
        "country": request.country,
        "insight": response.choices[0].message.content
    }
