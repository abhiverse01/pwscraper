# scraper.py: Scraper logic (scraper.py) to handle asynchronous scraping and retry mechanisms.
# pwscraper/scraper.py
"""
import json
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

class VideoScraper:
    def __init__(self, platforms_config, output_dir):
        self.platforms = platforms_config["platforms"]
        self.output_dir = output_dir

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def fetch_page(self, session, url):
        try:
            async with session.get(url) as response:
                if response.status in [500, 503]:
                    raise Exception(f"Temporary server error {response.status} for {url}")
                elif response.status != 200:
                    raise Exception(f"Failed to fetch {url}, status code: {response.status}")
                return await response.text()
        except aiohttp.ClientError as e:
            raise Exception(f"HTTP request failed for {url}: {e}")

    async def scrape_platform(self, session, platform):
        videos = []
        try:
            html = await self.fetch_page(session, platform["url"])
            soup = BeautifulSoup(html, "html.parser")

            # Custom scraping logic based on platform structure
            for video_tag in soup.find_all("div", class_="video-item"):
                title = video_tag.find("h3").text
                description = video_tag.find("p", class_="description").text
                video_url = video_tag.find("a", class_="video-link")["href"]
                videos.append({"title": title, "description": description, "url": video_url})
        except Exception as e:
            print(f"Error scraping {platform['name']}: {e}")
        return videos

    async def run(self):
        tasks = []
        async with aiohttp.ClientSession() as session:
            for platform in self.platforms:
                tasks.append(self.scrape_platform(session, platform))
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                processed_results = []
                for result in results:
                    if isinstance(result, Exception):
                        print(f"Task resulted in an exception: {result}")
                    else:
                        processed_results.extend(result)
                return processed_results
            except Exception as e:
                print(f"Critical error during scraping: {e}")
                return []

"""


import json
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential
from urllib.parse import urlparse

class VideoScraper:
    def __init__(self, platforms_config, output_dir):
        self.platforms = platforms_config["platforms"]
        self.output_dir = output_dir

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def fetch_page(self, session, url):
        try:
            async with session.get(url) as response:
                if response.status in [500, 503]:
                    raise Exception(f"Temporary server error {response.status} for {url}")
                elif response.status != 200:
                    raise Exception(f"Failed to fetch {url}, status code: {response.status}")
                return await response.text()
        except aiohttp.ClientError as e:
            raise Exception(f"HTTP request failed for {url}: {e}")

    async def scrape_youtube(self, session, platform):
        videos = []
        try:
            html = await self.fetch_page(session, platform["url"])
            soup = BeautifulSoup(html, "html.parser")

            # YouTube-specific scraping logic
            for video_tag in soup.find_all("a", href=True, class_="yt-simple-endpoint style-scope ytd-video-renderer"):
                title = video_tag.get("title", "No title available")
                video_url = f"https://www.youtube.com{video_tag['href']}"
                videos.append({"title": title, "url": video_url, "description": "N/A (YouTube description needs API)"})
        except Exception as e:
            print(f"Error scraping YouTube: {e}")
        return videos

    async def scrape_generic(self, session, platform):
        videos = []
        try:
            html = await self.fetch_page(session, platform["url"])
            soup = BeautifulSoup(html, "html.parser")

            # Custom scraping logic based on platform structure
            for video_tag in soup.find_all("div", class_="video-item"):
                title = video_tag.find("h3").text
                description = video_tag.find("p", class_="description").text
                video_url = video_tag.find("a", class_="video-link")["href"]
                videos.append({"title": title, "description": description, "url": video_url})
        except Exception as e:
            print(f"Error scraping {platform['name']}: {e}")
        return videos

    async def scrape_platform(self, session, platform):
        parsed_url = urlparse(platform["url"])
        if "youtube.com" in parsed_url.netloc:
            return await self.scrape_youtube(session, platform)
        else:
            return await self.scrape_generic(session, platform)

    async def run(self):
        tasks = []
        async with aiohttp.ClientSession() as session:
            for platform in self.platforms:
                tasks.append(self.scrape_platform(session, platform))
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                processed_results = []
                for result in results:
                    if isinstance(result, Exception):
                        print(f"Task resulted in an exception: {result}")
                    else:
                        processed_results.extend(result)
                return processed_results
            except Exception as e:
                print(f"Critical error during scraping: {e}")
                return []

