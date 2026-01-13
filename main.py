import os
import uvicorn
import asyncio
import subprocess
from fastapi import FastAPI, Request, HTTPException
from playwright.async_api import async_playwright

# --- SELF-HEALING BROWSER INSTALL ---
# This ensures Chromium is present even if the Railway build step skipped it
try:
    print("Checking for Chromium...")
    subprocess.run(["playwright", "install", "--with-deps", "chromium"], check=True)
except Exception as e:
    print(f"Note: Browser install check finished: {e}")

app = FastAPI()

# --- THE SCRAPER LOGIC ---
async def run_scrape_logic(zip_code: str):
    async with async_playwright() as p:
        # Launch browser with settings for low-memory environments
        browser = await p.chromium.launch(
            headless=True, 
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox", 
                "--disable-dev-shm-usage",
                "--single-process" # Helps on low RAM plans
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        url = f"https://www.realtor.com/realestateandhomes-search/{zip_code}"
        
        try:
            # Go to the website
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for house cards to appear
            await page.wait_for_selector("[data-testid='property-card']", timeout=20000)
            
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
            return {"error": "Scrape failed", "details": str(e)}

# --- THE API ROUTES ---

@app.get("/")
async def health_check():
    return {"status": "active", "message": "Server is running"}

@app.get("/leads/{zip_code}")
async def get_leads(zip_code: str, request: Request):
    # Security Check
    expected_secret = os.getenv("RAPIDAPI_PROXY_SECRET")
    received_secret = request.headers.get("X-RapidAPI-Proxy-Secret")

    if not expected_secret or received_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Unauthorized")

    data = await run_scrape_logic(zip_code)
    return {"zip_code": zip_code, "leads": data}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
