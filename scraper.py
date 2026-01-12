import asyncio
from playwright.async_api import async_playwright
# Using the standard stealth import which is compatible with most versions
from playwright_stealth import stealth

async def run_real_estate_scraper(zip_code: str):
    """
    Main scraping function that launches a browser, navigates to a 
    real estate portal, and extracts property data.
    """
    async with async_playwright() as p:
        # Launching browser with specific arguments to help avoid detection
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # Define a browser context with a modern, common User-Agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        
        page = await context.new_page()
        
        # Apply the stealth settings to the page
        # This replaces the 'stealth_async' function that was causing your crash
        await stealth(page)
        
        # Target URL: realtor.com search for the given ZIP
        url = f"https://www.realtor.com/realestateandhomes-search/{zip_code}"
        
        try:
            # Navigate and wait for the basic content to appear
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Artificial delay to mimic human reading and allow JS to load
            await asyncio.sleep(3)
            
            # Locate property cards using the specific Realtor.com test ID
            listings = await page.query_selector_all("[data-testid='property-card']")
            
            leads = []
            for listing in listings[:10]: # Limit to 10 for performance
                # Specific selectors for Realtor.com's layout
                address_el = await listing.query_selector("[data-label='pc-address']")
                price_el = await listing.query_selector("[data-label='pc-price']")
                
                if address_el and price_el:
                    address_text = await address_el.inner_text()
                    price_text = await price_el.inner_text()
                    
                    leads.append({
                        "address": address_text.strip().replace('\n', ' '),
                        "price": price_text.strip(),
                        "status": "Active Listing"
                    })
            
            await browser.close()
            return leads

        except Exception as e:
            # Ensure the browser closes even if the scrape fails
            await browser.close()
            return {"error": f"Scraping logic failed: {str(e)}"}
