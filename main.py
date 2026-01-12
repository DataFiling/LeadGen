import os
import uvicorn
from fastapi import FastAPI, HTTPException, Header
from typing import Optional
from dotenv import load_dotenv

# Import the 'Violent Execution' logic from your scraper file
from scraper import run_scraper

# Load the Forbidden Theory (Environment Variables)
load_dotenv()

app = FastAPI(
    title="Kenotic Real Estate Lead API",
    description="Extracting high-potentiality leads from the Apophenic Substrate.",
    version="1.0.0"
)

# This secret should be set in your .env file or your hosting provider's dashboard.
# It ensures only the RapidAPI 'Watchers' can trigger your King (Scraper).
RAPIDAPI_PROXY_SECRET = os.getenv("RAPIDAPI_PROXY_SECRET", "default_secret_for_local_testing")

@app.get("/")
async def health_check():
    """
    Verification endpoint to ensure the Shell is active.
    """
    return {
        "status": "online",
        "message": "The Apophenic Substrate is stable. Awaiting Observation."
    }

@app.get("/leads/{zip_code}")
async def get_leads(
    zip_code: str, 
    x_rapidapi_proxy_secret: Optional[str] = Header(None)
):
    """
    The primary endpoint for generating leads.
    """
    # 1. Security Check: Block unauthorized entities from the Void
    if x_rapidapi_proxy_secret != RAPIDAPI_PROXY_SECRET:
        raise HTTPException(
            status_code=403, 
            detail="Unauthorized. Access is restricted to RapidAPI Proxy."
        )

    # 2. Validation: Ensure the ZIP code is a valid 5-digit string
    if not zip_code.isdigit() or len(zip_code) != 5:
        raise HTTPException(
            status_code=400, 
            detail="Invalid ZIP code. Please provide a 5-digit numeric code."
        )

    try:
        # 3. Execution: Command the scraper to observe the target environment
        data = await run_scraper(zip_code)

        # Handle internal scraper errors (like network blockages)
        if isinstance(data, dict) and "error" in data:
            raise HTTPException(status_code=502, detail=f"Scraper Error: {data['error']}")

        # 4. Return: Send the captured data back through the gateway
        return {
            "success": True,
            "zip_code": zip_code,
            "count": len(data),
            "leads": data,
            "note": "Apophenia processed. Contagious subjectivity avoided."
        }

    except Exception as e:
        # Catch-all for unexpected 'Kenotic' shifts
        raise HTTPException(status_code=500, detail=f"Internal Core Error: {str(e)}")

if __name__ == "__main__":
    # Launching the server on Port 8000
    # Port will be overridden by Railway/Render using environment variables
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
