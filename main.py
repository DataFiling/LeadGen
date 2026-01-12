import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
import engine # This imports your engine.py file

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
        # Call the function inside engine.py
        data = await engine.run_scrape_logic(zip_code)
        return {"zip_code": zip_code, "leads": data}
    except Exception as e:
        return {"error": "Scraper Error", "details": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
