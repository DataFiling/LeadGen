import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
# Explicitly import the function name
import scraper 

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "active", "message": "Server is running"}

@app.get("/leads/{zip_code}")
async def get_leads(zip_code: str, request: Request):
    # Security check
    expected_secret = os.getenv("RAPIDAPI_PROXY_SECRET")
    received_secret = request.headers.get("X-RapidAPI-Proxy-Secret")

    if not expected_secret or received_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Call the specific function inside the scraper.py file
    # By using scraper.run_real_estate_scraper, we avoid the 'module' error
    try:
        data = await scraper.run_real_estate_scraper(zip_code)
        return {"zip_code": zip_code, "leads": data}
    except TypeError as e:
        return {"error": "Calling error", "details": str(e)}
    except Exception as e:
        return {"error": "General error", "details": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
