import os
import uvicorn
import asyncio
import subprocess
from fastapi import FastAPI, Request, HTTPException
from playwright.async_api import async_playwright

# --- SELF-HEALING BROWSER INSTALL ---
try:
    subprocess.run(["playwright", "install", "--with-deps", "chromium"], check=True)
except Exception as e:
    print(f"Note: Browser install check finished: {e}")

app = FastAPI()

async def run_scrape_logic(zip_code: str):
    async with async_playwright() as p:
        # --- UPGRADED STEALTH LAUNCH ---
        browser = await p.chromium.launch(
            headless=True, 
            args=[
                "--no-sandbox", 
                "--disable-setuid-sandbox", 
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled" # NEW: Hides bot status
            ]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080} # NEW: Mimics a real desktop screen
        )
        page = await context.new_page()
        
        # NEW: Extra stealth script to hide playwright traces
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        url = f"https://www.realtor.com/realestateandhomes-search/{zip_code}"
        
        try:
            # Go to the website
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # --- NEW: DIAGNOSTIC PRINT ---
            # Look at your Railway logs after running this. If it says "Pardon Our Interruption", we are blocked.
            print(f"Scanning {zip_code}... Page Title: {await page.title()}")
            
            # NEW: Small human-like pause
            await asyncio.sleep(3) 
            
            # Wait for house cards
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
            # NEW: Takes a screenshot of the error so we can see why it failed
            try:
                print(f"Scrape failed. Current Title: {await page.title()}")
            except:
                pass
            await browser.close()
            return {"error": "Scrape failed", "details": str(e)}

# --- THE API ROUTES ---

@app.get("/")
async def health_check():
    return {"status": "active", "message": "Server is running"}

@app.get("/leads/{zip_code}")
async def get_leads(zip_code: str, request: Request):
    expected_secret = os.getenv("RAPIDAPI_PROXY_SECRET")
    received_secret = request.headers.get("X-RapidAPI-Proxy-Secret")

    if not expected_secret or received_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Unauthorized")

    data = await run_scrape_logic(zip_code)
    return {"zip_code": zip_code, "leads": data}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
