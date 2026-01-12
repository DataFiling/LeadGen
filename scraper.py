import asyncio
import os
from playwright.async_api import async_playwright
# Importing 'stealth' directly from the module to avoid "module object is not callable"
from playwright_stealth import stealth

async def run_real_estate_scraper(zip_code: str):
    """
    Launches a headless browser, applies stealth patterns, and 
    extracts the first 10 property leads from Realtor.com.
    """
    async with async_playwright() as p:
        # Launch Chromium with anti-detection flags
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        
        # Create a browser context with a common User-Agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        # Apply stealth to the page to bypass basic bot detection
        await stealth(page)
        
        url = f"https://www.realtor.com/realestateandhomes-search/{zip_code}"
        
        try:
            # Navigate to the URL
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for the property cards to render
            await page.wait_for_selector("[data-testid='property-card']", timeout=10000)
            
            # Locate all property cards
            listings = await page.query_selector_all("[data-testid='property-card']")
            
            leads = []
            for listing in listings[:10]:
                # Extract address and price
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
            # Return error as a list/dict so the API can still respond with details
            return {"error": f"Scraper encountered an issue: {str(e)}"}
