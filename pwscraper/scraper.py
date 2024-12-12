# pwscraper/scraper.py

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
import os

logger = logging.getLogger(__name__)

class VideoScraper:
    def __init__(self, platforms_config, output_dir):
        self.platforms = platforms_config["platforms"]
        self.output_dir = output_dir
        self.semaphore = asyncio.Semaphore(5)  # Limit concurrent tasks

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> str:
        try:
            async with session.get(url) as response:
                if response.status == 429:
                    raise Exception("Rate limit exceeded. Retrying...")
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            raise

    async def scrape_youtube(self, session, platform):
        videos = []
        try:
            html = await self.fetch_page(session, platform["url"])
            soup = BeautifulSoup(html, "html.parser")

            for video_tag in soup.find_all("a", href=True, class_="yt-simple-endpoint style-scope ytd-video-renderer"):
                title = video_tag.get("title", "No title available")
                video_url = f"https://www.youtube.com{video_tag['href']}"
                videos.append({"title": title, "url": video_url, "description": "Use YouTube API for descriptions"})
        except Exception as e:
            logger.error(f"Error scraping YouTube: {e}")
        return videos

    async def scrape_generic(self, session, platform):
        videos = []
        try:
            html = await self.fetch_page(session, platform["url"])
            soup = BeautifulSoup(html, "html.parser")

            for video_tag in soup.find_all("div", class_="video-item"):
                title = video_tag.find("h3").text.strip()
                description = video_tag.find("p", class_="description").text.strip()
                video_url = video_tag.find("a", class_="video-link")["href"]
                videos.append({"title": title, "description": description, "url": video_url})
        except Exception as e:
            logger.error(f"Error scraping {platform['name']}: {e}")
        return videos

    async def scrape_platform(self, session, platform):
        parsed_url = urlparse(platform["url"])
        async with self.semaphore:  # Respect concurrency limit
            if "youtube.com" in parsed_url.netloc:
                return await self.scrape_youtube(session, platform)
            else:
                return await self.scrape_generic(session, platform)

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
