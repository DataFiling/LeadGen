import os
from fastapi import FastAPI, HTTPException, Header
from typing import Optional
from scraper import run_real_estate_scraper

app = FastAPI(title="Real Estate Lead API")

# Retrieve the secret from environment variables
# In RapidAPI, this ensures only paying users can reach your server
RAPIDAPI_PROXY_SECRET = os.getenv("RAPIDAPI_PROXY_SECRET")

@app.get("/")
async def health_check():
    return {"status": "active", "message": "Server is running"}

@app.get("/leads/{zip_code}")
async def get_leads(
    zip_code: str, 
    x_rapidapi_proxy_secret: Optional[str] = Header(None)
):
    # 1. Security check for RapidAPI
    if RAPIDAPI_PROXY_SECRET and x_rapidapi_proxy_secret != RAPIDAPI_PROXY_SECRET:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    # 2. Basic ZIP code validation
    if not zip_code.isdigit() or len(zip_code) != 5:
        raise HTTPException(status_code=400, detail="Invalid ZIP code format")

    # 3. Trigger the scraper
    try:
        data = await run_real_estate_scraper(zip_code)
        
        if "error" in data:
            raise HTTPException(status_code=500, detail=data["error"])
            
        return {
            "zip_code": zip_code,
            "total_leads": len(data),
            "results": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
