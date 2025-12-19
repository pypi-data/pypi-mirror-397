import asyncio
import re
import pandas as pd
from datetime import timedelta
from crawlee.crawlers import PlaywrightCrawler, PlaywrightCrawlingContext
from crawlee import Request, ConcurrencySettings

# Combined city list from both scripts
ALL_CITIES = [
    # Utah County
    "alpine", "american-fork", "eagle-mountain", "highland", "lindon",
    "lehi", "orem", "provo", "saratoga-springs", "spanish-fork",
    # Salt Lake County
    "draper", "holladay", "midvale", "millcreek", "cottonwood-heights",
    "murray", "salt-lake-city", "sandy", "south-jordan", "south-salt-lake",
    "sugarhouse", "west-jordan", "west-valley"
]

# Utility function to safely extract text from a selector
async def safe_text(page, selector):
    try:
        el = await page.query_selector(selector)
        if el:
            txt = await el.text_content()
            return (txt or "").strip()
    except:
        return ""
    return ""

# Validate URL
def is_valid_url(url: str) -> bool:
    if not url:
        return False
    return not any(url.lower().startswith(p) for p in ("javascript:", "mailto:", "tel:", "#"))

# Extract details from a listing page
async def extract_detail(context: PlaywrightCrawlingContext, results):
    page = context.page
    url = context.request.url
    city = context.request.user_data.get("city", "unknown")
    mls = url.split("/listing/")[-1].split("/")[0]
    await asyncio.sleep(1)

    street = await safe_text(page, ".prop___overview h2")
    city_state = await safe_text(page, "#location-data")
    address = f"{street}, {city_state}".strip(" ,")

    price = await safe_text(page, ".prop-details-overview li span")
    beds = (await safe_text(page, ".prop-details-overview li:nth-of-type(2) span")).replace(",", "")
    baths = (await safe_text(page, ".prop-details-overview li:nth-of-type(3) span")).replace(",", "")
    sqft = (await safe_text(page, ".prop-details-overview li:nth-of-type(4) span")).replace(",", "")

    html = await page.content()
    year_built = re.search(r"Year\s*Built[^0-9]*(\d{4})", html, re.I)
    lot_size = re.search(r"Lot[^0-9]*([\d.,]+\s*(?:ac|acre|sq\.? ft))", html, re.I)
    garage = re.search(r"Garage[^0-9]*(\d+)", html, re.I)

    agent = await safe_text(page, ".agent-name, [class*='agent']")
    agent = re.sub(r"\s+", " ", agent).strip() if agent else ""

    data = {
        "mls": mls,
        "price": price,
        "address": address,
        "beds": beds,
        "baths": baths,
        "sqft": sqft,
        "year_built": year_built.group(1) if year_built else "",
        "lot_size": lot_size.group(1) if lot_size else "",
        "garage": garage.group(1) if garage else "",
        "agent": agent,
        "city": city
    }
    results.append(data)

# Extract search results and queue detail pages
async def extract_search_results(context: PlaywrightCrawlingContext, max_listings):
    page = context.page
    url = context.request.url
    match = re.search(r"utahrealestate\.com/([^/]+)-homes", url)
    city = match.group(1) if match else "unknown"

    try:
        await page.wait_for_selector(".property___card", timeout=15000)
    except:
        return []

    cards = await page.query_selector_all(".property___card")
    listings = []
    for card in cards[:max_listings]:
        mls = await card.get_attribute("listno")
        if not mls:
            continue
        detail_url = f"https://www.utahrealestate.com/listing/{mls}"
        listings.append(Request.from_url(detail_url, label="detail", user_data={"city": city}))
    return listings

# Main function for PyPi package
async def get_data_async(max_listings=5, cities=ALL_CITIES, output="pandas"):
    results = []
    start_urls = [f"https://www.utahrealestate.com/{c}-homes" for c in cities]

    crawler = PlaywrightCrawler(
        headless=True,
        browser_type='firefox',
        max_request_retries=2,
        max_requests_per_crawl=2000,
        concurrency_settings=ConcurrencySettings(min_concurrency=1, max_concurrency=5, desired_concurrency=3),
        request_handler_timeout=timedelta(seconds=60),
    )

    @crawler.router.default_handler
    async def router_handler(context: PlaywrightCrawlingContext):
        if "/listing/" in context.request.url or context.request.label == "detail":
            await extract_detail(context, results)
        else:
            new_requests = await extract_search_results(context, max_listings)
            await context.add_requests(new_requests)

    await crawler.run(start_urls)

    # Output handling
    if output == "pandas":
        return pd.DataFrame(results)
    elif output == "csv":
        df = pd.DataFrame(results)
        df.to_csv("utah_housing_data.csv", index=False)
        return "Data saved to utah_housing_data.csv"
    else:
        raise ValueError("Invalid output option. Choose 'pandas' or 'csv'.")

# Wrapper for synchronous call
def get_data(max_listings=5, cities=ALL_CITIES, output="pandas"):
    return asyncio.run(get_data_async(max_listings, cities, output))