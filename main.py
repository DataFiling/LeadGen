from fastapi import FastAPI, HTTPException
from scraper import run_scraper  # This imports the logic from your scraper.py
import uvicorn

app = FastAPI(title="Real Estate Lead API")

@app.get("/")
async def root():
    return {"message": "API is Online. Awaiting Observation."}

# This is exactly where your snippet goes, integrated with the scraper
@app.get("/leads/{zip_code}")
async def get_leads(zip_code: str):
    # 1. Validation: Ensure the ZIP is 5 digits
    if not zip_code.isdigit() or len(zip_code) != 5:
        raise HTTPException(status_code=400, detail="Invalid ZIP code format.")
    
    # 2. Execution: Call the function inside scraper.py
    data = await run_scraper(zip_code)
    
    # 3. Error Handling: If the scraper fails, let the user know
    if isinstance(data, dict) and "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
        
    # 4. Response: Send the data back to RapidAPI
    return {
        "status": "success",
        "zip_code": zip_code,
        "count": len(data),
        "leads": data
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
