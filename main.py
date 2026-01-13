async def run_scrape_logic(zip_code: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, 
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        
        # 1. This context makes the bot look like a real person
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={
                "Referer": "https://www.google.com/"
            }
        )
        page = await context.new_page()
        
        url = f"https://www.realtor.com/realestateandhomes-search/{zip_code}"
        
        try:
            # 2. Wait for the network to be quiet before looking for houses
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # We wait up to 20 seconds for the houses to appear
            await page.wait_for_selector("[data-testid='property-card']", timeout=20000)
            
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
            return {"error": f"Request timed out or was blocked. Details: {str(e)}"}
