import asyncio
from playwright.async_api import async_playwright
# Import the specific stealth function from the logic folder of the library
from playwright_stealth.stealth import stealth

async def run_scrape_logic(zip_code: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        # We are now calling the function we specifically imported above
        try:
            await stealth(page)
        except Exception as e:
            print(f"Stealth warning: {e}")
        
        url = f"https://www.realtor.com/realestateandhomes-search/{zip_code}"
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_selector("[data-testid='property-card']", timeout=15000)
            
            listings = await page.query_selector_all("[data-testid='property-card']")
            
            leads = []
            for listing in listings[:10]:
                address_el = await listing.query_selector("[data-label='pc-address']")
                price_el = await listing.query_selector("[data-label='pc-price']")
                
                if address_el and price_el:
                    leads.append({
                        "address": (await address_el.inner_text()).strip(),
                        "price": (await price_el.inner_text()).strip()
                    })
            
            await browser.close()
            return leads

        except Exception as e:
            await browser.close()
            return {"error": str(e)}
