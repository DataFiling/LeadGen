import asyncio
from playwright.async_api import async_playwright
# Using the specific function import to avoid module conflicts
from playwright_stealth import stealth

async def run_scrape_logic(zip_code: str):
    """
    Handles the browser lifecycle and data extraction.
    """
    async with async_playwright() as p:
        # Configuration for stable cloud deployment
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        # Explicitly apply the stealth function
        await stealth(page)
        
        url = f"https://www.realtor.com/realestateandhomes-search/{zip_code}"
        
        try:
            # Navigate to the target ZIP code search
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for property cards to be visible
            await page.wait_for_selector("[data-testid='property-card']", timeout=15000)
            
            # Select the first 10 listings
            listings = await page.query_selector_all("[data-testid='property-card']")
            
            leads = []
            for listing in listings[:10]:
                address_el = await listing.query_selector("[data-label='pc-address']")
                price_el = await listing.query_selector("[data-label='pc-price']")
                
                if address_el and price_el:
                    leads.append({
                        "address": (await address_el.inner_text()).strip().replace('\n', ' '),
                        "price": (await price_el.inner_text()).strip(),
                        "status": "Active"
                    })
            
            await browser.close()
            return leads

        except Exception as e:
            await browser.close()
            return {"error": str(e)}
