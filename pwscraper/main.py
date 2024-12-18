# PWscraper/main.py

import asyncio # `asyncio` is a library to write concurrent code using the async/await syntax.
import asyncio # `asyncio` is a library to write concurrent code using the async/await syntax.
from scraper import VideoScraper # Import the VideoScraper class from the scraper module.
from utils import setup_logging, validate_config # Import the setup_logging and validate_config functions from the utils module.
from storage import save_dataset # Import the save_dataset function from the storage module.
import logging # The `logging` module defines functions and classes which implement a flexible event logging system for applications and libraries.

# main.py
from pwscraper.scraper import PixabayScraper

logger = logging.getLogger(__name__) # Create a logger instance for the main module.

async def main():
    setup_logging()
    logger.info("Starting the scraping process.")

    config_path = "pwscraper/config/platforms.json"
    config = None

    try:
        config = validate_config(config_path)
        logger.info(f"Configuration loaded successfully: {config['platforms']}")
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        return

    scraper = VideoScraper(platforms_config=config, output_dir="datasets/raw")

    try:
        scraped_data = await scraper.run()

        if not scraped_data:
            logger.warning("No data was scraped. Exiting.")
            return

        logger.info(f"Scraped data: {scraped_data}")
        scraped_data = VideoScraper.deduplicate_data(scraped_data)
        save_dataset(scraped_data, output_file="datasets/processed/videos_dataset.csv", format="csv")
    except Exception as e:
        logger.critical(f"An unhandled error occurred during scraping: {e}", exc_info=True)
    finally:
        logger.info("Scraping process finished.")

if __name__ == "__main__":
    asyncio.run(main())
