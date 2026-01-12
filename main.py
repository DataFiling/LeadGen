import os
from fastapi import FastAPI, Request, HTTPException
# This import style prevents the "module not callable" error
from scraper import run_real_estate_scraper

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "active", "message": "Server is running"}

@app.get("/leads/{zip_code}")
async def get_leads(zip_code: str, request: Request):
    # 1. Security Check: Verify the RapidAPI Proxy Secret
    expected_secret = os.getenv("RAPIDAPI_PROXY_SECRET")
    received_secret = request.headers.get("X-RapidAPI-Proxy-Secret")

    if not expected_secret or received_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid Secret Key")

    # 2. Execution: Call the function imported from scraper.py
    try:
        data = await run_real_estate_scraper(zip_code)
        return {"zip_code": zip_code, "leads": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Railway provides the PORT variable; default to 8080 as seen in your logs
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
