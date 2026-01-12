import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
# This is the most direct way to import the function
from engine import run_scrape_logic

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "active"}

@app.get("/leads/{zip_code}")
async def get_leads(zip_code: str, request: Request):
    # Security check
    expected_secret = os.getenv("RAPIDAPI_PROXY_SECRET")
    received_secret = request.headers.get("X-RapidAPI-Proxy-Secret")

    if not expected_secret or received_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        # We call the function name directly now
        data = await run_scrape_logic(zip_code)
        return {"zip_code": zip_code, "leads": data}
    except Exception as e:
        # This will tell us if it's STILL a calling error or something new
        return {"error": "Final attempt error", "details": str(e), "type": str(type(e))}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
