#!/usr/bin/env python3
"""Screenshot ad HTML files to PNG using Playwright."""
import sys, os, asyncio
sys.stdout.reconfigure(encoding="utf-8")

from playwright.async_api import async_playwright

ADS = [
    {"html": "ad_event_1080x1080.html", "png": "ad_event_1080x1080.png", "w": 1080, "h": 1080},
    {"html": "ad_quote_1080x1080.html", "png": "ad_quote_1080x1080.png", "w": 1080, "h": 1080},
    {"html": "ad_story_1080x1920.html", "png": "ad_story_1080x1920.png", "w": 1080, "h": 1920},
]

async def main():
    ads_dir = os.path.dirname(os.path.abspath(__file__))
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for ad in ADS:
            html_path = os.path.join(ads_dir, ad["html"])
            png_path = os.path.join(ads_dir, ad["png"])
            page = await browser.new_page(viewport={"width": ad["w"], "height": ad["h"]})
            await page.goto(f"file:///{html_path.replace(os.sep, '/')}")
            await page.wait_for_timeout(500)
            await page.screenshot(path=png_path, full_page=False)
            await page.close()
            size_kb = os.path.getsize(png_path) / 1024
            print(f"  {ad['png']} ({ad['w']}x{ad['h']}) — {size_kb:.0f} KB")
        await browser.close()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
