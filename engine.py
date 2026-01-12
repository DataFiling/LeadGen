import asyncio
from playwright.async_api import async_playwright

async def run_scrape_logic(zip_code: str):
    async with async_playwright() as p:
        # Launch with essential cloud flags
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        
        # Manually set headers to look like a real browser
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        
        page = await context.new_page()
        url = f"https://www.realtor.com/realestateandhomes-search/{zip_code}"
        
        try:
            # Increase timeout to 90s to avoid 502s on slow loads
            await page.goto(url, wait_until="domcontentloaded", timeout=90000)
            
            # Wait for property cards
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
            return {"error": f"Scrape failed: {str(e)}"}
