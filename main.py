import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
# Explicitly importing our renamed file
import engine 

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "active", "message": "Server is running"}

@app.get("/leads/{zip_code}")
async def get_leads(zip_code: str, request: Request):
    # 1. Security Check
    expected_secret = os.getenv("RAPIDAPI_PROXY_SECRET")
    received_secret = request.headers.get("X-RapidAPI-Proxy-Secret")

    if not expected_secret or received_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid Secret Key")

    # 2. Execution logic
    try:
        # We call the module (engine) then the function (run_scrape_logic)
        data = await engine.run_scrape_logic(zip_code)
        return {"zip_code": zip_code, "leads": data}
    except Exception as e:
        # If the calling error occurs here, it will be caught specifically
        return {"error": "Execution error", "details": str(e)}

if __name__ == "__main__":
    # Railway usually defaults to 8080 or 8000; check your logs if this fails
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
