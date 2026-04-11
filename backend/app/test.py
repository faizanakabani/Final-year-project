import asyncio
import re
import json
from crawl4ai import AsyncWebCrawler
from urllib.parse import urljoin, urlparse

async def scrape_page(crawler, url, visited_urls, base_url, base_domain, scraped_data, current_depth, max_depth):
    if url in visited_urls or current_depth > max_depth:
        return
    visited_urls.add(url)

    result = await crawler.arun(url=url)
    markdown_content = result.markdown
    print(f"Scraping: {url}")

    # Remove URLs from the content
    cleaned_content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', markdown_content)

    # Store the cleaned content in the dictionary
    scraped_data[url] = cleaned_content.strip()

    # Extract links from the markdown content
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', markdown_content)
    for link_text, link_url in links:
        absolute_url = urljoin(base_url, link_url)
        parsed_url = urlparse(absolute_url)

        # Skip non-HTTP links and specific file types
        if parsed_url.scheme not in ('http', 'https'):
            continue
        if any(parsed_url.path.endswith(ext) for ext in ['.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp']):
            continue
        if not any(parsed_url.path.endswith(ext) for ext in ['.pdf', '.ppt', '.txt', '.html', '']):
            continue

        # Check if the domain matches the base domain
        if parsed_url.netloc == base_domain:
            await scrape_page(crawler, absolute_url, visited_urls, base_url, base_domain, scraped_data, current_depth + 1, max_depth)

async def main():
    base_url = "https://www.akasaair.com/"
    base_domain = urlparse(base_url).netloc
    visited_urls = set()
    scraped_data = {}
    max_depth = 50

    async with AsyncWebCrawler() as crawler:
        await scrape_page(crawler, base_url, visited_urls, base_url, base_domain, scraped_data, 0, max_depth)

    # Save the scraped data to a JSON file
    with open("scraped_data.json", "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=4)

def parse_dictionary_and_check_links(scraped_data, domain):
    domain_pattern = re.compile(r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    domain_netloc = urlparse(domain).netloc

    for key, value in scraped_data.items():
        # Find all URLs in the value
        urls_in_value = domain_pattern.findall(value)
        for url in urls_in_value:
            parsed_url = urlparse(url)
            if parsed_url.netloc == domain_netloc:
                print(f"Key: {key}")
                break  # No need to check other URLs in this value once one is found

if __name__ == "__main__":
    asyncio.run(main())

    # Load the scraped data from the JSON file
    with open("scraped_data.json", "r", encoding="utf-8") as f:
        scraped_data = json.load(f)

    # Define the domain to check
    domain = "https://www.akasaair.com/"

    # Parse the dictionary and check for links
    parse_dictionary_and_check_links(scraped_data, domain)
