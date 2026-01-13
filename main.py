import os
import uvicorn
import asyncio
from fastapi import FastAPI, Request, HTTPException
from playwright.async_api import async_playwright

# This is the line the server was missing
app = FastAPI()

# --- THE SCRAPER LOGIC ---
async def run_scrape_logic(zip_code: str):
    async with async_playwright() as p:
        # Launch browser with settings that work on Railway
        browser = await p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        
        # This makes the bot look like a real person on a computer
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        url = f"https://www.realtor.com/realestateandhomes-search/{zip_code}"
        
        try:
            # Go to the website and wait for it to load
            await page.goto(url, wait_until="load", timeout=60000)
            
            # Wait 10 seconds for the houses to show up
            await page.wait_for_selector("[data-testid='property-card']", timeout=15000)
            
            listings = await page.query_selector_all("[data-testid='property-card']")
            
            leads = []
            for listing in listings[:10]:
                address_el = await listing.query_selector("[data-label='pc-address']")
                price_el = await listing.query_selector("[data-label='pc-price']")
                
                if address_el and price_el:
                    addr = await address_el.inner_text()
                    pri = await price_el.inner_text()
                    leads.append({
                        "address": addr.strip().replace('\n', ' '),
                        "price": pri.strip()
                    })
            
            await browser.close()
            return leads

        except Exception as e:
            await browser.close()
            return {"error": "timeout or blocked", "details": str(e)}

# --- THE API ROUTES ---

@app.get("/")
async def health_check():
    # This helps you check if the server is awake
    return {"status": "active", "message": "Server is running"}

@app.get("/leads/{zip_code}")
async def get_leads(zip_code: str, request: Request):
    # Security Check (RapidAPI Secret)
    expected_secret = os.getenv("RAPIDAPI_PROXY_SECRET")
    received_secret = request.headers.get("X-RapidAPI-Proxy-Secret")

    if not expected_secret or received_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Run the scraper
    data = await run_scrape_logic(zip_code)
    return {"zip_code": zip_code, "leads": data}

if __name__ == "__main__":
    # Get the port from Railway or use 8080 as a backup
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
