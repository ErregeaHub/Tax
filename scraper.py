import asyncio
import json
import random
import re
import time
import os
import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# Configuration
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

def clean_value(text):
    if not text: return 0.0
    cleaned = re.sub(r'[^\d.]', '', text.replace(',', ''))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

async def get_page_content(browser, url):
    context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
    page = await context.new_page()
    await asyncio.sleep(random.uniform(1, 3))
    try:
        await page.goto(url, wait_until="networkidle", timeout=60000)
        content = await page.content()
        await page.close()
        await context.close()
        return content
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        await page.close()
        await context.close()
        return None

async def scrape_uk(browser):
    print("Scraping UK data...")
    url = "https://www.gov.uk/income-tax-rates"
    content = await get_page_content(browser, url)
    if not content: return None
    soup = BeautifulSoup(content, 'html.parser')
    data = {
        "country": "United Kingdom", "currency": "GBP", "effective_year": "2025/2026",
        "terminology": {"income_tax": "Income Tax", "social_security": "National Insurance", "pay_period": "Monthly Salary", "net_pay": "Take-Home Pay"},
        "income_tax": {"personal_allowance": 12570, "bands": []},
        "social_security": {"name": "National Insurance", "type": "Class 4", "rates": []}
    }
    table = soup.find('table')
    if table:
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 3:
                name = cols[0].get_text(strip=True)
                threshold = cols[1].get_text(strip=True)
                rate_text = cols[2].get_text(strip=True)
                rate = clean_value(rate_text) / 100 if '%' in rate_text else clean_value(rate_text)
                data["income_tax"]["bands"].append({"name": name, "threshold": threshold, "rate": rate})
    data["social_security"]["rates"] = [{"threshold": "£12,570 to £50,270", "rate": 0.06}, {"threshold": "Over £50,270", "rate": 0.02}]
    return data

async def scrape_us(browser):
    print("Scraping USA data...")
    return {
        "country": "United States", "currency": "USD", "effective_year": "2025",
        "terminology": {"income_tax": "Federal Income Tax", "social_security": "FICA (Self-Employment)", "pay_period": "Monthly Paycheck", "net_pay": "Net Pay"},
        "income_tax": {"bands": [
            {"name": "10%", "threshold": "$0 - $11,925", "rate": 0.10}, {"name": "12%", "threshold": "$11,926 - $48,475", "rate": 0.12},
            {"name": "22%", "threshold": "$48,476 - $103,350", "rate": 0.22}, {"name": "24%", "threshold": "$103,351 - $197,300", "rate": 0.24},
            {"name": "32%", "threshold": "$197,301 - $250,525", "rate": 0.32}, {"name": "35%", "threshold": "$250,526 - $626,350", "rate": 0.35},
            {"name": "37%", "threshold": "Over $626,350", "rate": 0.37}
        ]},
        "social_security": {"name": "FICA", "type": "Self-Employment", "rate": 0.153, "base_multiplier": 0.9235}
    }

async def scrape_au(browser):
    print("Scraping Australia data...")
    url = "https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents"
    content = await get_page_content(browser, url)
    data = {
        "country": "Australia", "currency": "AUD", "effective_year": "2024/2025",
        "terminology": {"income_tax": "Income Tax", "social_security": "Medicare Levy", "pay_period": "Fortnightly Pay", "net_pay": "Take-Home"},
        "income_tax": {"bands": []},
        "social_security": {"name": "Medicare Levy", "rate": 0.02}
    }
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    threshold = cols[0].get_text(strip=True)
                    rate_text = cols[1].get_text(strip=True)
                    rate = 0.0
                    if 'NIL' not in rate_text.upper():
                        rate_match = re.search(r'(\d+)c', rate_text)
                        rate = int(rate_match.group(1)) / 100 if rate_match else 0.0
                    data["income_tax"]["bands"].append({"threshold": threshold, "rate": rate})
    if not data["income_tax"]["bands"]:
        data["income_tax"]["bands"] = [
            {"threshold": "$0 \u2013 $18,200", "rate": 0.0}, {"threshold": "$18,201 \u2013 $45,000", "rate": 0.16},
            {"threshold": "$45,001 \u2013 $135,000", "rate": 0.30}, {"threshold": "$135,001 \u2013 $190,000", "rate": 0.37},
            {"threshold": "Over $190,000", "rate": 0.45}
        ]
    return data

async def scrape_ca(browser):
    print("Scraping Canada data...")
    return {
        "country": "Canada", "currency": "CAD", "effective_year": "2025",
        "terminology": {"income_tax": "Federal & Provincial Tax", "social_security": "CPP Contributions", "pay_period": "Monthly Salary", "net_pay": "Net Income"},
        "income_tax": {
            "federal_bands": [
                {"threshold": "$0 - $57,375", "rate": 0.15}, {"threshold": "$57,376 - $114,750", "rate": 0.205},
                {"threshold": "$114,751 - $177,882", "rate": 0.26}, {"threshold": "$177,883 - $253,414", "rate": 0.29},
                {"threshold": "Over $253,414", "rate": 0.33}
            ],
            "ontario_bands": [{"threshold": "$0 - $52,502", "rate": 0.0505}, {"threshold": "$52,503 - $105,004", "rate": 0.0915}, {"threshold": "Over $105,004", "rate": 0.1116}]
        },
        "social_security": {"name": "CPP", "rate": 0.119, "limit": 67800}
    }

def generate_sitemap(base_url="https://globaltax.io"):
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url>\n    <loc>{base_url}/</loc>\n    <lastmod>{now}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>1.0</priority>\n  </url>\n</urlset>'
    os.makedirs('dist', exist_ok=True)
    with open('dist/sitemap.xml', 'w') as f: f.write(sitemap)
    print(f"Sitemap generated at dist/sitemap.xml")

async def main():
    os.makedirs('dist', exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        results = {"metadata": {"last_updated": datetime.datetime.now().strftime("%Y-%m-%d")}, "data": {}}
        funcs = [scrape_uk, scrape_us, scrape_au, scrape_ca]
        for func in funcs:
            try:
                res = await func(browser)
                if res: results["data"][res["country"].lower().replace(' ', '_')] = res
                await asyncio.sleep(2)
            except Exception as e: print(f"Error in {func.__name__}: {e}")
        await browser.close()
        with open('dist/global_tax_config.json', 'w') as f: json.dump(results, f, indent=4)
        print("Scraping complete. Data saved to dist/global_tax_config.json")
        generate_sitemap()

if __name__ == "__main__":
    asyncio.run(main())
