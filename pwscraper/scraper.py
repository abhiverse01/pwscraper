import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
import os

logger = logging.getLogger(__name__)

class PixabayScraper:
    def __init__(self, platforms_config, output_dir):
        self.platforms = platforms_config["platforms"]
        self.output_dir = output_dir
        self.semaphore = asyncio.Semaphore(5)  # Limit concurrent tasks

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> str:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://pixabay.com/',  # Add a referer header to make it more legitimate
                'Upgrade-Insecure-Requests': '1',
                'TE': 'Trailers'
            }
            async with session.get(url, headers=headers) as response:
                if response.status == 429:
                    raise Exception("Rate limit exceeded. Retrying...")
                response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
                return await response.text()
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise

    async def scrape_pixabay(self, session, platform):
        images = []
        try:
            html = await self.fetch_page(session, platform["url"])
            soup = BeautifulSoup(html, "html.parser")

            # Find the images in the mediaSection
            media_section = soup.find_all("div", class_="mediaSection--yiQ4N")
            for item in media_section:
                img_tag = item.find("img")
                if img_tag and img_tag.has_attr('src'):
                    img_url = img_tag['src']
                    alt_text = img_tag.get('alt', 'No alt text')
                    title = img_tag.get('title', 'No title')

                    # Get description, heading, and additional metadata
                    description_section = item.find_next("div", class_="descriptionSection--HSyfs")
                    description = description_section.get_text(strip=True) if description_section else "No description"

                    heading_section = item.find_next("div", class_="headingRow--MzaSD")
                    heading = heading_section.get_text(strip=True) if heading_section else "No heading"

                    images.append({
                        "title": title,
                        "alt_text": alt_text,
                        "description": description,
                        "heading": heading,
                        "url": img_url
                    })
        except Exception as e:
            logger.error(f"Error scraping Pixabay: {e}")
        return images

    async def scrape_platform(self, session, platform):
        parsed_url = urlparse(platform["url"])
        async with self.semaphore:  # Respect concurrency limit
            if "pixabay.com" in parsed_url.netloc:
                return await self.scrape_pixabay(session, platform)
            else:
                return []

    async def run(self):
        tasks = []
        async with aiohttp.ClientSession() as session:
            for platform in self.platforms:
                tasks.append(self.scrape_platform(session, platform))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Task resulted in an exception: {result}")
                else:
                    processed_results.extend(result)
            return processed_results

    @staticmethod
    def deduplicate_data(data):
        seen = set()
        deduplicated = []
        for item in data:
            if item["url"] not in seen:
                seen.add(item["url"])
                deduplicated.append(item)
        return deduplicated

# Example configuration and usage
if __name__ == "__main__":
    platforms_config = {
        "platforms": [
            {"name": "Pixabay", "url": "https://pixabay.com/images/search/people/"}  # Replace with the actual URL you want to scrape
        ]
    }
    output_dir = "output_images"
    
    scraper = PixabayScraper(platforms_config, output_dir)
    results = asyncio.run(scraper.run())

    # Process the results (e.g., save images or print the data)
    for result in results:
        print(result)
