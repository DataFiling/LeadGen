import os
from fastapi import FastAPI
from playwright.async_api import async_playwright

app = FastAPI()

@app.get("/")
async def health():
    return {"status": "online", "message": "The Watchers are observing."}

@app.get("/test-browser")
async def test_browser():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://example.com")
            title = await page.title()
            await browser.close()
            return {"success": True, "page_title": title}
    except Exception as e:
        return {"success": False, "error": str(e)}
