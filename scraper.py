import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth

async def run_real_estate_scraper(zip_code: str):
    """
    Launches a headless browser to scrape property listings from Realtor.com.
    """
    async with async_playwright() as p:
        # Launch Chromium with settings for Linux containers
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        # Apply stealth function (NOT the module)
        await stealth(page)
        
        url = f"https://www.realtor.com/realestateandhomes-search/{zip_code}"
        
        try:
            # Navigate and wait for content
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for property cards to render
            await page.wait_for_selector("[data-testid='property-card']", timeout=15000)
            
            listings = await page.query_selector_all("[data-testid='property-card']")
            
            leads = []
            for listing in listings[:10]:
                address_el = await listing.query_selector("[data-label='pc-address']")
                price_el = await listing.query_selector("[data-label='pc-price']")
                
                if address_el and price_el:
                    address_text = await address_el.inner_text()
                    price_text = await price_el.inner_text()
                    
                    leads.append({
                        "address": address_text.strip().replace('\n', ' '),
                        "price": price_text.strip(),
                        "status": "Active"
                    })
            
            await browser.close()
            return leads

        except Exception as e:
            await browser.close()
            return {"error": f"Scraping failed: {str(e)}"}
