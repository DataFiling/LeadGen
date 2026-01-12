import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
import engine 

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

    # Use the long-form call to the function inside engine.py
    try:
        # engine = the file, run_scrape_logic = the function
        result = await engine.run_scrape_logic(zip_code)
        return {"zip_code": zip_code, "leads": result}
    except Exception as e:
        return {
            "error": "Call failed",
            "details": str(e),
            "debug_info": f"Is engine a module? {str(type(engine))}"
        }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
